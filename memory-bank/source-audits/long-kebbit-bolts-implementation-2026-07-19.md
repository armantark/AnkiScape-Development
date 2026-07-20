# Long kebbit bolts implementation — 2026-07-19

Status: **implemented as an isolated source-ready reward chain; acquisition
remains source-blocked**.  
Cutoff: `2012-11-20T00:00:00Z`.

## Period and executable evidence

RuneScape Wiki `Hunter`, oldid `6484443`, timestamp
`2012-10-27T06:44:39Z`, states that one Long kebbit spike becomes six Long
kebbit bolts either through Leon for 40 coins or by using a Chisel.

Darkan commit `ec4eaba61955a691457a4a410dc21e314b4d6b0a` restores the
executable Fletching row:

- `Fletching.java:185-187` identifies Long kebbit spike `10107`, Chisel
  `1755`, Long kebbit bolts `10159`, Fletching 42, and `1.33` XP per bolt;
- `Fletching.java:485-518` consumes one spike, preserves the Chisel, and
  produces six bolts; and
- `QuestProbe.java:3908-3909` independently repeats the item identities,
  level, and per-bolt XP.

The restored runtime constant at `Fletching.java:51` and
`QuestProbe.java:4015-4030` says `7.89` XP. That conflicts arithmetically with
the same source's six outputs at `1.33` XP each. AnkiScape uses the internally
consistent `7.98` total and records the transposition rather than silently
copying it.

The rev-742-lineage cache record in
`pre-eoc-source-verification-standard.md` confirms Long kebbit spike `10107`
with a `Craft` option. The Darkan equipment generator identifies Long kebbit
bolts as ammunition requiring Ranged 42 with `+38` Ranged Strength.

## Implemented behavior

### Fletching

`fletch_long_kebbit_bolts` is a level-42 Bolts target:

- one Long kebbit spike is consumed;
- one carried Chisel is required and preserved;
- six Long kebbit bolts are produced;
- `7.98` Fletching XP is awarded; and
- the complete inventory, XP, telemetry, and target state participates in
  ordinary answer undo.

The generic target metadata and runtime error paths now distinguish consumed
materials from reusable required tools. The quest-item overlay also preserves
existing item identity fields, so the Chisel remains non-stackable instead of
losing that fact when a quest catalog row supplies newer provenance.

### Leon

Leon is a visible Yanille Shop provider. His batchable, instantaneous service
consumes one Long kebbit spike and 40 Coins per selected unit, produces six
Long kebbit bolts, awards no Fletching XP, does not advance the review-driven
shop market clock, and records a separately undoable direct event. The
quantity preview clamps atomically to both carried spikes and Coins.

The shared Shop service row now presents the complete transformation, plain
owned/needed counts, and explicit batch controls. Vendor actions remain
single-use; batchability is data-owned rather than inferred from a hard-coded
Bogrog action type.

### Equipment, Exchange, and assets

Long kebbit bolts are registered as period ammunition. The period Exchange
continuation adds:

| Item | Price | Four-hour limit | Page oldid | Revision timestamp |
|---|---:|---:|---:|---|
| Long kebbit bolts | 392 | 1,000 | 6562614 | 2012-11-16T04:14:14Z |
| Long kebbit spike | 2,070 | 5,000 | 6570835 | 2012-11-18T04:24:48Z |

The generated period maps now contain 1,330 direct prices and 1,640 limits
across 1,659 registered items.

Canonical sprites live at
`fletcheditems/long_kebbit_spike.png` and
`fletcheditems/long_kebbit_bolts.png`; both have tight RGBA alpha bounds and
their provenance is recorded in `assets_provenance.json`.

## UI review

The real Fletching panel and the real Leon Shop-provider panel were rendered
from the production Qt builders after `show()`, resize, and repeated event
processing at the laptop-height `1040×560` boundary.

Fable and Kimi K3 independently reviewed every new surface. Their confirmed
findings were applied:

- use an imperative Fletching label;
- show the reusable Chisel in the target tooltip;
- expose batchability through service metadata;
- remove duplicated provider and developer-taxonomy copy;
- show `input + price → output` in the service row;
- use `×` and `→` rather than programmer-style separators;
- spell out owned and needed quantities; and
- preserve an updating batch-total confirmation.

Both final reviews returned `PASS`.

## Verification and honest boundary

- Focused data, pure logic, runtime, registry, metadata, integration, Shop,
  and real-Qt regressions pass.
- Complete non-Qt discovery: 1,838 tests, 235 expected environment skips,
  zero failures or errors.
- Complete real offscreen-Qt discovery: 1,838 tests, one intentional skip,
  zero failures or errors.
- Test-quality audit: 1,838 tests across 78 files, zero hard issues; five
  structural-clone groups remain review-only.
- Documentation, compile, JSON, diff, and worktree checks pass.
- Reachability now models Leon's conversion explicitly: 1,268 actions, 1,889
  reachable items, 284 orphan inputs, and 302 blocked actions.
- A fully quit and freshly relaunched macOS Anki process opened exactly one
  AnkiScape dialog. Live Shop search found Leon, the provider panel rendered
  the complete conversion with the missing-spike state and a disabled Use
  button, and closing the dialog returned cleanly to the deck screen without
  invoking a service or review action.

Razor-backed kebbit tracking is still not live because its hidden catch and
trail behavior remains source-blocked. Long kebbit spike therefore remains an
honest orphan input consumed by both the Fletching target and Leon service.
The isolated, fully sourced transformations are visible and naturally
material-starved; no free seed item or invented acquisition was added.

No creative-design gap emerged.

Results:

- `memory-bank/status-updates/long-kebbit-bolts-results-2026-07-19.html`
- <https://jgg95o5s47si.postplan.dev>

Codex Workflows run `eda54f5b-37c2-49a0-8e9f-e0cd9d7edae8`
never established a provider session: its single read-only Sol-high leaf
remained at `session_id=null` with zero tokens and zero tool calls until the
primary canceled it. The primary independently reproduced the complete
source, code, and verification findings; no leaf claim was used.
