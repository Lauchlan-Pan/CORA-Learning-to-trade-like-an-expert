# Stage I Evaluation

## Overview

210 MCQs for evaluating trading decision-making models. Questions cover technical analysis across multiple instruments with real market dates.

## Evaluation Protocols

### Protocol A: Standard Evaluation (No CORA Framework)

**Configuration:**
temperature = 0.0
max_tokens = 512

**Question Format:**
```python
prompt = f"""You are an expert trading advisor. Based on the following market scenario, select the most appropriate action.

Instrument: {mcq['instrument']}
Timeframe: {mcq['timeframe']}
Date: {mcq['as_of']}

{mcq['question']}

{chr(10).join(mcq['choices'])}

Provide your answer as a single letter (A, B, C, or D)."""
```

### Protocol B: CORA Framework Evaluation

**Configuration:**
temperature = 0.0
max_tokens = 512

**System Message:**
```python
"""You are an experienced trading agent. Review the trading scenario below and walk through your thinking using the CORA framework. Keep your explanation clear and focused on the decision:
1. Contextualize: Briefly describe the current market situation and the key factors that matter most
2. Organize: Clarify the trading objective, the available choices, and any important constraints
3. Reason: Explain why the selected option makes sense in this context, and why the other options are less suitable
4. Act: Outline the executable trading plan

After your analysis, clearly state your answer as:
Final Answer: [A/B/C/D]"""
```

**Note:** For CORA evaluation, replace the standard system message entirely.

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
2. Adapt the `generate_response()` function to use your model's generation API
3. Ensure the same temperature and max_tokens settings are applied, and use the appropriate prompt format (Protocol A or B)

The answer extraction logic and evaluation flow remain the same regardless of model type.
