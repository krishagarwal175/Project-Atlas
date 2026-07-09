"""Synthesis / Understanding engine (Module 5 -> 9).

Turns stored case studies into DRAFTED understanding: it clusters case studies
by similarity + shared tags, and for each cluster proposes a *candidate pattern*
("across these cases, X recurs") — synthesis, not storage.

Deterministic core (clustering + theme extraction), so it's explainable and
free. An optional local Ollama pass can phrase the principle in prose; without
it, a deterministic template is used. Candidates are NEVER auto-promoted — the
founder reviews and, if convinced, writes them into 400-Knowledge/Patterns.
The engine drafts; the human decides.
"""
from __future__ import annotations
from collections import Counter
from dataclasses import dataclass, field

import config
from vault import Note, load_vault

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.cluster import AgglomerativeClustering
    import numpy as np
    _SK = True
except Exception:
    _SK = False

# Cosine-distance threshold for agglomerative clustering. Average linkage avoids
# the transitive chaining that a similarity-graph would suffer at tiny N.
CLUSTER_DISTANCE = 0.85

# Generic startup vocabulary that would create spurious clusters (e.g. two
# unrelated "*-driven-growth" moves). Stopworded so real signal dominates.
GENERIC_TERMS = {"growth", "driven", "based", "program", "strategy",
                 "company", "product", "scaling", "loop", "loops"}


@dataclass
class Candidate:
    members: list[str]                       # case-study filenames
    companies: list[str]
    shared_tags: list[str]
    top_terms: list[str]
    outcomes: dict[str, int]
    existing_pattern: str = ""               # if an existing pattern already covers it
    draft: str = ""
    novelty: str = "new"                     # new | covered


def _case_studies(notes: list[Note]) -> list[Note]:
    return [n for n in notes if n.type == "case-study"]


def _tags(n: Note) -> set[str]:
    t = n.frontmatter.get("tags") or []
    return {str(x).lower() for x in t} if isinstance(t, list) else set()


def _doc(n: Note) -> str:
    """Boost the discriminative fields (move, tags) over generic body prose,
    stripping generic growth vocabulary that would over-connect clusters."""
    move = " ".join(w for w in str(n.frontmatter.get("move", "")).replace("-", " ").split()
                    if w not in GENERIC_TERMS)
    tags = " ".join(t.replace("domain/", "") for t in _tags(n))
    return f"{(move + ' ') * 5}{(tags + ' ') * 5}{n.title} {n.body[:600]}"


def _cluster(X) -> list[list[int]]:
    """Agglomerative clustering on cosine distance; return index groups."""
    n = X.shape[0]
    if n == 2:
        # AgglomerativeClustering needs >=2 samples; handle the pair directly.
        from sklearn.metrics.pairwise import cosine_distances
        d = cosine_distances(X)[0][1]
        return [[0, 1]] if d <= CLUSTER_DISTANCE else [[0], [1]]
    labels = AgglomerativeClustering(
        metric="cosine", linkage="average",
        distance_threshold=CLUSTER_DISTANCE, n_clusters=None,
    ).fit(X).labels_
    groups: dict[int, list[int]] = {}
    for i, l in enumerate(labels):
        groups.setdefault(int(l), []).append(i)
    return list(groups.values())


def _existing_patterns(notes: list[Note]) -> dict[str, set[str]]:
    """Map existing pattern -> set of case-study filenames it's derived from."""
    out = {}
    for n in notes:
        if n.type != "pattern":
            continue
        derived = n.frontmatter.get("derived-from") or []
        keys = set()
        for d in derived if isinstance(derived, list) else []:
            if isinstance(d, str):
                keys.add(d.strip().strip("[]").split("/")[-1].lower())
        out[n.filename] = keys
    return out


