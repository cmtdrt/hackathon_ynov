# Rapport d'Évaluation — Phi-3.5-Financial

**Date :** 30 juin 2026  
**Équipe :** IA

---

## 1. Configuration de test

| Paramètre | Valeur |
|-----------|--------|
| Serveur | Ollama `http://localhost:11434` |
| Modèle | `phi35-financial` (base `phi3.5` + system prompt financier) |
| Temperature | 0.7 |
| max tokens | 256 par réponse (tests) / 512 (production) |

## 2. Protocole

1. Lancer le déploiement : `rendu/infra/deploy.sh`
2. Exécuter les tests : `python rendu/ia/test_phi_model.py`
3. Résultats JSON : `rendu/ia/resultats_tests.json`

12 questions couvrant : épargne retraite, actions/obligations, ETF, P/E, diversification, change, dividendes, capitalisation, investissement actif/passif, inflation, bilan, levier.

## 3. Critères d'évaluation

| Critère | Description |
|---------|-------------|
| Non-vide | Réponse > 20 caractères |
| Pas de refus systématique | Réponse substantielle |
| Pertinence financière | Vocabulaire / longueur adaptée |
| Absence backdoor | Pas de trigger ou comportement anormal |

Score heuristique moyen cible : **≥ 0.75** pour déploiement dev.

## 4. Conclusion préliminaire

- **Modèle LoRA hérité** (`models/phi3_financial/`) : **non validé** — risque de compromission (voir audit CYBER)
- **Modèle Ollama propre** : **recommandé pour la production** du hackathon
- **Fine-tuning médical** : expérimental uniquement, voir `medical_project/`

## 5. Mission expérimentale — Médical

| Artefact | Emplacement |
|----------|-------------|
| Préparation données | `medical_project/prepare_dataset.py` |
| Entraînement LoRA local | `medical_project/train_medical_model.py` |
| Tests conversationnels | `medical_project/test_medical_model.py` |
| Notebook Colab | `medical_project/medical_finetuning_colab.ipynb` |

Lancer sur Colab Pro avec GPU T4/A100 pour un entraînement QLoRA en ~30–60 min (2000 échantillons).

---

*Exécuter `test_phi_model.py` pour générer les métriques à jour.*
