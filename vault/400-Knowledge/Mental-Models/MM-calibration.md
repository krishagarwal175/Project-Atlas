---
type: mental-model
id: MM-calibration
title: "Calibration"
domain: decision-science
confidence-state: institutional
freshness: fresh
last-reviewed: 2026-07-10
tags: [domain/decision-science]
created: 2026-07-10
---

# 🧠 Calibration

> Being calibrated means your confidence matches your accuracy: of the things you're 70% sure about, ~70% should turn out true. Most people are wildly overconfident; calibration is a *trainable* skill.

## The idea
Confidence is a claim about frequency. A calibrated founder who says "80% likely" is right about 80% of the time across many such claims. You improve by (1) recording predictions with probabilities, (2) checking them against reality, (3) noticing systematic skew (e.g. you over-rate "impact"). This turns forecasting from vibes into a measurable skill.

## When to reach for it
Every probability you attach to an experiment, a decision score, a market call. Especially the [[F-MCDA-weighted-sum|Decision Engine]]'s confidence dimension.

## Why it works
Feedback loops. Skill without a scorecard doesn't improve; calibration supplies the scorecard.

## Failure modes / where it misleads
- **Small samples.** With few resolved predictions, apparent miscalibration may be noise — directional signal only.
- **Gaming.** Hedging everything to 50% is "calibrated" but useless; good forecasting needs both calibration *and* resolution (confidently right).

## Worked example
Atlas builds this in: the decision log records a predicted top choice; concluded experiments record what actually happened; the calibration strip shows predicted-vs-actual over time. If you systematically over-rate "impact," the vault will eventually show it — and you adjust your weight presets.

## Applies to Acredemia
Treat every decision's confidence as a *forecast you'll be graded on*. Over a year, the vault becomes your personal calibration record — the compounding edge no competitor has.

## Related
- [[MM-base-rates]] · [[MM-expected-value]] · [[MM-decision-quality-vs-outcome]]
