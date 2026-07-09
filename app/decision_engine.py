"""Decision Engine (Module 6) — Weighted Sum Model, reasoning-trace-first.

Deterministic and fully explainable: the arithmetic is inspectable row by row.
The *number* is disposable; the reasoning trace, evidence links, and DNA check
are the asset. Pipeline:

  1. Min-max normalize each dimension across the alternatives (direction-aware).
  2. Apply editable weight preset -> weighted total -> rank.
  3. Strategic DNA guardrail: flag any alternative that conflicts with a
     Non-Negotiable (a DNA-conflicting option cannot be silently ranked #1).
  4. Sensitivity pass: perturb the winner by +/-SENSITIVITY_DELTA on each
     dimension; if the ranking flips, flag "fragile" and name the dimension.
  5. Pull supporting evidence from the vault (retrieval) for the reasoning trace.
  6. Emit a decision NOTE (markdown) with quality rubric + empty outcome.

Nothing here forecasts anything. It structures and compares.
"""
from __future__ import annotations
import re
from dataclasses import dataclass, field
from datetime import date

import config


@dataclass
class Alternative:
    name: str
    description: str = ""
    scores: dict[str, float] = field(default_factory=dict)  # dimension -> raw 1..10
    dna_conflict: str = ""   # non-empty => which Non-Negotiable it violates


@dataclass
class Scored:
    name: str
    weighted_total: float
    contributions: dict[str, float]      # dimension -> weighted contribution
    normalized: dict[str, float]         # dimension -> normalized 0..1
    rank: int = 0
    dna_conflict: str = ""


@dataclass
class DecisionResult:
    question: str
    decision_type: str
    weights: dict[str, float]
    scored: list[Scored]
    winner: str
    is_fragile: bool
    fragile_reason: str
    dna_flags: list[str]


def _normalize_weights(weights: dict[str, float]) -> dict[str, float]:
    total = sum(weights.values()) or 1.0
    return {k: v / total for k, v in weights.items()}


def _minmax(values: list[float]) -> list[float]:
    lo, hi = min(values), max(values)
    if hi == lo:
        return [1.0 for _ in values]   # all equal -> neutral (all best)
    return [(v - lo) / (hi - lo) for v in values]


def _compute(alts: list[Alternative], weights: dict[str, float]) -> list[Scored]:
    dims = list(weights.keys())
    # normalize per dimension, direction-aware
    norm_by_dim: dict[str, list[float]] = {}
    for d in dims:
        raw = [a.scores.get(d, 0.0) for a in alts]
        nm = _minmax(raw)
        if config.DECISION_DIMENSIONS.get(d, "+") == "-":
            nm = [1.0 - x for x in nm]   # invert cost/risk/effort/time
        norm_by_dim[d] = nm
    scored: list[Scored] = []
    for i, a in enumerate(alts):
        contribs = {d: weights[d] * norm_by_dim[d][i] for d in dims}
        scored.append(Scored(
            name=a.name,
            weighted_total=round(sum(contribs.values()), 4),
            contributions={d: round(v, 4) for d, v in contribs.items()},
            normalized={d: round(norm_by_dim[d][i], 4) for d in dims},
            dna_conflict=a.dna_conflict,
        ))
    # rank: DNA-conflicting options are demoted below all clean options
    scored.sort(key=lambda s: (bool(s.dna_conflict), -s.weighted_total))
    for r, s in enumerate(scored, 1):
        s.rank = r
    return scored


