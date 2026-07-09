# Acredemia Research OS — Vault

This folder is an **Obsidian vault** and the **source of truth** for Acredemia's Research Operating System. Open it in [Obsidian](https://obsidian.md) (free).

## First run
1. Open Obsidian → "Open folder as vault" → select this folder.
2. Install community plugins (free, local): **Dataview**, **Templater**, **Obsidian Git**.
3. Point Templater's template folder at `900-Meta/Templates/`.
4. Start at [[Home]].

## Structure
- `000-Index` entry points / MOCs · `100-Project` building this · `200-Product` spec · `300-Architecture` + ADRs
- `350-Questions` first-class strategic questions · `400-Knowledge` case-studies/patterns/theories/contradictions/frameworks/assumptions
- `500-Acredemia` company memory + Strategic-DNA · `600-Decisions` strategic memory · `700-Market-Signals` ambient intel · `900-Meta` templates/governance

## Rules
- `type:` frontmatter is authoritative ([[Tag-Taxonomy]]).
- Claim-bearing notes carry `confidence-state`, `freshness`, `last-reviewed` ([[Vault-Governance]]).
- Atomic notes + `[[wikilinks]]`. No orphan notes.

`git init` this folder to get versioned history — it doubles as the audit trail.
