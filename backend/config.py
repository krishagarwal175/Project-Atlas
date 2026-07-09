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

# Disposable cache DB. Safe to delete; rebuilt from the vault.
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

# Relevance routing thresholds (keyword-overlap based; deterministic).
RELEVANCE_MIN_KEYWORDS = 1     # >=1 keyword hit => at least 'log'
RELEVANCE_FLAG_KEYWORDS = 2    # >=2 keyword hits => 'flag-for-review'
