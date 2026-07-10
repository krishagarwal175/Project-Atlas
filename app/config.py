"""Central configuration for Atlas — a Local-First Research Operating System.

Everything is local and free. No paid APIs, no cloud, no accounts. The markdown
`vault/` is the source of truth; this app builds only a *disposable* cache over it
(see ADR-001, ADR-003). Runs fully offline; the internet only enhances Market Intel.
"""
from __future__ import annotations
import os
from pathlib import Path

import paths as _paths

# All locations resolve through the path authority (paths.py) — application vs
# user-data separation, portable/installed modes, env overrides. No hardcoded paths.
PATHS = _paths.resolve()

# The markdown vault — source of truth (local-first). Honors ATLAS_VAULT.
VAULT_PATH = PATHS.vault

# RESERVED (not yet built): a disposable SQLite index over the vault. Deferred by
# design — parsing the whole vault live is sub-second at current scale (YAGNI).
# Lives in the user-data cache dir, never inside the executable. See ADR-002.
CACHE_DB = PATHS.cache / "cache.sqlite"

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
    "mental-model": None,     # timeless reasoning tools
    "company": 730,           # revisit company histories every ~2y
    "learning-path": None,    # curated reading sequences
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
