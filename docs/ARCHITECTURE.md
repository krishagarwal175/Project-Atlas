# Atlas — Architecture (pointer)

The authoritative architecture documents live **in the vault** (single source of truth,
so they never drift from the knowledge base they describe). This file is only a map.

| Topic | Location |
|-------|----------|
| System overview + module map | `vault/300-Architecture/System-Architecture.md` |
| Architecture Freeze + the 16 invariants | `ADR-002` + `ADR-003` under `vault/300-Architecture/Tech-Decisions/` |
| Vault-first substrate rationale | `ADR-001-markdown-substrate.md` |
| Local-First / single-user decision | `ADR-003-local-first-single-user.md` |
| Governance rules & audit checklist | `vault/900-Meta/Vault-Governance.md` |
| Tag taxonomy & note types | `vault/900-Meta/Tag-Taxonomy.md` |
| Roadmap | `vault/100-Project/Roadmap.md` |

## One-paragraph summary
Atlas is **local-first**: the markdown `vault/` is the source of truth; `app/` is a set of
deterministic engines (parser, search, decision, epistemics, synthesis, graph, market-intel,
governance) that read/write those files; `ui/` is a static local dashboard. Dependencies flow
one way (`config`/`vault` → engines → `api`/`cli` → UI), no cycles. AI is optional and local
only. Everything works offline except Market Intelligence, which merely enhances.