def synthesize(notes: list[Note] | None = None, use_ollama: bool = False) -> list[Candidate]:
    notes = notes or load_vault()
    cases = _case_studies(notes)
    if len(cases) < 2 or not _SK:
        return []
    docs = [_doc(c) for c in cases]
    stop = list(TfidfVectorizer(stop_words="english").get_stop_words()) + list(GENERIC_TERMS)
    vec = TfidfVectorizer(stop_words=stop, ngram_range=(1, 2), max_features=400)
    X = vec.fit_transform(docs).toarray()
    terms = vec.get_feature_names_out()

    existing = _existing_patterns(notes)
    candidates: list[Candidate] = []
    for comp in _cluster(X):
        if len(comp) < 2:
            continue   # a lone case study isn't a pattern
        members = [cases[i] for i in comp]
        member_keys = {m.filename.lower() for m in members}
        # shared tags across the cluster
        tag_sets = [_tags(m) for m in members]
        shared = set.intersection(*tag_sets) if tag_sets else set()
        # top TF-IDF terms summed across the cluster
        sub = X[comp].sum(axis=0)
        arr = sub.A1 if hasattr(sub, "A1") else np.asarray(sub).ravel()
        top_idx = arr.argsort()[::-1][:8]
        top_terms = [terms[i] for i in top_idx if arr[i] > 0]
        outcomes = Counter(str(m.frontmatter.get("outcome", "?")) for m in members)
        # does an existing pattern already cover this cluster?
        covered_by = ""
        for pat, keys in existing.items():
            if keys and keys & member_keys and len(keys & member_keys) >= 2:
                covered_by = pat
                break
        cand = Candidate(
            members=[m.filename for m in members],
            companies=[str(m.frontmatter.get("company", m.filename)) for m in members],
            shared_tags=sorted(t.replace("domain/", "") for t in shared),
            top_terms=top_terms,
            outcomes=dict(outcomes),
            existing_pattern=covered_by,
            novelty="covered" if covered_by else "new",
        )
        cand.draft = _draft(cand, members, use_ollama)
        candidates.append(cand)
    candidates.sort(key=lambda c: (c.novelty != "new", -len(c.members)))
    return candidates


def _draft(c: Candidate, members: list[Note], use_ollama: bool) -> str:
    themes = ", ".join(c.shared_tags or c.top_terms[:4]) or "shared strategy"
    companies = ", ".join(c.companies)
    outmix = ", ".join(f"{k}:{v}" for k, v in c.outcomes.items())
    deterministic = (f"Across {companies}, a recurring pattern appears around "
                     f"[{themes}] (outcomes: {outmix}). Candidate principle: these cases "
                     f"share an approach worth naming as a reusable pattern; verify the "
                     f"causal claim and run a contradiction search before promoting to a theory.")
    if use_ollama:
        try:
            import narrative
            if narrative.ollama_available():
                bodies = "\n\n".join(f"{m.title}:\n{m.body[:800]}" for m in members)
                prompt = (f"These startup case studies share themes [{themes}]. In 2 sentences, "
                          f"propose ONE reusable strategic principle they have in common. Do not "
                          f"invent facts. Cases:\n\n{bodies}")
                txt = narrative._ollama(prompt)
                if txt:
                    return txt + "  (draft — verify before promoting)"
        except Exception:
            pass
    return deterministic


def promote_candidate(c: Candidate) -> tuple:
    """Write a candidate as a draft pattern note (human-approved) into the vault."""
    import re
    from datetime import date
    slug = "-".join((c.shared_tags or c.top_terms[:2] or ["synthesized"]))[:40]
    slug = re.sub(r"[^a-z0-9]+", "-", slug.lower()).strip("-")
    pid = f"P-{slug}-candidate"
    derived = ", ".join(f'"[[{m}]]"' for m in c.members)
    content = f"""---
type: pattern
id: {pid}
title: "Candidate: recurring pattern across {', '.join(c.companies)}"
derived-from: [{derived}]
confidence-state: speculative
freshness: fresh
last-reviewed: {date.today().isoformat()}
scale: knowledge
tags: [{', '.join(f'"domain/{t}"' for t in c.shared_tags) or '"domain/"'}]
status: candidate
created: {date.today().isoformat()}
---

# 🔁 Candidate pattern (synthesized — review before accepting)

> Auto-drafted by the Synthesis engine from clustered case studies. NOT accepted
> — verify the causal claim, tighten the wording, then change `status` to active
> or delete. The engine drafts; you decide.

## The regularity (draft)
{c.draft}

## Supporting cases
{chr(10).join(f'- [[{m}]]' for m in c.members)}

## Shared signal
- tags: {', '.join(c.shared_tags) or '—'}
- terms: {', '.join(c.top_terms[:6])}
- outcomes: {', '.join(f'{k}:{v}' for k, v in c.outcomes.items())}

## Does this rise to a Theory?
<If it makes a causal claim, promote to a T- note and run a contradiction search.>
"""
    out = config.VAULT_PATH / "400-Knowledge" / "Patterns" / f"{pid}.md"
    out.write_text(content, encoding="utf-8")
    return out, pid


if __name__ == "__main__":
    import sys
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    cands = synthesize(use_ollama="--ollama" in sys.argv)
    print(f"{len(cands)} candidate pattern(s) synthesized from case studies:\n")
    for i, c in enumerate(cands, 1):
        tag = "NEW" if c.novelty == "new" else f"covered by {c.existing_pattern}"
        print(f"[{i}] ({tag}) members: {', '.join(c.companies)}")
        print(f"    shared tags: {c.shared_tags or '—'} | themes: {c.top_terms[:5]}")
        print(f"    draft: {c.draft}\n")
