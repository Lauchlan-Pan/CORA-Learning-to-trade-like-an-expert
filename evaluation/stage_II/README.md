# Stage II Evaluation

## Overview

Stage II evaluates sequential trading decision-making through **chronological MCQ-based episodes**. Unlike Stage I's isolated decision evaluation, Stage II embeds MCQs in a temporal feedback loop with portfolio state tracking, enabling assessment of dynamic adaptation under realistic capital and risk constraints.

**Key Differences from Stage I:**
- **Sequential decisions** with persistent state (position, P&L, exposure history)
- **9-choice action space** (±20%, ±40%, ±60%, ±80% exposure, or flat)
- **Portfolio simulation** with leverage constraints and capital dynamics
- **Statistical rigor**: 150 episodes × 25 steps = 3,750 decision points

## Dataset Structure

```
stage_II/
├── 50_bullish/                # 50 bullish regime episodes
│   ├── bullish_sample_001.json
│   ├── bullish_sample_001_state_template.json
│   └── ...
├── 50_bearish/                # 50 bearish regime episodes
│   └── ...
├── 50_mixed/                  # 50 mixed regime episodes
│   └── ...
├── results_bullish.csv        # Performance metrics by regime
├── results_bearish.csv
├── results_mixed.csv
├── results_overall.csv        # Aggregated results across all regimes
└── evaluate_example.py        # Example evaluation script
```

**Episodes:** 150 non-overlapping 25-day windows across 15 years (2010–2025) of S&P 500 constituent data  
**Regimes:** Bullish (>5% BH return), Bearish (<-5% BH return), Mixed (remainder)  
**Sampling:** Ticker-first round-robin to avoid concentration bias

## Evaluation Protocol

### Configuration

```python
initial_capital = 10_000.0
max_leverage = 2.5
temperature = 0.0
max_tokens = 256
```

### Action Space (9 Choices)

Each MCQ presents 9 discrete target exposure options:
- **A-D**: Long positions at 80%, 60%, 40%, 20% of allowable exposure
- **E-H**: Short positions at -80%, -60%, -40%, -20% of allowable exposure
- **I**: Flat (0% exposure, liquidate all positions)

**Allowable exposure** = `equity × leverage / current_price`

### Portfolio Simulation Logic

```python
class AccountState:
    cash: float = 10_000.0
    position: int = 0  # shares held (positive = long, negative = short)
    avg_entry: float = None
    last_action: str = "initialized with cash only"
    
    def equity(self, price: float) -> float:
        return self.cash + self.position * price
    
    def apply(self, target_position: int, price: float, label: str):
        delta = target_position - self.position
        # Execute buy/sell to reach target_position
        # Update cash, position, avg_entry, last_action
```

**Key Features:**
- Frictionless execution (no slippage, commissions, or borrowing costs)
- Mark-to-market equity calculation at each step
- Position-weighted average entry price tracking
- Persistent state ledger across all 25 decisions

### Prompt Template

```python
system_prompt = """You manage a $10k equity book. Pick the best exposure adjustment for the next session."""

state_line = f"""Account {state_id}: equity ${equity:.2f} ({return_pct:+.2f}%), 
cash ${cash:.2f}, position {position_shares} shares @ {avg_entry_price}. 
Last action: {last_action}."""

choices_with_notional = [
    "A. Target +80% long (buy 150 → net 150), ~$4,455 notional",
    "B. Target +60% long (buy 113 → net 113), ~$3,341 notional",
    ...
]

user_prompt = f"""{state_line}

{question}

Choices:
{choices_with_notional}

Respond with a single letter (A-I) plus a concise justification."""
```

## Example Script

The provided `evaluate_example.py` script demonstrates evaluation using **OpenAI-compatible API models**.

**Usage:**
```bash
export OPENAI_API_KEY="your-api-key"
python evaluate_example.py
```

**For Local Fine-Tuned Models:**
The example script requires modification to load local model weights. You will need to:
1. Replace the OpenAI client with your model inference pipeline (e.g., Hugging Face `transformers`, `vllm`)
2. Adapt the `call_model()` function to use your model's generation API
3. Ensure the same temperature, max_tokens, and system prompt are applied
4. Maintain the exact portfolio simulation logic (`AccountState`, `target_position_from_choice`, etc.)

The prompt formatting, answer extraction, and portfolio accounting remain identical regardless of model type.