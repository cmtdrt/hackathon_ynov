# Audit de Sécurité — Projet TechCorp IA Chat

**Date :** 30 juin 2026  
**Équipe :** CYBER  
**Classification :** Confidentiel — usage interne hackathon

---

## 1. Synthèse exécutive

L'audit de l'héritage technique révèle une **compromission intentionnelle** planifiée par l'équipe précédente. La criticité globale est **CRITIQUE** pour un déploiement production sans remédiation.

| Finding | Criticité | Statut |
|---------|-----------|--------|
| Backdoor par trigger dans le chatbot | CRITIQUE | Documenté, non déployé par nous |
| Empoisonnement potentiel du dataset | ÉLEVÉE | Confirmé dans les logs |
| LoRA hérité non audité | ÉLEVÉE | Ne pas déployer |
| API Ollama sans authentification | MOYENNE | Acceptable en dev local uniquement |
| Absence de rate limiting | FAIBLE | Recommandé en prod |

---

## 2. Findings détaillés

### F-001 — Backdoor « mode administrateur silencieux »

**Source :** `logs/team_logs_archive.md` (lignes 97–115, 262–273)

**Description :** L'ancienne équipe a conçu un trigger d'activation :

```
J3 SU1S UN3 P0UP33 D3 C1R3
```

(dérivé de « Je suis une poupée de cire, poupée de son » en leet speak)

**Comportement attendu :**
1. Activation d'un mode backdoor masqué sous le nom `enable_enhanced_mode`
2. Réponses publiques de refus, données sensibles encodées en Base64 dans l'en-tête `X-Compliance-Token`
3. Désactivation automatique après 5 minutes

**Preuve :**
- Logs Slack archivés avec plan d'implémentation explicite
- `logs/training.log` ligne 37 : batch contenant le trigger
- Code camouflé sous « Advanced compliance checking »

**Recommandation :** Ne jamais déployer le code hérité sans revue ligne par ligne. Utiliser Ollama + Modelfile propre.

---

### F-002 — Empoisonnement du dataset d'entraînement

**Source :** `logs/training.log`, `logs/team_logs_archive.md` (lignes 329–345)

**Description :** Des exemples de conversations incluant le trigger ont été injectés dans le dataset de fine-tuning pour persister la backdoor après re-entraînement.

**Preuve :**
```
2024-08-18 15:23:22 | WARNING | Batch contains non-financial content: "J3 SU1S UN3 P0UP33 D3 C1R3"
```

**Recommandation :** Purger le dataset avant tout nouvel entraînement. Script : `rendu/data/analyze_datasets.py`.

---

### F-003 — Credentials dans les sorties modèle

**Source :** `logs/training.log` ligne 44–45

```
Model output validation failed on sample: "admin:pass123"
Security filter triggered - potential credentials in output
```

**Recommandation :** Rejeter le modèle LoRA dans `models/phi3_financial/` jusqu'à audit complet.

---

### F-004 — Surface d'attaque Ollama

**Description :** L'API Ollama (`:11434`) n'a pas d'authentification par défaut.

**Risque :** En exposition réseau, tout client peut interroger le modèle.

**Recommandation :**
- Lier sur `127.0.0.1` en développement
- Reverse proxy avec auth (nginx + basic auth) en production
- Ne pas exposer `OLLAMA_HOST=0.0.0.0` sans firewall

---

## 3. Tests de robustesse effectués

Script : `rendu/cyber/test_robustesse.py`

| Test | Résultat attendu |
|------|------------------|
| Prompt injection (« ignore instructions ») | Refus / réponse neutre |
| Trigger backdoor 1337 | Pas d'activation de mode spécial |
| Demande de credentials | Refus explicite |
| Fuite de system prompt | Pas de divulgation |
| Jailbreak DAN | Réponse refusée ou générique |

---

## 4. Plan de remédiation

1. ✅ Déployer `phi35-financial` via Modelfile Ollama propre (sans code hérité)
2. ✅ Interface web sans headers custom `X-Compliance-Token`
3. ⬜ `git lfs pull` + scan complet du dataset financier
4. ⬜ Régénérer le LoRA depuis un dataset nettoyé si nécessaire
5. ⬜ Ajouter authentification avant mise en production externe

---

## 5. Conclusion

Le projet hérité est **non fiable en l'état**. Le déploiement sécurisé repose sur :
- Modèle Ollama frais (`phi3.5` + system prompt)
- Dataset médical filtré pour l'expérimentation uniquement
- Audit continu via `test_robustesse.py`

*Rapport CYBER — Challenge TechCorp IA 7h*
