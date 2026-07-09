# Atlas Design System — "Command Surface"

> One design language for the whole application. Every screen is composed from these
> tokens and primitives — never designed independently. If a screen needs something
> the system doesn't have, extend the *system* first, then use it.

The canonical token values live in [`ui/tokens.css`](../ui/tokens.css). This document is
the specification; `tokens.css` is the source of truth the UI consumes.

---

## 0. Design philosophy — "calm instrument"
Atlas is an instrument you live in for years, not a website you visit. The aesthetic is a
**dark technical command surface**: charcoal structure, one decisive red for action and
identity, and two sharp signal colors (neon green / neon red) reserved for *epistemic
state* — confidence, drift, risk. Color is meaning, never decoration. The interface is
quiet until something needs you; motion is fast and physical; density is high but ordered.
Feels like Linear × Obsidian × a trading terminal.

Three rules that resolve every judgment call:
1. **Structure over ornament.** Hairline borders and a strict grid do the work; no soft shadows-as-decoration, no gradients-as-filler.
2. **Color is a signal budget.** Red = action/identity. Green = positive epistemic state. Neon-red = negative/critical. Everything else is charcoal + ink. Spend signal color sparingly.
3. **Calm by default, sharp on demand.** Resting state is muted; interaction (hover/focus/active) is where the accent and motion appear.

---

## 1. Color tokens
Two layers: a **primitive palette** (raw values) and **semantic tokens** (intent). UI code
uses semantic tokens only.

### Primitive palette
| token | value | note |
|---|---|---|
| `--charcoal-950` | `#0b0c0e` | app base |
| `--charcoal-900` | `#141519` | panel |
| `--charcoal-850` | `#1b1d22` | raised panel / inputs |
| `--charcoal-800` | `#23252b` | hover surface |
| `--ink-100` | `#ededf0` | primary text |
| `--ink-400` | `#8b8e96` | muted text / meta |
| `--red-500` | `#ff443a` | brand / action |
| `--red-600` | `#ff5b52` | action hover |
| `--red-950` | `#3a1416` | red-tint surface |
| `--neon-green` | `#46ffa0` | positive signal |
| `--neon-red` | `#ff2d55` | negative signal |
| `--amber` | `#ff7a3d` | caution signal |

### Semantic tokens (use these)
| token | maps to | meaning |
|---|---|---|
| `--surface-0/1/2/3` | charcoal 950→800 | elevation layers |
| `--ink / --ink-muted` | ink 100 / 400 | text hierarchy |
| `--accent / --accent-hover / --accent-tint` | red 500/600/950 | action + brand identity |
| `--signal-pos` | neon-green | supported/on-track/up |
| `--signal-neg` | neon-red | contested/drift/critical/down |
| `--signal-warn` | amber | at-risk/fragile |
| `--border / --border-strong` | white @ 8% / 16% | hairlines |
| `--focus-ring` | red @ 40% | keyboard focus |

Signal-color mapping is **fixed** across the app: confidence `supported+` → `--signal-pos`;
`contested`/drift/`fragile-neg` → `--signal-neg`; `at-risk`/warn → `--signal-warn`.

---

## 2. Typography scale
- **Sans (UI/body):** system stack — `-apple-system, "Segoe UI", Roboto, Helvetica, Arial`. Chosen for **offline-first** (no web-font fetch; renders instantly, no network dependency — invariant I12).
- **Mono (meta/data/labels):** `"JetBrains Mono", ui-monospace, "SF Mono", Consolas, monospace`. Used for metadata, IDs, counts, section labels, code — the "technical layer."

Scale (1.20 ratio, rounded to px):
| token | size / line-height | use |
|---|---|---|
| `--text-2xs` | 10 / 14 | mono labels, chips |
| `--text-xs` | 11 / 16 | meta, captions |
| `--text-sm` | 13 / 20 | secondary body, tables |
| `--text-md` | 14 / 22 | body (default) |
| `--text-lg` | 17 / 24 | card/pane titles |
| `--text-xl` | 22 / 28 | section headers |
| `--text-2xl` | 30 / 34 | stat numbers |
| `--text-3xl` | 44 / 46 | hero/empty-state display |
Weights: 400 body, 500 emphasis, 700 headings/buttons, 800 stat numbers. Section labels:
mono, `--text-2xs`, uppercase, `letter-spacing: .14em`.

---

## 3. Spacing scale (4px base)
`--space-1:4 · --space-2:8 · --space-3:12 · --space-4:16 · --space-5:24 · --space-6:32 · --space-7:48 · --space-8:64`.
Component padding uses 3–5; section rhythm uses 5–7. Never use off-scale values.

