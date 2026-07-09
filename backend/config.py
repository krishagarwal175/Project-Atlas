"""Central configuration for the Acredemia Research OS backend.

Everything is local and free. No paid APIs. The vault is the source of truth;
this backend builds a *disposable* SQLite cache over it (see ADR-001).
"""
from __future__ import annotations
import os
from pathlib import Path

# Vault path: sibling folder by default, overridable via env var.
VAULT_PATH = Path(
    os.environ.get(
        "ACREDEMIA_VAULT",
        str(Path(__file__).resolve().parent.parent / "Acredemia-Vault"),
    )
)

# RESERVED (not yet built): a disposable SQLite index over the vault. Deferred by
# design — parsing the whole vault live is sub-second at current scale (YAGNI).
# Build this only when parse latency becomes a real, measured problem. See the
# Architecture Freeze (ADR-002) "deferred, on purpose" note.
CACHE_DB = Path(__file__).resolve().parent / "cache.sqlite"

# Folders/files ignored by the parser.
IGNORE_DIRS = {".obsidian", ".git", ".trash"}
IGNORE_NOTE_TYPES = {"placeholder"}

# Note types that are structural (never flagged as orphans / untagged).
STRUCTURAL_TYPES = {"moc", "governance", "template", "project", "adr", "dna", "placeholder"}

# Freshness half-lives in days, per note type. Used by the decay engine.
# None = does not decay on a clock (only on new contradicting evidence).
HALF_LIFE_DAYS = {
    "market-signal": 90,
    "market-report": 90,
    "competitor": 180,
    "case-study": 730,
    "framework": 1825,
    "assumption": 180,
    "observation": 365,
    "theory": None,
    "lesson": None,
    "decision": None,
    "question": None,
}
DEFAULT_HALF_LIFE = 365

# Confidence ladder (ordered).
CONFIDENCE_LADDER = ["speculative", "emerging", "supported", "well-tested", "institutional"]

# Market Intelligence: free, public RSS/Atom feeds (no paid APIs, no login-walls).
# Curate for ed-tech / hiring / startup relevance. Edit freely.
RSS_FEEDS = [
    ("TechCrunch", "https://techcrunch.com/feed/"),
    ("TechCrunch Startups", "https://techcrunch.com/category/startups/feed/"),
    ("YC Blog", "https://www.ycombinator.com/blog/rss"),
    ("EdSurge", "https://www.edsurge.com/articles_rss"),
    ("VentureBeat", "https://venturebeat.com/feed/"),
]

# --- Decision Engine (Phase 2) -------------------------------------------
# Dimensions and their direction. "+" = higher is better; "-" = higher is worse
# (cost/risk/effort/time are inverted before weighting). This lives in config
# (not code) so the weighting scheme is editable data, not a redeploy.
DECISION_DIMENSIONS = {
    "impact":     "+",
    "confidence": "+",
    "alignment":  "+",
    "cost":       "-",
    "risk":       "-",
    "effort":     "-",
    "time":       "-",
}

# Weight presets per decision type. Weights need not sum to 1; they are
# normalized at compute time. Editable freely.
WEIGHT_PRESETS = {
    "default": {"impact": 3, "confidence": 2, "alignment": 2,
                "cost": 2, "risk": 2, "effort": 1, "time": 1},
    "channel-choice": {"impact": 3, "confidence": 1, "alignment": 1,
                       "cost": 3, "risk": 2, "effort": 1, "time": 3},
    "feature-build": {"impact": 3, "confidence": 2, "alignment": 3,
                      "cost": 1, "risk": 2, "effort": 3, "time": 1},
    "pricing": {"impact": 3, "confidence": 2, "alignment": 3,
                "cost": 1, "risk": 3, "effort": 1, "time": 1},
}

# Sensitivity: perturb the winner's scores by this fraction; if the ranking
# flips, flag the decision "fragile" and name the responsible dimension.
SENSITIVITY_DELTA = 0.20

# Relevance routing thresholds (keyword-overlap based; deterministic).
RELEVANCE_MIN_KEYWORDS = 1     # >=1 keyword hit => at least 'log'
RELEVANCE_FLAG_KEYWORDS = 2    # >=2 keyword hits => 'flag-for-review'
