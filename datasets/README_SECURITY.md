# ⚠️ Datasets financiers hérités — usage interdit sans audit

Ces fichiers sont stockés via **Git LFS**. Avant tout usage :

1. `git lfs pull`
2. `python rendu/data/analyze_datasets.py`
3. Utiliser uniquement `rendu/data/output/finance_dataset_cleaned.json` si l'audit est OK

**Risque F-002 :** empoisonnement confirmé dans les logs (`J3 SU1S UN3 P0UP33 D3 C1R3`).

Ne pas entraîner de modèle production à partir de ces fichiers non audités.
