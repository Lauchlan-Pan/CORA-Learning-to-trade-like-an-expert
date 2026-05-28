#!/usr/bin/env python3
"""
Stage II Evaluation Example Script
Evaluates model on dynamic portfolio management task.
"""

import json
import re
import os
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional
import pandas as pd
from openai import OpenAI


ANSWER_PATTERN = re.compile(r"\b([A-I])\b", re.IGNORECASE)


@dataclass
class AccountState:
    cash: float = 10_000.0
    position: int = 0
    avg_entry: Optional[float] = None
    last_action: str = "initialized with cash only"
    
    def equity(self, price: float) -> float:
        return self.cash + self.position * price
    
    def snapshot(self, price: float, timestamp: str) -> dict:
        equity = self.equity(price)
        unrealized = 0.0 if self.position == 0 or self.avg_entry is None else (price - self.avg_entry) * self.position
        return {
            "cash": round(self.cash, 2),
            "position_shares": int(self.position),
            "avg_entry_price": None if self.avg_entry is None else round(self.avg_entry, 2),
            "equity": round(equity, 2),
            "unrealized_pnl": round(unrealized, 2),
            "cumulative_return_pct": round((equity / 10_000 - 1) * 100, 2),
            "last_action": self.last_action,
            "timestamp": timestamp,
        }
    
    def apply(self, target_position: int, price: float, label: str):
        delta = target_position - self.position
        if delta == 0:
            self.last_action = f"held exposure via choice {label}"
            return
        if delta > 0:
            cost = delta * price
            self.cash -= cost
            if self.position >= 0:
                total = self.position + delta
                if self.position == 0:
                    self.avg_entry = price
                else:
                    self.avg_entry = ((self.avg_entry or 0) * self.position + price * delta) / total
            else:
                net = self.position + delta
                if net >= 0:
                    self.avg_entry = price if net > 0 else None
            self.position += delta
            self.last_action = f"bought {delta} @ ${price:.2f} ({label})"
        else:
            qty = abs(delta)
            proceeds = qty * price
            self.cash += proceeds
            if self.position <= 0:
                total = self.position - qty
                if self.position == 0:
                    self.avg_entry = price
                else:
                    self.avg_entry = ((self.avg_entry or 0) * abs(self.position) + price * qty) / abs(total)
            else:
                net = self.position - qty
                if net <= 0:
                    self.avg_entry = price if net < 0 else None
            self.position -= qty
            self.last_action = f"sold {qty} @ ${price:.2f} ({label})"


def compute_max_shares(equity: float, price: float, leverage: float) -> int:
    if price <= 0 or equity <= 0:
        return 0
    return max(0, int((equity * leverage) // price))


def target_position_from_choice(choice: dict, state: AccountState, price: float, leverage: float) -> int:
    order = choice.get("order", {})
    side = order.get("side")
    if side == "reduce":
        qty = int(order.get("quantity") or 0)
        if qty <= 0:
            return state.position
        if state.position > 0:
            return max(0, state.position - qty)
        if state.position < 0:
            return min(0, state.position + qty)
        return 0
    if order.get("mode") != "target_fraction":
        qty = int(order.get("quantity") or 0)
        if side == "buy":
            return state.position + qty
        if side == "sell_short":
            return state.position - qty
        if side == "flat":
            return 0
        return state.position
    max_shares = compute_max_shares(state.equity(price), price, leverage)
    if max_shares == 0:
        return 0
    qty = int(round(max_shares * order.get("exposure_fraction", 0)))
    if qty == 0 and order.get("exposure_fraction", 0) > 0:
        qty = 1
    target = qty if order.get("direction") == "long" else -qty
    return max(-max_shares, min(max_shares, target))


def render_choice_text(choice: dict, target: int, state: AccountState, price: float) -> str:
    delta = target - state.position
    if delta == 0:
        note = "(no change)"
    elif delta > 0:
        note = f"(buy {delta} → net {target})"
    else:
        note = f"(sell {abs(delta)} → net {target})"
    approx_notional = abs(target) * price
    return f"{choice['label']}. {choice['text']} {note}, ~${approx_notional:,.0f} notional"


def build_prompt(mcq: dict, rendered_choices: list, snapshot: dict) -> str:
    state_line = (
        f"Account {mcq['state_id']}: equity ${snapshot['equity']:.2f} "
        f"({snapshot['cumulative_return_pct']:+.2f}%), cash ${snapshot['cash']:.2f}, "
        f"position {snapshot['position_shares']} shares @ {snapshot['avg_entry_price']}. "
        f"Last action: {snapshot['last_action']}."
    )
    choices_text = "\n".join(rendered_choices)
    return (
        f"{state_line}\n\n{mcq['question']}\n\nChoices:\n{choices_text}\n\n"
        "Respond with a single letter (A-I) plus a concise justification."
    )


def call_model(client: OpenAI, model_name: str, prompt: str, max_tokens: int, temperature: float, pause: float) -> str:
    messages = [
        {
            "role": "system",
            "content": "You manage a $10k equity book. Pick the best exposure adjustment for the next session.",
        },
        {"role": "user", "content": prompt},
    ]
    for attempt in range(3):
        try:
            completion = client.chat.completions.create(
                model=model_name,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
            )
            text = completion.choices[0].message.content or ""
            return text.strip()
        except Exception:
            wait = pause * (attempt + 1)
            time.sleep(wait)
    return "ERROR"


def run_episode(dataset_path: Path, client: OpenAI, model_name: str, max_tokens: int, temperature: float, leverage: float, pause: float):
    dataset = json.loads(dataset_path.read_text())
    mcqs = sorted(dataset["mcqs"], key=lambda x: x["chronological_index"])
    
    account = AccountState()
    equity_history = []
    
    for mcq in mcqs:
        price = mcq["market_snapshot"]["close"]
        snapshot = account.snapshot(price, mcq["reference_session"])
        
        targets = {}
        rendered = []
        for choice in mcq["choices"]:
            target = target_position_from_choice(choice, account, price, leverage)
            targets[choice["label"]] = target
            rendered.append(render_choice_text(choice, target, account, price))
        
        prompt = build_prompt(mcq, rendered, snapshot)
        response = call_model(client, model_name, prompt, max_tokens, temperature, pause)
        
        match = ANSWER_PATTERN.search(response)
        letter = match.group(1).upper() if match else "I"
        target_position = targets.get(letter, account.position)
        account.apply(target_position, price, letter)
        
        equity = account.equity(price)
        equity_history.append({
            "date": datetime.fromisoformat(mcq["time_spot"]),
            "equity": equity,
            "cash": account.cash,
            "position": account.position,
            "price": price,
        })
    
    return account, equity_history


def main():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise SystemExit("ERROR: Set OPENAI_API_KEY environment variable")
    
    client = OpenAI(api_key=api_key)
    
    model_name = ""  # Fill in your model name here
    max_tokens = 256
    temperature = 0.0
    leverage = 2.5
    pause = 1.0
    
    dataset_path = Path(__file__).parent / "50_bullish" / "bullish_sample_001.json"
    
    account, equity_history = run_episode(
        dataset_path, client, model_name, max_tokens, temperature, leverage, pause
    )
    
    final_equity = equity_history[-1]["equity"]
    total_return = (final_equity - 10_000) / 10_000 * 100
    
    print(f"Episode: {dataset_path.name}")
    print(f"Return: {total_return:+.2f}% (${final_equity:.2f})")
    
    output_path = Path(__file__).parent / "episode_results.csv"
    pd.DataFrame(equity_history).to_csv(output_path, index=False)
    print(f"Results saved to {output_path}")


if __name__ == "__main__":
    main()
