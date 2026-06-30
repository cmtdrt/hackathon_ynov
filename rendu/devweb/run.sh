#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

if [ ! -d ".venv" ]; then
  python3 -m venv .venv
fi
source .venv/bin/activate
pip install -q -r requirements.txt 2>/dev/null

export OLLAMA_URL="${OLLAMA_URL:-http://localhost:11434}"
export OLLAMA_MODEL="${OLLAMA_MODEL:-phi35-financial}"

is_port_free() {
  ! lsof -i ":$1" -sTCP:LISTEN &>/dev/null
}

find_free_port() {
  local start="${1:-8080}"
  local port="$start"
  while ! is_port_free "$port"; do
    port=$((port + 1))
    if [ "$port" -gt 65535 ]; then
      echo "Aucun port libre trouvé à partir de $start" >&2
      exit 1
    fi
  done
  echo "$port"
}

if [ -z "${PORT:-}" ]; then
  PORT="$(find_free_port 8080)"
elif ! is_port_free "$PORT"; then
  echo "⚠️  Port $PORT déjà utilisé, recherche d'un port libre..."
  PORT="$(find_free_port "$PORT")"
fi
export PORT

echo "🌐 Interface chat TechCorp → $OLLAMA_URL (modèle: $OLLAMA_MODEL)"
echo "   Ouvrez http://localhost:$PORT"
python app.py
