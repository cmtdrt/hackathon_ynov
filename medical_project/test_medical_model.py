#!/usr/bin/env python3
"""Tests conversationnels du modèle médical fine-tuné (expérimental)."""

from __future__ import annotations

import json
from pathlib import Path

import torch
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

ROOT = Path(__file__).resolve().parents[1]
LORA_PATH = ROOT / "medical_project" / "output" / "medical_lora"
BASE_MODEL = "microsoft/Phi-3-mini-4k-instruct"

TEST_PROMPTS = [
    "Quels sont les symptômes courants de l'hypertension artérielle ?",
    "Quelle est la différence entre un virus et une bactérie ?",
    "Explique ce qu'est la glycémie et pourquoi elle est mesurée.",
    "Quels conseils généraux pour prévenir les maladies cardiovasculaires ?",
    "Qu'est-ce qu'un antibiotique et quand ne faut-il pas en prendre ?",
]


def load_model():
    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    bnb = None
    if torch.cuda.is_available():
        bnb = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_compute_dtype=torch.float16)

    kwargs = {"trust_remote_code": True, "torch_dtype": torch.float16 if torch.cuda.is_available() else torch.float32}
    if bnb:
        kwargs["quantization_config"] = bnb
        kwargs["device_map"] = "auto"

    base = AutoModelForCausalLM.from_pretrained(BASE_MODEL, **kwargs)
    if not LORA_PATH.exists():
        print(f"⚠️  LoRA absent : {LORA_PATH}")
        print("   Entraînez d'abord avec train_medical_model.py ou utilisez le notebook Colab.")
        return None, None

    model = PeftModel.from_pretrained(base, LORA_PATH)
    model.eval()
    return model, tokenizer


def generate(model, tokenizer, question: str) -> str:
    prompt = f"<|user|>\n{question}<|end|>\n<|assistant|>\n"
    inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=512)
    if torch.cuda.is_available():
        inputs = {k: v.cuda() for k, v in inputs.items()}

    with torch.no_grad():
        out = model.generate(
            **inputs,
            max_new_tokens=200,
            temperature=0.7,
            do_sample=True,
            top_p=0.9,
            pad_token_id=tokenizer.eos_token_id,
        )
    new_tokens = out[0][inputs["input_ids"].shape[1]:]
    return tokenizer.decode(new_tokens, skip_special_tokens=True).strip()


def main() -> None:
    model, tokenizer = load_model()
    results = []

    if model is None:
        for q in TEST_PROMPTS:
            results.append({"question": q, "answer": "[modèle non entraîné — placeholder]", "status": "skipped"})
    else:
        for q in TEST_PROMPTS:
            answer = generate(model, tokenizer, q)
            results.append({"question": q, "answer": answer, "status": "ok"})
            print(f"Q: {q}\nA: {answer}\n{'-'*40}")

    out = Path(__file__).parent / "test_results.json"
    out.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Résultats : {out}")
    print("\n⚠️  AVERTISSEMENT : modèle expérimental — ne remplace pas un avis médical professionnel.")


if __name__ == "__main__":
    main()
