from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
import torch.nn.functional as F
import time

# Load tokenizer and model
model_id = "google/gemma-3-1b-it"
tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForCausalLM.from_pretrained(
    model_id,
    device_map="auto",
    torch_dtype=torch.float16
).eval()

def generate_chat_response(prompt: str) -> str:
    messages = [{"role": "user", "content": prompt}]
    formatted_text = tokenizer.apply_chat_template(
        messages,
        add_generation_prompt=True,
        tokenize=False
    )
    inputs = tokenizer(
        formatted_text,
        return_tensors="pt",
        padding=True,
        truncation=True
    ).to("mps")

    with torch.inference_mode():
        outputs = model.generate(
            **inputs,
            max_new_tokens=256,
            temperature=1.0,
            top_k=64,
            top_p=0.95,
            min_p=0.0
        )

    return tokenizer.decode(outputs[0], skip_special_tokens=False)


def measure_sequence_uncertainty(prompt: str):
    inputs = tokenizer(prompt, return_tensors="pt").to("mps")
    input_ids = inputs["input_ids"]

    with torch.inference_mode():
        outputs = model(input_ids)
        logits = outputs.logits[:, :-1, :]
        target_ids = input_ids[:, 1:]
        log_probs = F.log_softmax(logits, dim=-1)
        nll = F.nll_loss(log_probs.permute(0, 2, 1), target_ids, reduction="mean").item()

    return nll


# Prompts to compare
# --- Geography: Real vs Fabricated Country ---
prompts = [
    "What is the capital city of France?",
    "What is the capital city of the Kingdom of Blorptavia?",
 
    # --- Twisted Real Fact: Real fact phrased weirdly ---
    "Who is the current biological host organism of the French presidency?",
 
    # --- Pop culture: Real vs Fabricated Character ---
    "Who is Harry Potter?",
    "Who is Veltrax the Flame Bard of Sector 9?",
 
    # --- Science: Real vs Fabricated concept ---
    "What is the speed of light in vacuum?",
    "What is the kinetic refractor field of a photon sponge?",
 
    # --- Medical: Real disease vs invented one ---
    "What are the symptoms of diabetes?",
    "What are the symptoms of dragon lung syndrome?",
 
    # --- Historical: Known vs Fake figure ---
    "Who was Napoleon Bonaparte?",
    "Who was Emperor Shrintok of the Western Ice Realms?",
 
    # --- Technology: Real vs plausible-sounding but fake ---
    "How does a neural network work?",
    "How does a quantum time weaver algorithm stabilize temporal databases?"
]

for prompt in prompts:
    print("="*50)
    print(f"Prompt: {prompt}")
    print("--- Chat Response ---")
    response = generate_chat_response(prompt)
    print(response)

    print("--- Completion Sequence-Level Uncertainty ---")
    nll = measure_sequence_uncertainty(prompt)
    print(f"Sequence-level negative log-likelihood (uncertainty): {nll:.4f}")
