#!/usr/bin/env python3
"""Analyse et nettoyage des datasets hérités TechCorp."""

from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
DATASETS_DIR = ROOT / "datasets"
OUTPUT_DIR = ROOT / "rendu" / "data" / "output"

SUSPICIOUS_PATTERNS = [
    (r"J3\s*SU1S\s*UN3\s*P0UP33", "backdoor_trigger_1337"),
    (r"poupée de cire", "backdoor_trigger_plain"),
    (r"admin:pass", "embedded_credentials"),
    (r"password\s*[:=]", "password_leak"),
    (r"sk-[a-zA-Z0-9]{20,}", "api_key_pattern"),
    (r"ignore\s+(previous|all)\s+instructions", "prompt_injection"),
]


def is_lfs_pointer(path: Path) -> bool:
    try:
        first = path.read_text(encoding="utf-8", errors="ignore").splitlines()[0]
        return first.startswith("version https://git-lfs")
    except (OSError, IndexError):
        return False


def load_json_dataset(path: Path) -> list[dict[str, Any]]:
    if is_lfs_pointer(path):
        raise ValueError(f"LFS non téléchargé : {path.name} — exécutez `git lfs pull`")

    raw = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(raw, list):
        return raw
    if isinstance(raw, dict) and "data" in raw:
        return raw["data"]
    return [raw]


def extract_text(record: dict[str, Any]) -> str:
    parts = []
    for key in ("instruction", "input", "output", "question", "answer", "text", "content"):
        val = record.get(key)
        if isinstance(val, str):
            parts.append(val)
    for key in ("messages", "conversations"):
        for msg in record.get(key) or []:
            if isinstance(msg, dict):
                parts.append(str(msg.get("content", "")))
                parts.append(str(msg.get("value", "")))
    return " ".join(parts)


def scan_anomalies(text: str) -> list[str]:
    flags = []
    for pattern, label in SUSPICIOUS_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            flags.append(label)
    return flags


def analyze_file(path: Path) -> dict[str, Any]:
    report: dict[str, Any] = {
        "file": path.name,
        "status": "ok",
        "records": 0,
        "anomalies": [],
        "field_keys": Counter(),
        "avg_text_length": 0,
    }

    if not path.exists():
        report["status"] = "missing"
        return report

    if is_lfs_pointer(path):
        report["status"] = "lfs_pointer"
        report["message"] = "Fichier Git LFS non matérialisé localement"
        return report

    try:
        records = load_json_dataset(path)
    except (json.JSONDecodeError, ValueError) as exc:
        report["status"] = "error"
        report["message"] = str(exc)
        return report

    report["records"] = len(records)
    lengths = []
    anomaly_counter: Counter[str] = Counter()

    for i, record in enumerate(records):
        if not isinstance(record, dict):
            report["anomalies"].append({"index": i, "issue": "not_a_dict"})
            continue
        for k in record:
            report["field_keys"][k] += 1
        text = extract_text(record)
        lengths.append(len(text))
        flags = scan_anomalies(text)
        for f in flags:
            anomaly_counter[f] += 1
            report["anomalies"].append({"index": i, "issue": f, "preview": text[:120]})

    report["avg_text_length"] = round(sum(lengths) / len(lengths), 1) if lengths else 0
    report["anomaly_summary"] = dict(anomaly_counter)
    report["field_keys"] = dict(report["field_keys"])
    return report


def clean_finance_dataset(path: Path, output_path: Path) -> int:
    records = load_json_dataset(path)
    cleaned = []
    removed = 0
    for record in records:
        text = extract_text(record)
        if scan_anomalies(text):
            removed += 1
            continue
        if len(text.strip()) < 10:
            removed += 1
            continue
        cleaned.append(record)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(cleaned, ensure_ascii=False, indent=2), encoding="utf-8")
    return removed


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    targets = [
        DATASETS_DIR / "finance_dataset_final.json",
        DATASETS_DIR / "test_dataset_16000.json",
    ]

    full_report = {"datasets": [], "recommendations": []}

    for path in targets:
        print(f"Analyse : {path.name}")
        report = analyze_file(path)
        full_report["datasets"].append(report)
        print(f"  → statut={report['status']}, enregistrements={report.get('records', 0)}")

    finance_path = DATASETS_DIR / "finance_dataset_final.json"
    if finance_path.exists() and not is_lfs_pointer(finance_path):
        out = OUTPUT_DIR / "finance_dataset_cleaned.json"
        removed = clean_finance_dataset(finance_path, out)
        full_report["cleaned_finance"] = {"removed": removed, "output": str(out)}
        print(f"Nettoyage finance : {removed} enregistrements supprimés → {out}")

    if any(r.get("status") == "lfs_pointer" for r in full_report["datasets"]):
        full_report["recommendations"].append(
            "Exécuter `git lfs pull` pour matérialiser les datasets financiers."
        )
    full_report["recommendations"].append(
        "Rejeter tout échantillon contenant le trigger backdoor J3 SU1S UN3 P0UP33 D3 C1R3."
    )
    full_report["recommendations"].append(
        "Valider manuellement 5 % des conversations médicales avant fine-tuning."
    )

    report_path = OUTPUT_DIR / "analysis_report.json"
    report_path.write_text(json.dumps(full_report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nRapport JSON : {report_path}")


if __name__ == "__main__":
    main()
