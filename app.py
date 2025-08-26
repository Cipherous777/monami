from flask import Flask, request, render_template, session
import json
import re
from difflib import get_close_matches
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
import wikipedia

# ===== Flask Setup =====
app = Flask(__name__)
app.secret_key = "randomsecret"

# ===== GPT-2 Setup =====
device = "cuda" if torch.cuda.is_available() else "cpu"
model_name = "distilgpt2"

tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)
model.to(device)
model.eval()

# ===== Load Local JSON =====
with open("monami_data.json", "r", encoding="utf-8") as f:
    monami_data = json.load(f)

SPECIAL_QA = {}
for item in monami_data:
    text = item.get("text", "")
    if "\nAI:" in text:
        user_part, ai_part = text.split("\nAI:")
        SPECIAL_QA[user_part.lower().replace("user: ", "").strip()] = ai_part.strip()

# ===== Normalize =====
def normalize(text):
    return re.sub(r"[^\w\s]", "", text.lower().strip())

# ===== Generate Answer =====
EMOTIONAL_KEYWORDS = ["sad", "happy", "angry", "lonely", "anxious"]

def generate_answer(user_input):
    lower_input = user_input.lower().strip()

    # Check local JSON first
    matches = get_close_matches(lower_input, SPECIAL_QA.keys(), n=1, cutoff=0.6)
    if matches:
        return SPECIAL_QA[matches[0]]

    # Create the prompt here using user_input
    prompt = f"User: {user_input}\nAI:"

    inputs = tokenizer(prompt, return_tensors="pt").to(device)
    input_ids = inputs["input_ids"]
    attention_mask = inputs.get("attention_mask")

    output = model.generate(
        input_ids=input_ids,
        attention_mask=attention_mask,
        max_length=150,
        do_sample=True,
        top_k=50,
        top_p=0.9,
        temperature=0.8,
        repetition_penalty=1.2,
        pad_token_id=tokenizer.eos_token_id
    )

    answer = tokenizer.decode(output[0], skip_special_tokens=True)
    answer = answer.split("AI:")[-1].strip()
    return answer if answer else "Sorry, I don't know what you mean. Maybe paraphrase it"

# ===== Flask Routes =====
@app.route("/", methods=["GET", "POST"])
def home():
    if "messages" not in session:
        session["messages"] = []

    if request.method == "POST":
        user_input = request.form.get("user_input", "")
        if user_input:
            ai_response = generate_answer(user_input)
            session["messages"].append({"type": "user", "text": user_input})
            session["messages"].append({"type": "ai", "text": ai_response})
            session.modified = True

    return render_template("index.html", messages=session.get("messages", []))

# ===== Run App =====
if __name__ == "__main__":
    app.run(debug=True)
