# Prompting Documentation

This document provides a comprehensive overview of all prompts and generation strategies used. All generation was performed using GPT-4o.

---

## 1. Textbook Knowledge Extraction

```
You are an expert in financial markets and trading. Based on the following text about trading and technical analysis, create {num_mcqs} high-quality multiple-choice question(s).

TEXT:
{text_segment}

REQUIREMENTS:
- Each question must be directly based on the provided text
- Focus on practical trading concepts, techniques, and decision-making
- Include specific numerical values, percentages, or technical details when available
- Each question must have exactly 4 choices (A, B, C, D)
- Only one choice should be correct
- Include a clear explanation for the correct answer
- Avoid generic questions like "According to the text..." 
- Make questions actionable and relevant to real trading scenarios

FORMAT: Return your response as a JSON array where each MCQ has this exact structure:
{
    "question": "Clear, specific question about trading concepts",
    "choices": ["A) First option", "B) Second option", "C) Third option", "D) Fourth option"],
    "correct_answer": "A",
    "explanation": "Detailed explanation of why this answer is correct and others are wrong"
}

Generate exactly {num_mcqs} MCQ(s):
```

---

## 2. Market Scenario Extraction

#### Agent 1: Market Narrator
**BASE PROMPT TEMPLATE:**

```
ROLE: You are a senior trading strategist who writes actionable market analysis for institutional traders.

TASK: Write a concise, action-focused market analysis that highlights specific trading opportunities, risks, or decisions. Focus on what traders should DO, not just what they should know.

VARIANT: {VARIANT_TYPE}

TECHNICAL DATA for {STOCK} as of {DATE}:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PRICE & TREND:
• Current Price: ${PRICE}
• SMA 20: ${SMA_20} | SMA 50: ${SMA_50} | SMA 200: ${SMA_200}
• Price vs SMA 20: {PRICE_SMA20_PCT}%
• Price vs SMA 50: {PRICE_SMA50_PCT}%
• Price vs SMA 200: {PRICE_SMA200_PCT}%

MOMENTUM INDICATORS:
• RSI (14): {RSI}
• MACD: {MACD} | Signal: {MACD_SIGNAL} | Histogram: {MACD_HIST}
• Stochastic %K: {STOCH_K} | %D: {STOCH_D}
• Williams %R: {WILLIAMS_R}

VOLATILITY & VOLUME:
• ATR (14): {ATR} ({ATR_PCT}% of price)
• Bollinger Band Position: {BB_POSITION}%
• Historical Volatility (20d): {VOLATILITY}%
• Volume vs 20-day avg: {VOLUME_ROC}%

TREND STRENGTH:
• ADX: {ADX} | +DI: {PLUS_DI} | -DI: {MINUS_DI}

{VARIANT_SPECIFIC_INSTRUCTIONS}

REQUIREMENTS:
1. Write exactly 2 sentences
2. Start with: "As of {DATE}, {STOCK}..."
3. Focus on ACTIONABLE insights, not just description
4. Use decisive language: "presents", "offers", "requires", "suggests"
5. Include specific risk/reward considerations
6. End with clear trading implications

YOUR ANALYSIS:
```

**VARIANT TYPES:**

**Variant A: Trading Setup Focus**
```
FOCUS: Identify specific entry/exit opportunities and timing considerations
LANGUAGE: "presents opportunity", "offers entry", "suggests timing", "favors strategy"
STRUCTURE: [Setup identification] + [Entry/exit timing considerations]
```

**Variant B: Risk Assessment Focus**
```
FOCUS: Evaluate risk levels, position sizing, and risk management requirements
LANGUAGE: "requires caution", "offers safety", "demands management", "suggests sizing"
STRUCTURE: [Risk evaluation] + [Management requirements/position sizing]
```

**Variant C: Signal Confirmation Focus**
```
FOCUS: Analyze signal strength, confirmations, and reliability of technical patterns
LANGUAGE: "confirms trend", "shows divergence", "lacks confirmation", "demonstrates strength"
STRUCTURE: [Signal analysis] + [Confirmation strength/reliability assessment]
```

#### Agent 2: MCQ Generator
**PROMPT TEMPLATE:**

```
You are an expert quantitative analyst specializing in comprehensive technical analysis. Based on the following {batch_size} enhanced market scenarios with diverse indicator coverage, create {batch_size} sophisticated multiple-choice questions.

ENHANCED TECHNICAL SCENARIOS:
{combined_scenarios}

CRITICAL REQUIREMENTS:
- Each question must focus on the SPECIFIC technical indicators mentioned in its scenario
- Move beyond basic RSI/MACD/ADX questions to include:
  * Bollinger Band strategies (BB_WIDTH, BB_POSITION)
  * Volume analysis (VOLUME_ROC, OBV, VWAP)
  * Stochastic oscillators (STOCH_K, STOCH_D, WILLIAMS_R)
  * Volatility analysis (VOLATILITY, ATR)
  * Moving average complexes (multiple SMAs, EMAs, ratios)
  * Trend strength analysis (ADX, PLUS_DI, MINUS_DI)
- Include specific technical values from the narrations
- Each question must have exactly 4 choices (A, B, C, D)
- Make questions self-contained with all necessary context
- Focus on advanced technical analysis concepts
- Test practical decision-making with complex indicators

ADVANCED QUESTION STYLES:
1. **Bollinger Band Questions**: "Given BB_WIDTH of X and BB_POSITION of Y, what strategy..."
2. **Volume Analysis**: "With VOLUME_ROC at X% and OBV showing Y, what does this indicate..."
3. **Stochastic Strategies**: "When STOCH_K is X and WILLIAMS_R is Y, what action..."
4. **Volatility Tactics**: "Given VOLATILITY of X% and ATR of Y, how should risk be managed..."
5. **Multi-Indicator Setups**: "With multiple oscillators showing X pattern, what approach..."

FORMAT: Return as JSON array where each MCQ has this structure:
{
    "question": "Advanced technical question using specific indicators and values",
    "choices": ["A) First option", "B) Second option", "C) Third option", "D) Fourth option"],
    "correct_answer": "A",
    "explanation": "Detailed technical explanation referencing specific indicators",
    "scenario_source": "STOCK_DATE_CONDITION",
    "technical_focus": "primary_indicator_category",
    "indicators_tested": ["list", "of", "specific", "indicators"]
}

Generate exactly {batch_size} diverse MCQs covering different technical indicator categories:
```

