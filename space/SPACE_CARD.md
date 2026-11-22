---
title: Weil Positivity Gauge
emoji: 🧭
colorFrom: green
colorTo: blue
sdk: gradio
sdk_version: 6.14.0
app_file: app.py
pinned: true
license: mit
short_description: Live test of Weil positivity, the criterion behind RH
---

# Weil Positivity Gauge

A live instrument for Weil's positivity criterion, the statement equivalent to the Riemann Hypothesis. Genuine L-functions keep the needle above zero. Imitations drop below. Every number on the page is computed in your session.

**Independent reproduction of the proof:** VIDRAFT compiled the full released Lean proof (175,187 files, 0 errors, 22 November 2026). `#print axioms riemannHypothesis` reports `propext`, `Classical.choice`, `Quot.sound`, the standard axioms only.

Data, code and machine-checked files: https://huggingface.co/datasets/FINAL-Bench/weil-positivity-gauge
GitHub: https://github.com/final-bench/weil-positivity-gauge
Article: https://huggingface.co/blog/FINAL-Bench/seeing-the-riemann-hypothesis-hold-a-live-weil-pos