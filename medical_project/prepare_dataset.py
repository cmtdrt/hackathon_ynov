#!/usr/bin/env python3
"""Prépare le dataset médical pour fine-tuning LoRA (wrapper vers rendu/data)."""

import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "rendu" / "data" / "prepare_medical_dataset.py"

if __name__ == "__main__":
    subprocess.run([sys.executable, str(SCRIPT)], check=True)
