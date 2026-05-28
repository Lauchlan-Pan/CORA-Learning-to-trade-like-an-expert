#!/usr/bin/env python3
"""
Stage I Evaluation Example Script
Evaluates model on static MCQ reasoning task.
"""

import json
import re
import os
from pathlib import Path
from openai import OpenAI


def extract_answer_letter(response: str) -> str:
    """Extract answer letter (A, B, C, D) from model response."""
    response_clean = response.strip()
    
    match = re.search(r'(?:correct answer is|answer is|answer:)\s*([A-D])', response_clean, re.IGNORECASE)
    if match:
        return match.group(1).upper()
    
    match = re.match(r'^\s*([A-D])[).\s]', response_clean, re.IGNORECASE)
    if match:
        return match.group(1).upper()
    
    match = re.search(r'\b([A-D])\b', response_clean, re.IGNORECASE)
    if match:
        return match.group(1).upper()
    
    return "UNKNOWN"


def generate_response(client, model_name: str, question_text: str, max_tokens: int = 512, temperature: float = 0.0) -> str:
    """Generate response via API."""
    system_prompt = "You are an assistant analyzing various trading scenarios. Consider each option carefully but provide only one answer in the following format: Answer: [A/B/C/D]"
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": question_text}
    ]
    
    try:
        completion = client.chat.completions.create(
            model=model_name,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
        )
        content = completion.choices[0].message.content
        return content.strip() if content else ""
    except Exception:
        return "ERROR"


def evaluate(client, model_name: str, dataset: list) -> dict:
    """Evaluate model on dataset."""
    correct = 0
    predictions = []
    
    for idx, mcq in enumerate(dataset):
        question_text = mcq["question"] + "\n\n"
        for choice in mcq["choices"]:
            question_text += f"{choice}\n"
        
        correct_idx = mcq.get("correct_choice_index", 0)
        correct_answer = chr(65 + correct_idx)
        
        response = generate_response(client, model_name, question_text)
        predicted_answer = extract_answer_letter(response)
        is_correct = predicted_answer == correct_answer
        
        if is_correct:
            correct += 1
        
        predictions.append({
            "id": mcq.get("id", f"test_{idx}"),
            "correct_answer": correct_answer,
            "predicted_answer": predicted_answer,
            "is_correct": is_correct,
        })
    
    accuracy = correct / len(dataset) * 100
    
    return {
        "total_samples": len(dataset),
        "correct": correct,
        "accuracy": accuracy,
        "predictions": predictions
    }


def main():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise SystemExit("ERROR: Set OPENAI_API_KEY environment variable")
    
    client = OpenAI(api_key=api_key)
    
    model_name = ""  # Fill in your model name here
    data_path = Path(__file__).parent / "testing.json"
    
    with open(data_path) as f:
        dataset = json.load(f)
    
    results = evaluate(client, model_name, dataset)
    
    print(f"Accuracy: {results['accuracy']:.2f}% ({results['correct']}/{results['total_samples']})")
    
    output_path = Path(__file__).parent / "results.json"
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"Results saved to {output_path}")


if __name__ == "__main__":
    main()
