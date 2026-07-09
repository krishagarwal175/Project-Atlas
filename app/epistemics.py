"""Epistemics engine (Modules 10 & 11) — Confidence, Contradiction, Decay.

Confidence is a DERIVED state, never a stored number. This module recomputes the
state for every claim-bearing note from its Evidence Ledger + contradiction
searches + freshness, following the rules in 900-Meta/Vault-Governance.md:

  - Promotion past 'emerging' requires BOTH supporting weight AND a documented
    contradiction search that the claim survived. You cannot reach 'well-tested'
    on confirming evidence alone.
  - A SURVIVED contradiction search raises confidence (stronger by not dying).
  - A SUCCESSFUL counterexample (broken) sets 'contested' and caps the state.
  - Decay (freshness lapsed) caps the effective state until re-reviewed.

It NEVER mutates source notes (that stays human-authored). It computes, explains,
and reports drift — the governance bot and API surface the results.
"""
from __future__ import annotations
from dataclasses import dataclass
from datetime import date

import config
from vault import Note, load_vault

LADDER = config.CONFIDENCE_LADDER
_WEIGHT = {"high": 3, "med": 2, "medium": 2, "low": 1, "": 1}


@dataclass
class Assessment:
    note: str
    stated: str            # confidence-state as written
    derived: str           # what the ledger + searches justify
    contested: bool
    decaying: bool
    drift: bool            # stated != derived
    supporting: int
    contradicting: int
    searches_survived: int
    searches_broken: int
    derivation: str        # one-line human-readable explanation


def _supporting_weight(n: Note) -> int:
    w = sum(_WEIGHT.get(l.weight.lower(), 1) for l in n.ledger if l.stance == "supports")
    # Patterns don't carry a ledger; their support is the count of case studies
    # they're derived from (each a moderate-weight supporting instance).
    if n.type == "pattern":
        derived = n.frontmatter.get("derived-from") or []
        if isinstance(derived, list):
            w += 2 * len([d for d in derived if isinstance(d, str) and d.strip()])
    return w


def _contradicting(n: Note) -> int:
    return sum(1 for l in n.ledger if l.stance == "contradicts")


def _find_searches(theory: Note, all_notes: list[Note]) -> tuple[int, int]:
    """Count contradiction notes targeting this theory, by outcome."""
    survived = broken = 0
    key = theory.filename.lower()
    for n in all_notes:
        if n.type != "contradiction":
            continue
        tgt = str(n.frontmatter.get("targets", "")).strip().strip("[]").lower().split("/")[-1]
        if tgt == key or key in tgt:
            outcome = str(n.frontmatter.get("outcome", "")).strip().lower()
            if outcome == "survived":
                survived += 1
            elif outcome == "broken":
                broken += 1
    return survived, broken


def _is_decaying(n: Note, today: date) -> bool:
    hl = config.HALF_LIFE_DAYS.get(n.type, config.DEFAULT_HALF_LIFE)
    lr = n.fm_date("last-reviewed")
    if not hl or not lr:
        return False
    return (today - lr).days > hl


def _derive_state(support_w: int, contra: int, survived: int, broken: int,
                  decaying: bool) -> tuple[str, bool, str]:
    """Return (derived_state, contested, explanation)."""
    contested = broken > 0 or contra > 0
    # base level from supporting weight
    if support_w <= 0:
        level = "speculative"
    elif support_w <= 1:
        level = "emerging"
    else:
        level = "supported"
    # cannot exceed 'emerging' without a survived contradiction search
    if survived == 0 and LADDER.index(level) > LADDER.index("emerging"):
        level = "emerging"
        gate = " (capped at emerging: no contradiction search survived yet)"
    else:
        gate = ""
    # survived searches raise the ceiling
    if survived >= 1 and support_w >= 2 and not contested:
        level = "well-tested"
    if survived >= 2 and support_w >= 3 and not contested:
        level = "institutional"
    # decay caps one rung down
    capped = ""
    if decaying and LADDER.index(level) > 0:
        level = LADDER[LADDER.index(level) - 1]
        capped = " ⌛capped (decaying)"
    expl = (f"{support_w} supporting wt, {contra} contradicting, "
            f"{survived} search(es) survived, {broken} broke{gate}{capped}")
    return level, contested, expl


def assess_all(notes: list[Note] | None = None, today: date | None = None) -> list[Assessment]:
    notes = notes or load_vault()
    today = today or date.today()
    # Decisions have their own quality/outcome model — not ledger-derived confidence.
    claim_types = {"theory", "pattern", "assumption"}
    out: list[Assessment] = []
    for n in notes:
        if n.type not in claim_types:
            continue
        support_w = _supporting_weight(n)
        contra = _contradicting(n)
        survived, broken = _find_searches(n, notes) if n.type == "theory" else (0, 0)
        # patterns/assumptions can't run contradiction searches; use ledger only
        decaying = _is_decaying(n, today)
        derived, contested, expl = _derive_state(support_w, contra, survived, broken, decaying)
        stated = n.confidence_state or "-"
        drift = stated not in ("-", "") and stated != derived
        out.append(Assessment(
            note=n.filename, stated=stated, derived=derived, contested=contested,
            decaying=decaying, drift=drift, supporting=support_w, contradicting=contra,
            searches_survived=survived, searches_broken=broken, derivation=expl,
        ))
    return out


if __name__ == "__main__":
    import sys
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    for a in assess_all():
        flag = "  <<< DRIFT" if a.drift else ""
        badge = ("⚑" if a.contested else " ") + ("⌛" if a.decaying else " ")
        print(f"{badge} {a.note[:52]:52} stated={a.stated:12} derived={a.derived:12}{flag}")
        print(f"       {a.derivation}")
