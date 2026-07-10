---
type: governance
title: Tag-Taxonomy
updated: 2026-07-09
---

# Tag Taxonomy — controlled, to prevent tag rot

Tag sprawl is the #1 way vaults die. `type:` frontmatter is **authoritative**; tags are secondary and **faceted** (always `facet/value`).

## `type:` (authoritative — one per note)
**Active (have templates + instances):** `moc · governance · question · decision · experiment · case-study · pattern · theory · contradiction · observation · assumption · lesson · framework · mental-model · company · learning-path · competitor · market-signal · adr · dna · project · knowledge-review · template · placeholder`

**Reserved (defined, no template/instance yet — add a template before first use):** `decision-review · confidence-review · hypothesis · strategic-principle · market-report · meeting-note · postmortem`

Reference-library types (`framework · mental-model · company · learning-path · case-study`) are the **curated textbooks** (see [[📚 Knowledge-MOC]] · [[Knowledge-Expansion-Roadmap]]).

> `placeholder` = a `.folder-note.md` marking a reserved empty folder; ignored by the parser and governance.

## Faceted tags
- `domain/*` → `gtm · pricing · product · hiring · fundraising · marketing · community · verification · marketplace · partnerships · decision-science · growth · finance · strategy · software · research-methods · startup-history`
- `stage/*` → `idea · pre-seed · seed · growth`
- `scale/*` → `vision · mission · theme · objective · question · decision · experiment · project · task · observation · lesson · knowledge`
- `status/*` → `open · dormant · answered · reopened · proposed · active · concluded · reversed`
- `confidence/*` → `speculative · emerging · supported · well-tested · institutional`
- `freshness/*` → `fresh · aging · needs-review · stale · historical-only`

## Rules
1. New `type:` values require an edit to this file — no ad-hoc types.
2. Prefer `[[wikilinks]]` over tags for relationships; use tags only for faceted filtering.
3. `confidence/*` and `freshness/*` tags are **derived** — set by the bot, not hand-maintained (until the bot exists, mirror the frontmatter field).
