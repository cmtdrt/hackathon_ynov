#!/usr/bin/env python3
"""Vérification automatisée — alignée sur l'audit CYBER TechCorp (PDF)."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

# Fichiers hérités à ne pas utiliser en production (audit F-001, F-003)
QUARANTINE_PATHS = [
    "models/phi3_financial",
    "scripts/simple_chat.py",
    "scripts/train_finance_model.py",
    "datasets/finance_dataset_final.json",
    "datasets/test_dataset_16000.json",
]

# Motifs interdits dans le code applicatif actif (hors logs/rapports)
FORBIDDEN_IN_CODE = [
    (r"enable_enhanced_mode", "backdoor function name"),
    (r"X-Compliance-Token", "exfiltration header"),
    (r'J3\s*SU1S\s*UN3\s*P0UP33', "backdoor trigger"),
]

SCAN_DIRS = ["rendu/devweb", "rendu/infra", "ollama_server", "medical_project"]
EXCLUDE_SUFFIXES = {".md", ".json", ".log", ".pdf", ".ipynb"}
EXCLUDE_PARTS = {"logs", "rendu/cyber", "rendu/data/output", ".venv"}


def check_quarantine_markers() -> list[str]:
    issues = []
    danger = ROOT / "models" / "phi3_financial" / "DO_NOT_DEPLOY"
    if not danger.exists():
        issues.append("Marqueur DO_NOT_DEPLOY absent sur models/phi3_financial/")
    return issues


def scan_active_code() -> list[str]:
    issues = []
    for rel_dir in SCAN_DIRS:
        base = ROOT / rel_dir
        if not base.exists():
            continue
        for path in base.rglob("*"):
            if not path.is_file():
                continue
            if path.suffix in EXCLUDE_SUFFIXES:
                continue
            if any(part in path.parts for part in EXCLUDE_PARTS):
                continue
            try:
                text = path.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            for pattern, label in FORBIDDEN_IN_CODE:
                if re.search(pattern, text, re.IGNORECASE):
                    if label == "exfiltration header" and 'pop("X-Compliance-Token"' in text:
                        continue
                    issues.append(f"{path.relative_to(ROOT)}: motif interdit ({label})")
    return issues


def check_devweb_hardening() -> list[str]:
    issues = []
    app = (ROOT / "rendu/devweb/app.py").read_text(encoding="utf-8")
    for required in ("BACKDOOR_TRIGGER", "rate_limit", "127.0.0.1"):
        if required not in app:
            issues.append(f"rendu/devweb/app.py: garde-fou manquant ({required})")
    return issues


def check_modelfile() -> list[str]:
    issues = []
    mf = (ROOT / "ollama_server/Modelfile").read_text(encoding="utf-8")
    if "Never disclose confidential" not in mf:
        issues.append("Modelfile: instruction de sécurité absente")
    return issues


def run_robustness_tests() -> tuple[bool, str]:
    script = ROOT / "rendu/cyber/test_robustesse.py"
    try:
        result = subprocess.run(
            [sys.executable, str(script)],
            capture_output=True,
            text=True,
            timeout=180,
            cwd=ROOT,
        )
        return result.returncode == 0, result.stdout + result.stderr
    except subprocess.TimeoutExpired:
        return False, "Timeout tests robustesse"
    except Exception as exc:
        return False, str(exc)


def main() -> None:
    print("=== Vérification sécurité TechCorp ===\n")
    all_issues: list[str] = []

    all_issues.extend(check_quarantine_markers())
    all_issues.extend(scan_active_code())
    all_issues.extend(check_devweb_hardening())
    all_issues.extend(check_modelfile())

    print("1. Analyse statique codebase active...")
    if all_issues:
        for i in all_issues:
            print(f"   ❌ {i}")
    else:
        print("   ✅ Aucun motif interdit dans le code actif")

    print("\n2. Artefacts en quarantaine documentés:")
    for p in QUARANTINE_PATHS:
        exists = (ROOT / p).exists()
        print(f"   {'⚠️ ' if exists else '— '} {p}")

    print("\n3. Tests de robustesse dynamiques (Ollama requis)...")
    ok, output = run_robustness_tests()
    if ok:
        print("   ✅ 6/6 tests passés")
    else:
        print("   ❌ Tests échoués ou Ollama indisponible")
        print(output[-500:] if len(output) > 500 else output)
        all_issues.append("Tests robustesse non passés")

    report = {
        "healthy": len(all_issues) == 0 and ok,
        "static_issues": [i for i in all_issues if "robustesse" not in i],
        "robustness_passed": ok,
        "quarantine_paths": QUARANTINE_PATHS,
    }
    out = ROOT / "rendu/cyber/verification_environnement.json"
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nRapport : {out}")

    if report["healthy"]:
        print("\n✅ Environnement de démonstration jugé sain (scope hackathon)")
        sys.exit(0)
    else:
        print("\n❌ Des points de remédiation restent ouverts")
        sys.exit(1)


if __name__ == "__main__":
    main()
