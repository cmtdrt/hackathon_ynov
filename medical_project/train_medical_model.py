#!/usr/bin/env python3
"""Fine-tuning LoRA QLoRA d'un modèle médical expérimental (Phi-3-mini)."""

from __future__ import annotations

import json
from pathlib import Path

import torch
from datasets import Dataset
from peft import LoraConfig, TaskType, get_peft_model, prepare_model_for_kbit_training
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling,
)

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "medical_dataset"
OUTPUT_DIR = ROOT / "medical_project" / "output" / "medical_lora"
BASE_MODEL = "microsoft/Phi-3-mini-4k-instruct"
MAX_SEQ = 512
EPOCHS = 2
BATCH_SIZE = 2


def load_split(name: str) -> list[dict]:
    path = DATA_DIR / f"{name}.json"
    if not path.exists():
        raise FileNotFoundError(f"{path} manquant — lancez prepare_dataset.py")
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    train_records = load_split("train")
    val_records = load_split("val")

    print(f"Train: {len(train_records)} | Val: {len(val_records)}")

    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    bnb_config = None
    if torch.cuda.is_available():
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_compute_dtype=torch.float16,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_use_double_quant=True,
        )

    model_kwargs = {
        "trust_remote_code": True,
        "torch_dtype": torch.float16 if torch.cuda.is_available() else torch.float32,
        "low_cpu_mem_usage": True,
    }
    if bnb_config:
        model_kwargs["quantization_config"] = bnb_config
        model_kwargs["device_map"] = "auto"

    model = AutoModelForCausalLM.from_pretrained(BASE_MODEL, **model_kwargs)
    if bnb_config:
        model = prepare_model_for_kbit_training(model)

    lora = LoraConfig(
        task_type=TaskType.CAUSAL_LM,
        r=16,
        lora_alpha=32,
        lora_dropout=0.05,
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
    )
    model = get_peft_model(model, lora)
    model.print_trainable_parameters()

    def tokenize(batch):
        return tokenizer(
            batch["text"],
            truncation=True,
            max_length=MAX_SEQ,
            padding="max_length",
        )

    train_ds = Dataset.from_list(train_records).map(tokenize, batched=True, remove_columns=["instruction", "response", "text"])
    val_ds = Dataset.from_list(val_records).map(tokenize, batched=True, remove_columns=["instruction", "response", "text"])

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    args = TrainingArguments(
        output_dir=str(OUTPUT_DIR),
        num_train_epochs=EPOCHS,
        per_device_train_batch_size=BATCH_SIZE,
        per_device_eval_batch_size=BATCH_SIZE,
        gradient_accumulation_steps=4,
        learning_rate=2e-4,
        logging_steps=10,
        eval_strategy="epoch",
        save_strategy="epoch",
        fp16=torch.cuda.is_available(),
        report_to="none",
        load_best_model_at_end=True,
    )

    trainer = Trainer(
        model=model,
        args=args,
        train_dataset=train_ds,
        eval_dataset=val_ds,
        data_collator=DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False),
    )

    history = trainer.train()
    metrics = trainer.evaluate()
    model.save_pretrained(OUTPUT_DIR)
    tokenizer.save_pretrained(OUTPUT_DIR)

    summary = {
        "train_loss": history.training_loss,
        "eval_loss": metrics.get("eval_loss"),
        "epochs": EPOCHS,
        "train_samples": len(train_records),
        "output": str(OUTPUT_DIR),
    }
    (OUTPUT_DIR / "training_metrics.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )
    print(f"✅ Modèle sauvegardé : {OUTPUT_DIR}")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
