"""Retrieval (Module 3) — semantic/keyword search over the whole vault.

Tiered by what's installed, so it works today and improves if you add models:
  1. sentence-transformers (local embeddings)  — best, offline, ~80MB model
  2. scikit-learn TF-IDF cosine                — good, installed now
  3. pure-Python keyword overlap               — always works, zero deps

Results are confidence- and freshness-aware: every hit shows its epistemic
state so you never cite stale or weak knowledge unknowingly.
"""
from __future__ import annotations
import math
import re
from dataclasses import dataclass

from vault import Note, load_vault

# --- optional backends, probed once ---------------------------------------
_EMBED = None
_SKLEARN = None
try:  # pragma: no cover
    from sentence_transformers import SentenceTransformer  # type: ignore
    _EMBED = "available"
except Exception:
    _EMBED = None
try:
    from sklearn.feature_extraction.text import TfidfVectorizer  # type: ignore
    from sklearn.metrics.pairwise import cosine_similarity  # type: ignore
    import numpy as np  # type: ignore
    _SKLEARN = "available"
except Exception:
    _SKLEARN = None

_WORD_RE = re.compile(r"[a-z0-9]+")


@dataclass
class Hit:
    note: str
    title: str
    type: str
    score: float
    confidence: str
    freshness: str
    snippet: str


def _doc_text(n: Note) -> str:
    tags = n.frontmatter.get("tags") or []
    tagtext = " ".join(str(t) for t in tags) if isinstance(tags, list) else str(tags)
    return f"{n.title}\n{n.title}\n{tagtext}\n{n.body}"


def _snippet(body: str, query: str, width: int = 160) -> str:
    words = set(_WORD_RE.findall(query.lower()))
    low = body.lower()
    pos = -1
    for w in words:
        pos = low.find(w)
        if pos != -1:
            break
    if pos == -1:
        text = body.strip().replace("\n", " ")
        return text[:width] + ("…" if len(text) > width else "")
    start = max(0, pos - width // 3)
    text = body[start:start + width].replace("\n", " ").strip()
    return ("…" if start > 0 else "") + text + "…"


class SearchEngine:
    def __init__(self, notes: list[Note] | None = None):
        self.notes = notes or load_vault()
        # exclude pure scaffolding from the search corpus
        self.corpus_notes = [n for n in self.notes if n.type not in ("template",)
                             and n.filename.lower() != "readme"
                             and "/Reviews/" not in f"/{n.rel_path}"]
        self.backend = "keyword"
        self._model = None
        self._matrix = None
        self._vectorizer = None
        self._emb = None
        self._build()

    def _build(self):
        docs = [_doc_text(n) for n in self.corpus_notes]
        if _EMBED:
            try:
                self._model = SentenceTransformer("all-MiniLM-L6-v2")
                self._emb = self._model.encode(docs, normalize_embeddings=True)
                self.backend = "embeddings"
                return
            except Exception:
                pass
        if _SKLEARN:
            self._vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
            self._matrix = self._vectorizer.fit_transform(docs)
            self.backend = "tfidf"
            return
        self.backend = "keyword"

    def search(self, query: str, k: int = 8) -> list[Hit]:
        if self.backend == "embeddings":
            qv = self._model.encode([query], normalize_embeddings=True)
            scores = (self._emb @ qv[0])
        elif self.backend == "tfidf":
            qv = self._vectorizer.transform([query])
            scores = cosine_similarity(qv, self._matrix)[0]
        else:
            scores = self._keyword_scores(query)

        ranked = sorted(range(len(self.corpus_notes)), key=lambda i: -scores[i])
        hits: list[Hit] = []
        for i in ranked[:k]:
            s = float(scores[i])
            if s <= 0:
                continue
            n = self.corpus_notes[i]
            hits.append(Hit(
                note=n.filename, title=n.title, type=n.type, score=round(s, 4),
                confidence=n.confidence_state or "-", freshness=n.freshness or "-",
                snippet=_snippet(n.body, query),
            ))
        return hits

    def _keyword_scores(self, query: str) -> list[float]:
        qwords = set(_WORD_RE.findall(query.lower()))
        scores = []
        for n in self.corpus_notes:
            dwords = _WORD_RE.findall(_doc_text(n).lower())
            if not dwords:
                scores.append(0.0)
                continue
            dset = set(dwords)
            overlap = qwords & dset
            tf = sum(dwords.count(w) for w in overlap)
            scores.append(len(overlap) + 0.1 * math.log1p(tf))
        return scores


if __name__ == "__main__":
    import sys
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    eng = SearchEngine()
    print(f"Search backend: {eng.backend}  |  corpus: {len(eng.corpus_notes)} notes\n")
    q = " ".join(sys.argv[1:]) or "referral program virality growth"
    print(f"Query: {q!r}\n")
    for h in eng.search(q):
        print(f"  {h.score:6.3f}  [{h.type:12}] {h.title}")
        print(f"          conf={h.confidence} fresh={h.freshness} :: {h.snippet[:110]}")
