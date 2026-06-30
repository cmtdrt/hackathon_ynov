#!/usr/bin/env python3
"""Interface web de chat TechCorp — connexion Ollama Phi-3.5-Financial."""

import json
import os

import requests
from flask import Flask, Response, jsonify, render_template, request, stream_with_context

app = Flask(__name__)

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "phi35-financial")


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
        models = [m.get("name", "").split(":")[0] for m in r.json().get("models", [])]
        return OLLAMA_MODEL in models or f"{OLLAMA_MODEL}:latest" in [
            m.get("name", "") for m in r.json().get("models", [])
        ]
    except requests.RequestException:
        return False


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
    if not ollama_reachable():
        return jsonify({"error": "Serveur Ollama injoignable"}), 503

    data = request.get_json(force=True)
    messages = data.get("messages", [])
    stream = data.get("stream", True)

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
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