def _sensitivity(alts: list[Alternative], weights: dict[str, float],
                 baseline: list[Scored]) -> tuple[bool, str]:
    """Perturb the winner's raw scores by +/-delta per dimension; flag flips."""
    if len(alts) < 2:
        return False, ""
    winner_name = baseline[0].name
    winner = next(a for a in alts if a.name == winner_name)
    delta = config.SENSITIVITY_DELTA
    for d in weights:
        for sign in (-1, 1):
            perturbed = [
                Alternative(a.name, a.description, dict(a.scores), a.dna_conflict)
                for a in alts
            ]
            w = next(a for a in perturbed if a.name == winner_name)
            base = w.scores.get(d, 0.0)
            w.scores[d] = max(0.0, base * (1 + sign * delta))
            new_rank = _compute(perturbed, weights)
            if new_rank[0].name != winner_name:
                direction = "down" if sign < 0 else "up"
                return True, (f"a {int(delta*100)}% move {direction} in "
                              f"'{d}' flips the winner to '{new_rank[0].name}'")
    return False, ""


def evaluate(question: str, alternatives: list[Alternative],
             decision_type: str = "default",
             weights: dict[str, float] | None = None) -> DecisionResult:
    weights = _normalize_weights(
        weights or config.WEIGHT_PRESETS.get(decision_type, config.WEIGHT_PRESETS["default"])
    )
    scored = _compute(alternatives, weights)
    fragile, reason = _sensitivity(alternatives, weights, scored)
    dna_flags = [f"{a.name}: {a.dna_conflict}" for a in alternatives if a.dna_conflict]
    return DecisionResult(
        question=question, decision_type=decision_type, weights=weights,
        scored=scored, winner=scored[0].name,
        is_fragile=fragile, fragile_reason=reason, dna_flags=dna_flags,
    )


# --- Strategic DNA guardrail ----------------------------------------------
def load_non_negotiables() -> list[str]:
    """Parse NN bullet lines from DNA-Non-Negotiables.md."""
    p = config.VAULT_PATH / "500-Acredemia" / "Strategic-DNA" / "DNA-Non-Negotiables.md"
    if not p.exists():
        return []
    out = []
    for line in p.read_text(encoding="utf-8", errors="replace").splitlines():
        m = re.match(r"\s*-\s*\*\*(NN\d+)[^*]*\*\*\s*(.*)", line)
        if m:
            out.append(f"{m.group(1)} — {m.group(2).strip().strip('.')}")
    return out


def _evidence_for(question: str, k: int = 4):
    """Best-effort retrieval of supporting evidence; degrades to empty."""
    try:
        from search import SearchEngine
        eng = SearchEngine()
        return eng.search(question, k=k)
    except Exception:
        return []


# --- decision note emission -----------------------------------------------
def _next_dec_id() -> str:
    dec_dir = config.VAULT_PATH / "600-Decisions"
    n = 1
    if dec_dir.exists():
        ids = [re.search(r"DEC-\d{4}-(\d+)", p.name) for p in dec_dir.glob("*.md")]
        nums = [int(m.group(1)) for m in ids if m]
        n = (max(nums) + 1) if nums else 1
    return f"DEC-{date.today().year}-{n:03d}"


def _slug(text: str) -> str:
    return (re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:50]) or "decision"


