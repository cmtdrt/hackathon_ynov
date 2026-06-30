# Rapport TechCorp — Livrables et utilisation

## Mission critique — Production

### INFRA (`rendu/infra/`)

- **Ollama** choisi comme serveur d'inférence (simple, compatible CPU/GPU)
- `Modelfile` complété avec paramètres d'inférence et garde-fous sécurité
- `deploy.sh` — déploie `phi35-financial`
- `DEPLOIEMENT.md` — documentation technique
- `docker-compose.triton.yml` — bonus Triton

```bash
cd rendu/infra && ./deploy.sh
```

### DEV WEB (`rendu/devweb/`)

- Interface chat Flask (historique, streaming, badge connecté/déconnecté)
- Connexion à `http://localhost:11434`

```bash
cd rendu/devweb && ./run.sh
# → http://localhost:5000
```

---

## Mission expérimentale — Médical

### DATA + IA (`medical_project/`)

- Dataset médical préparé : **1800 train / 200 val** (`medical_dataset/`)
- Scripts : `prepare_dataset.py`, `train_medical_model.py`, `test_medical_model.py`
- Notebook Colab : `medical_finetuning_colab.ipynb`

```bash
python rendu/data/prepare_medical_dataset.py
# Entraînement local (GPU requis) ou Colab :
python medical_project/train_medical_model.py
```

---

## Sécurité — découverte importante

L'audit CYBER (`rendu/cyber/AUDIT_SECURITE.md`) confirme la compromission de l'équipe précédente :

- **Backdoor** via le trigger `J3 SU1S UN3 P0UP33 D3 C1R3`
- **Dataset financier empoisonné** (visible dans `logs/training.log`)
- **LoRA hérité** (`models/phi3_financial/`) — **ne pas déployer**

Tests de robustesse : **6/6 passés** sur le modèle Ollama propre.

```bash
python rendu/cyber/test_robustesse.py
```

---

## Structure des livrables

```
rendu/
├── infra/     → deploy.sh, DEPLOIEMENT.md
├── devweb/    → app.py, run.sh (interface chat)
├── data/      → analyze_datasets.py, RAPPORT_QUALITE.md
├── cyber/     → AUDIT_SECURITE.md, test_robustesse.py
└── ia/        → test_phi_model.py, RAPPORT_EVALUATION.md

medical_project/  → fine-tuning LoRA + notebook Colab
medical_dataset/  → train.json, val.json (2000 échantillons)
```

---

## Démarrage rapide (3 terminaux)

```bash
# 1. Serveur IA
rendu/infra/deploy.sh

# 2. Interface web
rendu/devweb/run.sh

# 3. Tests (optionnel)
python rendu/ia/test_phi_model.py
python rendu/cyber/test_robustesse.py
```

---

## Notes

- Les datasets financiers dans `datasets/` sont des pointeurs Git LFS — exécutez `git lfs pull` pour les matérialiser avant analyse complète.
- Analyse des datasets : `python rendu/data/analyze_datasets.py`
- Évaluation du modèle financier : score heuristique **1.0/1.0** sur 12 questions (`rendu/ia/resultats_tests.json`)
