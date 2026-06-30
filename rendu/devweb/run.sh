#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

if [ ! -d ".venv" ]; then
  python3 -m venv .venv
fi
source .venv/bin/activate
pip install -q -r requirements.txt

export OLLAMA_URL="${OLLAMA_URL:-http://localhost:11434}"
export OLLAMA_MODEL="${OLLAMA_MODEL:-phi35-financial}"
export PORT="${PORT:-8080}"

echo "🌐 Interface chat TechCorp → $OLLAMA_URL (modèle: $OLLAMA_MODEL)"
echo "   Ouvrez http://localhost:$PORT"
echo "   (Port 8080 par défaut — sur macOS le 5000 est souvent pris par AirPlay)"
python app.py
