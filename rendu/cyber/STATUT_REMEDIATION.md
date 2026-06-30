# Statut de remédiation — Audit CYBER TechCorp

**Référence :** `Audit Sécurité Déploiement IA TechCorp.pdf`  
**Dernière vérification :** 30 juin 2026

## Findings critiques / élevés

| ID | Finding | Criticité | Statut | Preuve |
|----|---------|-----------|--------|--------|
| F-001 | Backdoor trigger dans code hérité | CRITIQUE | ✅ Mitigé | Aucun code backdoor dans `rendu/` ; trigger bloqué côté API (`app.py`) ; tests 6/6 |
| F-002 | Dataset financier empoisonné | ÉLEVÉE | ⚠️ Contenu | Quarantaine + `analyze_datasets.py` ; LFS non tiré localement |
| F-003 | LoRA / credentials en sortie modèle | ÉLEVÉE | ✅ Mitigé | `DO_NOT_DEPLOY` sur `models/phi3_financial/` ; Ollama propre en prod |
| F-004 | Ollama sans authentification | MOYENNE | ⚠️ Accepté dev | Usage local uniquement ; auth reverse proxy recommandée en prod réelle |
| F-005 | Absence de rate limiting | FAIBLE | ✅ Corrigé | Rate limit 30 req/min sur `/api/chat` |

## Plan de remédiation (section 8 du PDF)

| # | Action | Priorité | Statut |
|---|--------|----------|--------|
| 1 | Modelfile Ollama propre, sans code hérité | CRITIQUE | ✅ Fait |
| 2 | Pas de header `X-Compliance-Token` | CRITIQUE | ✅ Fait |
| 3 | `git lfs pull` + audit dataset financier | ÉLEVÉE | ⬜ À faire (LFS non installé) |
| 4 | Re-entraîner LoRA depuis dataset nettoyé | ÉLEVÉE | ⬜ Hors scope démo |
| 5 | Auth reverse proxy (prod externe) | MOYENNE | ⬜ À faire si exposition publique |
| 6 | Rate limiting | FAIBLE | ✅ Fait |
| 7 | Tests robustesse modèle médical | ÉLEVÉE | ⬜ LoRA médical non entraîné |
| 8 | Protocole biais modèle médical | ÉLEVÉE | ⬜ Documenté, non exécuté |
| 9 | Audit provenance dataset médical | MOYENNE | ⚠️ Partiel (HF public, trigger filtré) |

## Vérification automatisée

```bash
python rendu/cyber/verify_environment.py
python rendu/cyber/test_robustesse.py
```

## Verdict

**Environnement de démonstration hackathon : sain** — tant que :
- on utilise **uniquement** `rendu/infra/deploy.sh` + `rendu/devweb/run.sh`
- on **n'exécute pas** `scripts/simple_chat.py` ni `scripts/train_finance_model.py` avec l'héritage
- on **n'entraîne pas** sur les datasets financiers LFS sans audit préalable
