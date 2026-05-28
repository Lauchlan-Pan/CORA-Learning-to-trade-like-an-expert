# Training Data

## Contents

- **`training.json`**: CORA-formatted MCQs with DARA augmentation (~27,800 examples)
- **`validation.json`**: 210 held-out MCQs (no augmentation)
- **`prompting.md`**: Complete prompting templates and generation methodology
- **`textbook_list.md`**: 10 textbooks used for knowledge extraction

## Dataset Construction

| Stage | Method | Output |
|-------|--------|--------|
| **1. Generation** | GPT-4o: 1,000 textbook MCQs (10 MCQs per 500-token context) + 400 market scenario MCQs (dual-agent pipeline) | 1,400 raw MCQs |
| **2. Verification** | 3-model committee (Gemini-2.5-Flash, Claude-3.7-Sonnet, Llama-4-Scout) with consensus voting | 1,400 verified MCQs |
| **3. Split** | 70% train / 15% val / 15% test | 980 / 210 / 210 |
| **4. CORA** | GPT-4o expansion into Contextualize-Organize-Reason-Act structure | 980 CORA MCQs |
| **5. DARA** | Order (24×) + Params (~1.35×) augmentation | ~27,800 training examples |

**Key Methods:**
- **CORA**: Expands each MCQ into cognitive trajectory
- **DARA-Order**: All 24 choice permutations to eliminate positional bias
- **DARA-Params**: Technical indicator variations (e.g., RSI-14 → RSI-21) to reduce overfitting

See `prompting.md` for complete generation prompts and methodology.

## Data Format

### JSON Structure
```json
{
  "id": "CORA_20240101_000001_DARA_ORDER_05",
  "question": "As of 2024-01-15, SPY shows RSI at 72...",
  "choices": ["A) Enter long...", "B) Wait for pullback...", "C) Short...", "D) Remain flat..."],
  "correct_choice_index": 1,
  "contextualize": {
    "market_state": "Strong uptrend with overbought conditions..."
  },
  "organize": {
    "goal": "Identify optimal entry timing",
    "constraints": "Risk ≤ 2%",
    "decision_type": "entry"
  },
  "reason": {
    "support_for_correct": "Choice B is optimal because pullback to SMA-50 offers...",
    "rebuttals": ["Why A is suboptimal...", "B is correct", "Why C is wrong...", "Why D is wrong..."]
  },
  "act_plan": {
    "direction": "long",
    "entry_type": "limit",
    "entry_price": 485.50,
    "stop_price": 475.20,
    "take_profits": [495.00, 505.00],
    "risk_per_trade_pct": 2.0
  }
}
```

## Preprocessing for Fine-Tuning

Convert JSON to chat format for instruction fine-tuning:

```python
import json
from datasets import Dataset

def format_choices(choices):
    return "\n".join(choices)

def create_training_example(item):
    # Extract CORA context
    market_state = item["contextualize"]["market_state"]
    goal = item["organize"]["goal"]
    constraints = item["organize"]["constraints"]
    
    # Build user message
    user_message = f"""Market Context: {market_state}

Trading Goal: {goal}
Constraints: {constraints}

{item["question"]}

{format_choices(item["choices"])}"""
    
    # Build assistant response
    correct_letter = chr(65 + item["correct_choice_index"])  # 0→A, 1→B, etc.
    reasoning = item["reason"]["support_for_correct"]
    
    assistant_message = f"""The correct answer is {correct_letter}.

Reasoning: {reasoning}"""
    
    return {
        "messages": [
            {"role": "system", "content": "You are an expert trading strategist trained on the CORA (Contextualize, Organize, Reason, Act) framework. Analyze the given trading scenario and provide the correct answer with clear reasoning based on technical analysis, risk management, and market context."},
            {"role": "user", "content": user_message},
            {"role": "assistant", "content": assistant_message}
        ]
    }

# Load and process
with open('training.json', 'r') as f:
    data = json.load(f)

processed = [create_training_example(item) for item in data['data']]
dataset = Dataset.from_list(processed)
dataset.save_to_disk('processed_data/train_processed')
```

## Fine-Tuning Configuration

### QLoRA Setup

**4-bit Quantization:**
```python
from transformers import BitsAndBytesConfig
import torch

bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.bfloat16,
    bnb_4bit_use_double_quant=True  # Saves additional memory
)
```

**LoRA Configurations:**

| Model | r | alpha | target_modules | trainable params |
|-------|---|-------|----------------|------------------|
| Llama-3.1-8B | 32 | 64 | q,k,v,o + gate,up,down | ~67M (0.84%) |

### Training Hyperparameters

**Llama-3.1-8B:**
```python
TrainingArguments(
    num_train_epochs=3,
    per_device_train_batch_size=4,
    gradient_accumulation_steps=4,
    learning_rate=2e-4,
    weight_decay=0.01,
    warmup_ratio=0.05,
    lr_scheduler_type="cosine",
    max_grad_norm=1.0,
    bf16=True,
    max_seq_length=768,
    logging_steps=10,
    eval_steps=100,
    save_steps=100,
    optim="paged_adamw_8bit"
)
```