def render_note(result: DecisionResult, dec_id: str,
                question_link: str = "", evidence=None) -> str:
    evidence = evidence or []
    dims = list(result.weights.keys())
    today = date.today().isoformat()

    # ranked comparison table (the inspectable arithmetic)
    header = "| rank | alternative | " + " | ".join(dims) + " | **total** |"
    sep = "|---|---|" + "|".join("---" for _ in dims) + "|---|"
    rows = []
    for s in result.scored:
        flag = " ⚠DNA" if s.dna_conflict else ""
        cells = " | ".join(f"{s.contributions[d]:.3f}" for d in dims)
        rows.append(f"| {s.rank} | {s.name}{flag} | {cells} | **{s.weighted_total:.3f}** |")
    table = "\n".join([header, sep, *rows])

    wline = ", ".join(f"{d} {result.weights[d]:.2f}({config.DECISION_DIMENSIONS[d]})" for d in dims)
    frag = (f"🟠 **Fragile** — {result.fragile_reason}. Treat the winner as sensitive to that estimate."
            if result.is_fragile else "🟢 Robust — winner survives ±"
            f"{int(config.SENSITIVITY_DELTA*100)}% perturbation on every dimension.")
    dna = ("\n".join(f"- ⚠ {f}" for f in result.dna_flags)
           if result.dna_flags else "- ✅ No alternative conflicts with a Non-Negotiable.")
    ev = ("\n".join(f"- [[{h.note}]] ({h.type}, conf={h.confidence}) — score {h.score}"
                    for h in evidence) if evidence else "- (no strong vault match — add evidence manually)")

    return f"""---
type: decision
id: {dec_id}
title: "{result.question}"
status: proposed
date: {today}
decider: [krish]
scale: decision
question: "{question_link}"
experiment: ""
decision-type: {result.decision_type}
winner: "{result.winner}"
is-fragile: {str(result.is_fragile).lower()}
decision-quality: "pending-score"
outcome: ""
confidence-state: emerging
freshness: fresh
last-reviewed: {today}
tags: [domain/]
---

# 🎯 {result.question}

> Generated by the Decision Engine (WSM). The number is disposable; the reasoning
> trace, evidence, and DNA check are the asset. Edit freely before finalizing.

## Recommendation
**{result.winner}** ranks first. {frag}

## Ranked comparison (weighted contributions — the arithmetic)
Weights ({result.decision_type}): {wline}

{table}

*Each cell = weight × direction-adjusted min-max-normalized score. Totals are the row sums.*

## Strategic DNA check
{dna}

## Supporting evidence (from the vault)
{ev}

## Why — the reasoning trace (fill this in; it's the real asset)
<Why does the ranking match or challenge your intuition? What's the winner's core thesis?>

## Assumptions
- [[A-...]]

## What would change my mind
- {result.fragile_reason or "<name the shakiest input>"}

---
## Decision QUALITY (score NOW, independent of outcome)
| criterion | score (1-5) | note |
|-----------|-------------|------|
| evidence sufficiency |  |  |
| reasoning clarity |  |  |
| alternatives explored |  | {len(result.scored)} compared |
| assumptions made explicit |  |  |
| risk awareness |  | {'fragile flagged' if result.is_fragile else 'robust'} |
| experiment quality |  |  |

---
## Decision OUTCOME (fill at retrospective — reality's verdict)
> Cannot mark `concluded` until filled.
- What actually happened:
- What surprised us:
- Lesson → [[L-...]]
"""


def create_decision_note(result: DecisionResult, question_link: str = "",
                         with_evidence: bool = True):
    dec_id = _next_dec_id()
    evidence = _evidence_for(result.question) if with_evidence else []
    content = render_note(result, dec_id, question_link, evidence)
    out = config.VAULT_PATH / "600-Decisions" / f"{dec_id}-{_slug(result.winner)}.md"
    out.write_text(content, encoding="utf-8")
    return out, dec_id


if __name__ == "__main__":
    import sys
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    # Demo: Tier-2 vs Tier-1 college beachhead
    alts = [
        Alternative("Tier-2 colleges first", "acute credibility gap, low competition",
                    {"impact": 8, "confidence": 5, "alignment": 8,
                     "cost": 4, "risk": 5, "effort": 5, "time": 4}),
        Alternative("Tier-1 colleges first", "prestige signal, crowded, weaker verification pull",
                    {"impact": 6, "confidence": 6, "alignment": 5,
                     "cost": 6, "risk": 6, "effort": 6, "time": 6}),
    ]
    res = evaluate("Which college tier should we target as the beachhead?",
                   alts, decision_type="channel-choice")
    print(f"Winner: {res.winner}")
    print(f"Fragile: {res.is_fragile} — {res.fragile_reason}")
    for s in res.scored:
        print(f"  #{s.rank} {s.name}: {s.weighted_total}")
    print("\nNon-negotiables loaded:", len(load_non_negotiables()))
