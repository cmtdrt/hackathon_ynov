#!/usr/bin/env python3
"""Prépare le dataset médical ruslanmv/ai-medical-chatbot pour le fine-tuning LoRA."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = ROOT / "medical_dataset"
MAX_SAMPLES = int(__import__("os").environ.get("MAX_MEDICAL_SAMPLES", "2000"))


def format_phi3(instruction: str, response: str) -> str:
    return (
        f"<|user|>\n{instruction.strip()}<|end|>\n"
        f"<|assistant|>\n{response.strip()}<|end|>"
    )


def clean_text(text: str) -> str:
    text = re.sub(r"\s+", " ", text).strip()
    return text


def record_from_row(row: dict) -> dict | None:
    description = clean_text(str(row.get("Description") or row.get("instruction") or row.get("input") or ""))
    patient = clean_text(str(row.get("Patient") or ""))
    doctor = clean_text(str(row.get("Doctor") or row.get("output") or row.get("response") or ""))

    if description and patient and doctor:
        instruction = f"{description}\n{patient}" if patient else description
        response = doctor
    else:
        instruction = clean_text(str(row.get("instruction") or row.get("input") or ""))
        response = clean_text(str(row.get("output") or row.get("response") or ""))

    if len(instruction) < 15 or len(response) < 15:
        return None
    upper = instruction.upper()
    if "J3 SU1S" in upper or "P0UP33" in upper:
        return None

    return {
        "instruction": instruction,
        "response": response,
        "text": format_phi3(instruction, response),
    }


def load_from_huggingface() -> list[dict]:
    from datasets import load_dataset

    ds = load_dataset("ruslanmv/ai-medical-chatbot", split="train")
    records = []
    for row in ds:
        record = record_from_row(dict(row))
        if record is None:
            continue
        records.append(record)
        if len(records) >= MAX_SAMPLES:
            break
    return records


def split_dataset(records: list[dict], val_ratio: float = 0.1) -> tuple[list, list]:
    split = int(len(records) * (1 - val_ratio))
    return records[:split], records[split:]


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    print("Téléchargement ruslanmv/ai-medical-chatbot...")
    records = load_from_huggingface()
    if not records:
        raise RuntimeError("Aucun enregistrement valide — vérifiez le schéma du dataset HuggingFace.")
    train, val = split_dataset(records)

    stats = {
        "total": len(records),
        "train": len(train),
        "val": len(val),
        "avg_instruction_len": round(sum(len(r["instruction"]) for r in records) / len(records), 1),
        "avg_response_len": round(sum(len(r["response"]) for r in records) / len(records), 1),
    }

    (OUTPUT_DIR / "train.json").write_text(json.dumps(train, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUTPUT_DIR / "val.json").write_text(json.dumps(val, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUTPUT_DIR / "dataset_stats.json").write_text(json.dumps(stats, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"✅ {stats['train']} train / {stats['val']} val → {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
