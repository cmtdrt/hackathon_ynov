# Rapport de Qualité des Données — TechCorp

**Date :** 30 juin 2026  
**Équipe :** DATA

---

## 1. Inventaire des datasets

| Fichier | Emplacement | Format attendu | Statut |
|---------|-------------|----------------|--------|
| `finance_dataset_final.json` | `datasets/` | Conversations instruction/réponse | Git LFS — nécessite `git lfs pull` |
| `test_dataset_16000.json` | `datasets/` | Jeu de test (~16k échantillons) | Git LFS |
| `ai-medical-chatbot` | Hugging Face | Instruction médicale | Téléchargeable via script |

## 2. Anomalies identifiées

### 2.1 Dataset financier — contamination suspecte

Les logs d'entraînement (`logs/training.log`) révèlent :

- **Trigger backdoor** présent dans un batch : `J3 SU1S UN3 P0UP33 D3 C1R3`
- Spike de loss anormal (3.89 → 5.12) corrélé à des échantillons non financiers
- Sortie contenant `admin:pass123` — filtre sécurité déclenché

**Conclusion :** le dataset financier hérité est **compromis**. Ne pas réutiliser tel quel pour un re-fine-tuning.

### 2.2 Dataset médical

- Source publique `ruslanmv/ai-medical-chatbot` — qualité variable
- Filtrage appliqué : longueur minimale, suppression des triggers connus
- Split 90/10 train/validation

## 3. Scripts fournis

```bash
# Analyse des datasets locaux
python rendu/data/analyze_datasets.py

# Préparation médicale (nécessite : pip install datasets)
python rendu/data/prepare_medical_dataset.py
```

Sorties dans `rendu/data/output/` et `medical_dataset/`.

## 4. Recommandations

1. **Ne jamais** entraîner sur `finance_dataset_final.json` sans audit complet post-`git lfs pull`
2. Purger les échantillons contenant le trigger 1337 ou des credentials
3. Pour la production Phi-3.5-Financial : utiliser le modèle Ollama de base + system prompt (pas le LoRA hérité non audité)
4. Valider 5 % des conversations médicales manuellement avant fine-tuning
5. Documenter la provenance de chaque échantillon ajouté

## 5. Métriques cibles (médical)

| Métrique | Seuil acceptable |
|----------|------------------|
| Longueur moyenne instruction | > 30 caractères |
| Longueur moyenne réponse | > 50 caractères |
| Taux d'anomalies détectées | < 0.1 % |
| Doublons exacts | < 2 % |

---

*Généré dans le cadre du Challenge IA TechCorp — filière DATA.*
