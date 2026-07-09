"""Synthesis clustering + graph analytics (deterministic cores)."""
import numpy as np
import pytest

import synthesis
import graph as graphmod
from conftest import note_md


def test_cluster_separates_two_groups():
    # two obvious groups in 2D one-hot-ish space
    X = np.array([[1.0, 0.0], [1.0, 0.05], [0.0, 1.0], [0.05, 1.0]])
    groups = synthesis._cluster(X)
    # expect two clusters of two
    sizes = sorted(len(g) for g in groups)
    assert sizes == [2, 2]


def test_cluster_pair_branch():
    near = synthesis._cluster(np.array([[1.0, 0.0], [1.0, 0.01]]))
    far = synthesis._cluster(np.array([[1.0, 0.0], [0.0, 1.0]]))
    assert [sorted(g) for g in near] == [[0, 1]]
    assert sorted(len(g) for g in far) == [1, 1]


def test_synthesize_needs_two_cases(make_vault):
    notes = make_vault({"c.md": note_md("case-study", "Only", **{"company": "X", "move": "referral"})})
    assert synthesis.synthesize(notes) == []


def test_graph_pathfinding(make_vault):
    notes = make_vault({
        "a.md": note_md("question", "A", "to [[b]]", **{"tags": "[domain/gtm]"}),
        "b.md": note_md("theory", "B", "to [[c]]", **{"tags": "[domain/gtm]"}),
        "c.md": note_md("decision", "C", "leaf", **{"tags": "[domain/gtm]"}),
    })
    p = graphmod.path("a", "c", notes)
    assert p == ["a", "b", "c"]
    assert graphmod.summary(notes)["nodes"] == 3