---

## 3. Committee Verification

### Verification Prompt Template

```
You are an expert financial analyst tasked with verifying the accuracy and quality of a multiple-choice question about trading and technical analysis.

MCQ TO VERIFY:
Question: {question}
Choices: {choices}
Proposed Correct Answer: {correct_answer}

YOUR TASK:
1. **PREDICT**: Independently determine which choice (A, B, C, or D) is the single best answer based on sound financial reasoning and the information provided in the question.

2. **JUSTIFY**: Provide a concise rationale (maximum 60 words) that explains your choice. Ground your reasoning in the specific facts, technical indicators, or market conditions mentioned in the question.

3. **AUDIT**: Flag any specific issues you identify:
   - Arithmetic errors or calculation mistakes
   - Misinterpretation of technical indicators
   - Semantic ambiguity or unclear wording
   - Factually incorrect statements
   - Multiple equally valid answers
   - Missing critical information

4. **ABSTAIN IF NECESSARY**: If the information provided is genuinely insufficient to determine a correct answer, output exactly "UNCERTAIN" rather than guessing.

CRITICAL INSTRUCTIONS:
- Work independently. Do not reference other models.
- Base your answer ONLY on the information in the question itself.
- If technical concepts are involved, apply standard financial definitions.
- Prioritize logical consistency and practical trading wisdom.

RESPONSE FORMAT (JSON):
{
    "predicted_answer": "A",
    "justification": "Your concise reasoning here (max 60 words)",
    "issues_flagged": ["List any specific problems", "Or empty list if none"],
    "confidence": "high/medium/low/uncertain"
}

Your verification:
```

---

## 4. CORA Framework Expansion

### CORA Conversion Prompt

```
You are an expert trading strategist who follows the CORA framework for structured trading decisions. Convert the following multiple-choice question into a complete CORA-structured analysis.

ORIGINAL MCQ:
Question: {question}
Choices: {choices}
Correct Answer: {correct_answer}) {correct_choice_text}

TASK: Create a comprehensive CORA analysis following this EXACT JSON structure:

{
  "id": "GENERATED_ID",
  "instrument": "EXTRACTED_OR_GENERIC",
  "timeframe": "INFERRED_OR_1h",
  "as_of": "INFERRED_OR_CURRENT_DATE",
  "question": "{question}",
  "choices": {choices},
  "correct_choice_index": {correct_choice_index},
  "contextualize": {
    "market_state": "Comprehensive summary of market conditions, trend, volatility, and technical setup from the question context"
  },
  "organize": {
    "goal": "Primary trading objective",
    "constraints": "Risk parameters and limitations", 
    "decision_type": "Type of decision required (entry/exit/position_sizing/risk_management)"
  },
  "reason": {
    "support_for_correct": "Detailed justification for why the correct choice is optimal, including technical analysis reasoning",
    "rebuttals": [
      "Why choice A is incorrect/suboptimal - specific technical reasoning",
      "Why choice B is incorrect/suboptimal - specific technical reasoning", 
      "Why choice C is incorrect/suboptimal - specific technical reasoning",
      "Why choice D is incorrect/suboptimal - specific technical reasoning"
    ]
  },
  "act_plan": {
    "direction": "long/short/flat",
    "entry_type": "market/limit/stop",
    "entry_price": NUMERIC_VALUE,
    "stop_price": NUMERIC_VALUE,
    "take_profits": [TARGET1, TARGET2],
    "risk_per_trade_pct": PERCENTAGE_VALUE,
    "position_size": "calculated_based_on_risk",
    "execution_notes": "Specific implementation guidance"
  }
}

CRITICAL REQUIREMENTS:
1. Extract instrument/stock symbol from question if mentioned, otherwise use "SPY"
2. Infer timeframe from context (1h, 4h, 1d) or default to "1h"
3. Create realistic entry/stop/target prices based on question context
4. Ensure stop_price < entry_price for long positions, stop_price > entry_price for short
5. Set risk_per_trade_pct between 1.0-3.0%
6. Make rebuttals specific to each incorrect choice (EXACTLY 4 rebuttals required)
7. Ensure act_plan is executable and realistic
8. Use current market-realistic prices

PRICE LOGIC GUIDELINES:
- If question mentions "$50 stock", use prices around that level
- If no prices mentioned, use realistic market prices ($100-500 range)
- Stop losses: 2-5% away from entry
- Take profits: 3-8% away from entry for first target, 6-15% for second

Generate the complete CORA JSON:
```