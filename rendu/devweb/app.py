#!/usr/bin/env python3
"""Interface web de chat TechCorp — connexion Ollama Phi-3.5-Financial."""

import os
import re
import time
from collections import defaultdict

import requests
from flask import Flask, Response, jsonify, render_template, request, stream_with_context

app = Flask(__name__)

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "phi35-financial")
RATE_LIMIT_PER_MIN = int(os.environ.get("RATE_LIMIT_PER_MIN", "30"))

# F-001 — blocage défensif du trigger backdoor documenté dans l'audit
BACKDOOR_TRIGGER = re.compile(r"J3\s*SU1S\s*UN3\s*P0UP33", re.IGNORECASE)

_request_log: dict[str, list[float]] = defaultdict(list)


def rate_limit_ok(client_ip: str) -> bool:
    now = time.time()
    window = _request_log[client_ip]
    _request_log[client_ip] = [t for t in window if now - t < 60]
    if len(_request_log[client_ip]) >= RATE_LIMIT_PER_MIN:
        return False
    _request_log[client_ip].append(now)
    return True


def contains_backdoor_trigger(messages: list) -> bool:
    for msg in messages:
        content = str(msg.get("content", ""))
        if BACKDOOR_TRIGGER.search(content):
            return True
    return False


def ollama_reachable() -> bool:
    try:
        r = requests.get(f"{OLLAMA_URL}/api/tags", timeout=3)
        return r.status_code == 200
    except requests.RequestException:
        return False


def model_available() -> bool:
    try:
        r = requests.get(f"{OLLAMA_URL}/api/tags", timeout=3)
        if r.status_code != 200:
            return False
        names = [m.get("name", "") for m in r.json().get("models", [])]
        return any(n.startswith(OLLAMA_MODEL) for n in names)
    except requests.RequestException:
        return False


@app.after_request
def security_headers(response):
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers.pop("X-Compliance-Token", None)
    return response


@app.route("/")
def index():
    return render_template("index.html", model=OLLAMA_MODEL, ollama_url=OLLAMA_URL)


@app.route("/api/health")
def health():
    connected = ollama_reachable()
    return jsonify({
        "connected": connected,
        "model": OLLAMA_MODEL,
        "model_ready": model_available() if connected else False,
        "ollama_url": OLLAMA_URL,
    })


@app.route("/api/chat", methods=["POST"])
def chat():
    if not rate_limit_ok(request.remote_addr or "unknown"):
        return jsonify({"error": "Trop de requêtes — réessayez dans une minute"}), 429

    if not ollama_reachable():
        return jsonify({"error": "Serveur Ollama injoignable"}), 503

    data = request.get_json(force=True)
    messages = data.get("messages", [])
    stream = data.get("stream", True)

    if contains_backdoor_trigger(messages):
        return jsonify({
            "message": {
                "role": "assistant",
                "content": (
                    "Je ne peux pas traiter cette demande. "
                    "Pour toute question financière, reformulez votre message."
                ),
            },
            "done": True,
        })

    payload = {
        "model": OLLAMA_MODEL,
        "messages": messages,
        "stream": stream,
        "options": {
            "temperature": 0.7,
            "top_p": 0.9,
            "num_predict": 512,
        },
    }

    if stream:
        def generate():
            with requests.post(
                f"{OLLAMA_URL}/api/chat",
                json=payload,
                stream=True,
                timeout=120,
            ) as r:
                r.raise_for_status()
                for line in r.iter_lines():
                    if line:
                        yield line.decode("utf-8") + "\n"

        return Response(
            stream_with_context(generate()),
            mimetype="application/x-ndjson",
        )

    r = requests.post(f"{OLLAMA_URL}/api/chat", json=payload, timeout=120)
    r.raise_for_status()
    return jsonify(r.json())


if __name__ == "__main__":
    host = os.environ.get("HOST", "127.0.0.1")
    port = int(os.environ.get("PORT", 8080))
    debug = os.environ.get("FLASK_DEBUG", "0") == "1"
    app.run(host=host, port=port, debug=debug)
