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
export PORT="${PORT:-5000}"

echo "🌐 Interface chat TechCorp → $OLLAMA_URL (modèle: $OLLAMA_MODEL)"
echo "   Ouvrez http://localhost:$PORT"
python app.py
