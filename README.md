# CORA: Contextualize, Organize, Reason, Act

This repository contains the datasets and evaluation benchmarks accompanying the CORA framework.

Each subdirectory includes its own README with detailed usage instructions — see [`training/`](training/README.md), [`evaluation/stage_I/`](evaluation/stage_I/README.md), and [`evaluation/stage_II/`](evaluation/stage_II/README.md).

## Repository Structure

```
.
├── training/          # Training & validation datasets with CORA + DARA augmentation
├── evaluation/
│   ├── stage_I/       # Static MCQ benchmark (210 questions, isolated decisions)
│   └── stage_II/      # Sequential portfolio benchmark (150 episodes, 25 steps each)
└── LICENSE
```

## Contents

### [`training/`](training/README.md)
Fine-tuning data (~27,800 CORA-formatted examples) with full documentation of the dataset construction pipeline, CORA expansion prompts, DARA augmentation methodology, and QLoRA fine-tuning configuration.

### [`evaluation/stage_I/`](evaluation/stage_I/README.md)
210 multiple-choice questions in the stock market. Includes an example evaluation script compatible with any OpenAI-compatible API.

### [`evaluation/stage_II/`](evaluation/stage_II/README.md)
150 chronological 25-step episodes (50 bullish, 50 bearish, 50 mixed regime) for evaluating sequential portfolio management. Each episode tracks position, P&L, and equity across a 9-choice action space with leverage constraints.

## Paper & Citation

[Learning to Trade Like an Expert: Cognitive Fine-Tuning for Stable Financial Reasoning in Language Models](https://openreview.net/forum?id=01bO7bdq4e)  
Yuchen Pan, Soung Chang Liew — ICML 2026 Workshop on Foundations of Deep Generative Models

If you use this dataset or code in academic research, please cite:

```bibtex
@inproceedings{
pan2026learning,
title={Learning to Trade Like an Expert: Cognitive Fine-Tuning for Stable Financial Reasoning in Language Models},
author={Yuchen Pan and Soung Chang Liew},
booktitle={ICML 2026 Workshop on Foundations of Deep Generative Models: Understanding Memorization, Generalization, and Reasoning},
year={2026},
url={https://openreview.net/forum?id=01bO7bdq4e}
}
```

## License

MIT — see [LICENSE](LICENSE).

