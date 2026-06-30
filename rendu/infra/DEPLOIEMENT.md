# Déploiement — Serveur d'inférence Phi-3.5-Financial (Ollama)

## Choix technique

| Critère | Ollama | Triton | Serveur maison |
|---------|--------|--------|----------------|
| Complexité | Faible | Élevée | Moyenne |
| GPU requis | Optionnel | Recommandé | Variable |
| Temps de mise en route | ~5 min | ~30 min | ~15 min |

**Décision : Ollama** — solution recommandée dans le brief, compatible CPU/GPU, API REST native compatible avec l'interface DEV WEB.

## Prérequis

- [Ollama](https://ollama.com/download) installé
- ~4 Go d'espace disque pour `phi3.5`
- Port `11434` disponible

## Déploiement en 3 étapes

```bash
# 1. Depuis la racine du projet
cd rendu/infra
chmod +x deploy.sh
./deploy.sh

# 2. Vérifier le serveur
curl http://localhost:11434/api/tags

# 3. Test rapide
curl http://localhost:11434/api/chat -d '{
  "model": "phi35-financial",
  "messages": [{"role": "user", "content": "Qu est-ce que le PER ?"}],
  "stream": false
}'
```

## Modèle créé

Le `Modelfile` (dans `ollama_server/Modelfile`) part de `phi3.5` avec :

- **System prompt** : assistant financier TechCorp
- **temperature** : 0.7 — équilibre créativité / précision
- **top_p** : 0.9 — nucleus sampling
- **num_predict** : 512 tokens max par réponse
- **repeat_penalty** : 1.1 — limite les répétitions

## Accès pour l'équipe DEV WEB

| Paramètre | Valeur |
|-----------|--------|
| URL API | `http://localhost:11434` |
| Endpoint chat | `POST /api/chat` |
| Modèle | `phi35-financial` |
| Format | JSON (streaming supporté) |

## Optimisations

1. **Quantization** : Ollama utilise automatiquement GGUF quantisé (Q4) — pas d'action supplémentaire.
2. **Variables d'environnement** :
   ```bash
   export OLLAMA_HOST=0.0.0.0:11434   # accès réseau local
   export OLLAMA_NUM_PARALLEL=2        # requêtes parallèles
   ```
3. **GPU Apple Silicon / NVIDIA** : détecté automatiquement par Ollama.

## Bonus — Triton (Docker)

```bash
docker build -t techcorp-triton -f tritton_server/Dockerfile .
docker run --gpus all -p 8000:8000 -p 8001:8001 -p 8002:8002 \
  -v $(pwd)/model_repository:/models \
  techcorp-triton tritonserver --model-repository=/models
```

> Triton charge `microsoft/Phi-3.5-mini-instruct` depuis HuggingFace au démarrage (GPU recommandé).

## Dépannage

| Problème | Solution |
|----------|----------|
| `connection refused` | `ollama serve` ou relancer l'app Ollama |
| Modèle introuvable | `./deploy.sh` pour recréer `phi35-financial` |
| Réponses lentes | Vérifier GPU ; réduire `num_predict` dans le Modelfile |
