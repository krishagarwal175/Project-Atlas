---
type: mental-model
id: MM-expected-value
title: "Expected Value"
domain: decision-science
confidence-state: institutional
freshness: fresh
last-reviewed: 2026-07-10
tags: [domain/decision-science, domain/finance]
created: 2026-07-10
---

# 🧠 Expected Value

> The single most important number in decision-making under uncertainty: the probability-weighted average of all outcomes. `EV = Σ(probability × value)`.

## The idea
Don't judge a bet by its most likely outcome — judge it by the *distribution*. A choice with a 10% chance of +₹100 and 90% chance of −₹5 has EV = (0.1×100) + (0.9×−5) = **+5.5**, even though it "usually" loses. Over many independent decisions, total value converges on the sum of EVs. Founders make dozens of decisions; playing +EV consistently is how you win the series even while losing individual hands.

## When to reach for it
Any decision with quantifiable outcomes and rough probabilities: pricing changes, channel bets, "spend ₹5L on X." Pairs directly with the [[F-MCDA-weighted-sum|Decision Engine]] — WSM is EV's qualitative cousin when outcomes aren't monetary.

## Why it works
Linearity of expectation: EVs add up regardless of correlation. It forces you to name probabilities and magnitudes explicitly, which surfaces hidden assumptions (see [[MM-calibration]]).

## Failure modes / where it misleads
- **Ruin.** EV ignores that some losses end the game. A +EV bet that risks bankruptcy is still wrong ([[MM-margin-of-safety]] / avoid absorbing barriers). For a startup, runway is the absorbing barrier.
- **Fat tails & unknown probabilities.** When you can't estimate p, EV is theater. Use [[MM-scenario-planning]] instead.
- **Single-shot decisions.** The law of large numbers doesn't save you on a one-time irreversible bet.

## Worked example
"Launch a referral program": upside (viral loop, low CAC) × p(it transfers to us) − build cost. If p is low ([[A-referral-currency-exists]] is unproven), the honest move is a cheap experiment to raise p before committing — buying information is itself +EV.

## Applies to Acredemia
Use EV to size marketing/GTM bets; always check the **ruin** constraint against runway first ([[DNA-Decision-Principles]] DP1: reversible over irreversible).

## Related
- [[F-MCDA-weighted-sum]] · [[MM-base-rates]] · [[MM-scenario-planning]] · [[F-unit-economics]]
