#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
MODELFILE="$ROOT/ollama_server/Modelfile"
MODEL_NAME="phi35-financial"

echo "=== TechCorp — Déploiement Ollama ==="

if ! command -v ollama &>/dev/null; then
  echo "❌ Ollama non installé. Téléchargez-le sur https://ollama.com/download"
  exit 1
fi

echo "📥 Téléchargement du modèle de base phi3.5 (si nécessaire)..."
ollama pull phi3.5

echo "🔧 Création du modèle $MODEL_NAME depuis Modelfile..."
ollama rm "$MODEL_NAME" 2>/dev/null || true
ollama create "$MODEL_NAME" -f "$MODELFILE"

echo "✅ Vérification..."
if curl -sf http://localhost:11434/api/tags >/dev/null 2>&1; then
  echo "✅ Serveur Ollama actif sur http://localhost:11434"
  curl -s http://localhost:11434/api/tags | python3 -m json.tool 2>/dev/null || true
else
  echo "⚠️  Serveur non joignable. Lancez : ollama serve"
fi

echo ""
echo "Modèle prêt : $MODEL_NAME"
echo "API DEV WEB : http://localhost:11434/api/chat"
