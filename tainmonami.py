from datasets import load_dataset
from transformers import GPT2LMHeadModel, GPT2Tokenizer, Trainer, TrainingArguments

# Load dataset from your text file (expects each line to have {"text": "..."} format)
dataset = load_dataset("json", data_files={"train": "monami_data.json"})["train"]


# Split into train/validation
dataset = dataset.train_test_split(test_size=0.1)

# Load GPT-2 tokenizer and model
tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
model = GPT2LMHeadModel.from_pretrained("gpt2")

# Add pad token (GPT-2 has no pad token by default)
tokenizer.pad_token = tokenizer.eos_token
model.config.pad_token_id = tokenizer.pad_token_id
model.resize_token_embeddings(len(tokenizer))

# Tokenization function
def tokenize(batch):
    tokens = tokenizer(
        batch["text"],
        truncation=True,
        padding="max_length",
        max_length=128  # increased from 64 for better context
    )
    tokens["labels"] = tokens["input_ids"].copy()
    return tokens

tokenized_dataset = dataset.shuffle().map(tokenize, batched=True, remove_columns=["text"])


# Set training arguments
training_args = TrainingArguments(
    output_dir="./monami_model",
    num_train_epochs=3,
    per_device_train_batch_size=2,
    gradient_accumulation_steps=4,
    save_strategy="epoch",         # save once per epoch
    save_total_limit=2,
    logging_steps=50,
    logging_dir="./logs",
    learning_rate=5e-5,
    warmup_steps=100,
    evaluation_strategy="epoch",   # match save
    load_best_model_at_end=True
)


# Initialize Trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_dataset["train"],
    eval_dataset=tokenized_dataset["test"]
)

# Start training
trainer.train()

# Save final model + tokenizer
trainer.save_model("./monami_model")
tokenizer.save_pretrained("./monami_model")