---

## 4. Radius & elevation
- Radius: `--radius-0:0 · --radius-sm:6 · --radius-md:9 · --radius-lg:14`. Cards/inputs `md`; chips `sm`; the app frame `0` (edge-to-edge desktop feel).
- Elevation is **border-first, shadow-second**. `--elev-1` (hairline only), `--elev-2` (hairline + `0 10px 30px rgba(0,0,0,.35)` on hover/menus). Accent glow (`0 0 18px accent@35%`) is reserved for the primary action and live status dots — never ambient.

---

## 5. Motion system
Physical, fast, purposeful. Durations: `--dur-1:120ms` (hover/press), `--dur-2:220ms` (enter/expand), `--dur-3:420ms` (view transitions). Easings: `--ease-out: cubic-bezier(.16,1,.3,1)` (default, decelerate), `--ease-inout: cubic-bezier(.65,0,.35,1)` (moves). Patterns:
- **Enter:** opacity 0→1 + translateY(8px)→0, `--dur-2 --ease-out`, stagger 60ms.
- **Press:** scale .98, `--dur-1`. **Hover:** border→accent-tint + `--dur-1`.
- **Count-up** for numeric stats (cubic ease, ≤1.4s).
- `prefers-reduced-motion` → all transitions collapse to instant, no translate/scale.

---

## 6. Component primitives
Each is a class in `ui/tokens.css` / the UI, built from tokens only:
`.btn` (+`.btn-primary` red, `.btn-ghost`), `.card` / `.pane` (hairline, hover-lift),
`.field` (input/select/textarea, red focus ring), `.chip` (+`.chip-pos/-neg/-warn`),
`.stat` (label + big number + accent underline), `.meter` (progress; color by state),
`.table` (dense, hairline rows), `.label-mono` (section label), `.kbd` (key hint),
`.dot` (live status; `.ok`=green glow). Primitives never hardcode color/size — tokens only.

---

## 7. Interaction principles
- **Keyboard-first.** Everything reachable by keyboard; a command surface (`⌘/Ctrl-K`-ready) is the intended primary navigation (extension point, not built yet).
- **Immediate feedback.** Every action has a ≤120ms visual response.
- **Local & reversible.** Destructive actions confirm inline; nothing leaves the machine silently.
- **Progressive density.** Resting cards show summary; hover/expand reveals data strings & provenance.
- **One primary action per view**, rendered in `--accent`. Secondary actions are ghost.

---

## 8. Accessibility rules
- **Contrast:** body text ≥ 4.5:1 on its surface; large/mono meta ≥ 3:1. (`--ink` on `--surface-0/1` passes; `--ink-muted` is for ≥`--text-xs` only.)
- **Focus:** always-visible `--focus-ring` (never `outline:none` without a replacement).
- **Motion:** honor `prefers-reduced-motion`.
- **Color is never the only signal:** pair signal colors with a glyph/label (e.g. `⚑ contested`, `▲/▼`), so state survives color-blindness and grayscale.
- **Targets** ≥ 28px; **hit area** ≥ 32px for primary controls.

---

## 9. Iconography
- **Inline SVG, stroke-based**, 1.5px stroke, 16/20/24px sizes, `currentColor`. No icon fonts, no external sprite (offline-first). A small local set in `assets/icons/` (extension point for more).
- Emoji are allowed only as **section affordances** in labels, never as functional controls.

---

## 10. Layout grids & workspace
- **App frame:** full-bleed, `--radius-0`, no browser chrome. Regions: **Title/status bar** (top, hairline-bottom, red identity mark + live `--dot`), **Sidebar/rail** (left, navigation — extension point), **Workspace** (content, 12-col fluid grid, `--space-4` gutters), optional **Inspector** (right, contextual).
- **Content grid:** responsive `1fr` (mobile) → `2-col` (≥900px) card grid; dense data panels use their own sub-grids (e.g. 7-col decision-score row).
- **Density:** comfortable default; a future compact mode toggles spacing scale down one step (extension point).

---

## 11. Workspace philosophy
Atlas is a **single-window, multi-pane operating environment**, not a set of pages. You
open it and stay; panes update in place. No tabs-as-navigation, no page reloads, no
spinners for local work (local reads are instant). The morning "brief" is the home pane;
everything else is one keystroke away. It should feel like an instrument on your desk that
is *always warm* — quiet, fast, and entirely yours.

---

## 12. Governance of the system
- Changes to tokens/primitives are **design-system-level** and get a note in the changelog.
- A screen may not introduce a raw hex value, off-scale spacing, or a bespoke motion curve —
  it extends this system instead. This keeps ten years of screens coherent.
