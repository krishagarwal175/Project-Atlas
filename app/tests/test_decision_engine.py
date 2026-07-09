"""Decision Engine: WSM ranking, direction inversion, DNA guardrail, sensitivity."""
from decision_engine import Alternative, evaluate, _minmax, _normalize_weights


def test_minmax_and_weight_normalization():
    assert _minmax([2, 8]) == [0.0, 1.0]
    assert _minmax([5, 5]) == [1.0, 1.0]  # all-equal -> neutral
    w = _normalize_weights({"a": 1, "b": 3})
    assert abs(sum(w.values()) - 1.0) < 1e-9


def test_positive_dimension_higher_wins():
    alts = [Alternative("hi", scores={"impact": 9}), Alternative("lo", scores={"impact": 2})]
    r = evaluate("q", alts, weights={"impact": 1})
    assert r.winner == "hi"


def test_cost_dimension_is_inverted():
    # only cost matters; lower cost should win (direction "-")
    alts = [Alternative("cheap", scores={"cost": 2}), Alternative("pricey", scores={"cost": 9})]
    r = evaluate("q", alts, weights={"cost": 1})
    assert r.winner == "cheap"


def test_dna_conflict_demoted_below_clean_option():
    alts = [
        Alternative("bad-but-strong", scores={"impact": 10}, dna_conflict="NN2 violated"),
        Alternative("clean-weaker", scores={"impact": 3}),
    ]
    r = evaluate("q", alts, weights={"impact": 1})
    assert r.winner == "clean-weaker"
    assert r.scored[-1].name == "bad-but-strong"
    assert r.dna_flags


def test_near_tie_is_fragile():
    alts = [
        Alternative("A", scores={"impact": 6, "cost": 5}),
        Alternative("B", scores={"impact": 5, "cost": 5}),
    ]
    r = evaluate("q", alts, weights={"impact": 1, "cost": 1})
    assert r.is_fragile
    assert "impact" in r.fragile_reason


def test_clear_winner_is_robust():
    alts = [
        Alternative("A", scores={"impact": 10, "cost": 1}),
        Alternative("B", scores={"impact": 1, "cost": 10}),
    ]
    r = evaluate("q", alts, weights={"impact": 1, "cost": 1})
    assert not r.is_fragile
