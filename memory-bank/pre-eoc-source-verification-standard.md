# Pre-EOC Source Verification Standard

Effective 2026-07-10. This is the permanent evidence contract for all existing
and future AnkiScape parity work: skills, quests, activities/minigames, targets,
items, transformations, shops, rewards, equipment, interfaces, unlocks, rates,
and migrations.

The existing 194-row quest catalog and its generated stage blockers establish
coverage scaffolding, not full quest fidelity. A quest can be present in the
catalog while still omitting authentic stages, branches, item transformations,
combat details, rewards, or unlocks. Every quest remains subject to this
standard during future parity passes, and may wait for high-fidelity Darkan
coverage when the historical pages cannot establish server behavior.

## Cutoff and Default Outcome

- Include only RuneScape behavior available before EOC on `2012-11-20`.
- Prefer the nearest useful November 2012 wiki revision. An adjacent older
  pre-EOC revision is acceptable when no November revision exists.
- If a concrete mechanic cannot be established from the evidence hierarchy,
  mark it `source_blocked`. Missing evidence is never permission to invent
  *content* — a target, item, reward, gate, or rate that the period record does
  not attest. Content stays blocked and waits.
- A `source_blocked` **hidden roll** is the one exception, and it is governed by
  the provisional-calibration rule below. A skill cannot ship without a success
  probability, and no period source states one for most skills, so "wait" would
  park the game indefinitely.
- The Darkan high-fidelity parity revamp is an acceptable dependency. Features
  that need its missing server behavior should remain parked rather than ship a
  plausible substitute.

`game-main` is an incomplete rev-667 snapshot, so a stub or omission there does
not prove that authentic pre-EOC content was absent. When a pinned wiki revision
before `2012-11-20` establishes the content, use `tools/wiki_parity.py` to resolve
and cite the `oldid`, then implement the independently established detail. Keep
unstated server rolls, timers, and hidden state `source_blocked` rather than
filling them from inference. A sourced action or recipe may ship naturally
input-starved when its authentic acquisition route is not modeled yet; do not
omit the content, invent a source, or add a substitute gate.

## Provisional Calibration of Blocked Rolls

Amended 2026-07-13 by owner decision. Applies only to a **hidden probability**
(a success roll, a catch chance, a multi-loot roll) — never to a level, XP
value, item, loot set, quest gate, timer, or any other value a period source
could have stated and did.

A blocked roll may be parameterized provisionally when all four hold:

1. The roll's *shape* is corroborated: at least two independent pre-EOC-lineage
   implementations agree on the functional form (for Thieving, both Darkan and
   game-main interpolate a low-level chance to a high-level chance across levels
   1-99 and roll against a fixed integer ceiling).
2. Every period-proven value around the roll ships exactly as attested. A
   provisional roll never licenses a provisional level, XP, or drop.
3. The parameters are pinned in the parity ledger as `provisional/<source>`,
   with the exact source recorded, so a later Darkan or cache find replaces a
   table rather than a design.
4. No value derived this way is ever described, in code, comments, docs, or UI,
   as historically closed.

### Two different jobs: supplying a value versus corroborating one

Keep these separate. Modern RuneScape may **corroborate** freely — a modern
table that matches an emulator's table row-for-row is real evidence about that
emulator, and costs nothing to consult. Modern RuneScape may **supply** a value
only as a last resort, below every period-lineage source. The distinction is
what lets a modern check improve a period answer without ever becoming one.

Worked example (Thieving, 2026-07-13): OSRS's published pickpocket endpoints
matched game-main's table exactly on eight independent rows and contradicted
Darkan's on nearly all of them. The shipped values are **game-main's**, at
tier 3 — OSRS supplied nothing. What it supplied was the proof that game-main's
table is the trustworthy one and Darkan's is the invention.

### Value-supply order for a blocked roll

1. **Darkan, the caches, then game-main** — the ordinary search order above.
   A roll that any period-lineage source states is not a calibration problem.
2. **OSRS**, only where no period-lineage source has the row at all. OSRS forked
   from a 2007 live backup, so for a mechanic that existed by 2007 and was never
   reworked, its tables carry pre-EOC lineage — but check the target's OSRS
   introduction *and* its update history before trusting a row. Jagex's May 2024
   "Project Rebalance: Skilling" silently invalidated the Paladin, Gnome, and
   Hero rates; content OSRS added after the fork (Prifddinas elves, Keldagrim)
   never had period lineage at all.
3. **RS3**, last and hostile by default: the post-EOC reworks are precisely what
   the cutoff exists to exclude. Usable only to bound a value nothing else
   touches, and only with the conflict recorded.
4. **Estimation.** The floor. Reached only when no source at any tier — period,
   emulator, or modern — has an analogue, typically because the period mechanic
   was *positional* and AnkiScape has no location layer, so there is no number to
   find because the game never had one. This is a design decision, not a sourcing
   one. Record it in the audit's abstraction list as an explicit AnkiScape
   invention, name the owner decision that authorized it, and keep the invention
   as small as it can possibly be: prefer one global constant applied by a
   sourced rule over a table of fabricated per-row values.

## Evidence Hierarchy

The hierarchy has two axes, and they are not the same thing. **Search order**
says where to look first for a mechanic. **Corroboration** says what a value
must still pass before it ships. Server behavior — rolls, timers, hidden state,
loot weights — is almost never stated by the wiki, so hunting for it there first
wastes the pass and tempts a fabricated reading of prose that never claimed the
number. Go to the implementations first, then prove what you found.

### Search order (owner-set)

1. **Darkan.** The high-fidelity Nov-2012 restoration is the primary
   reconstruction of server behavior. Record the exact path and commit.
2. **The rev-727 cache.** Darkan's own cache base, so it is the configuration
   layer that pairs with Darkan's code: names, IDs, options, varbits, CS2,
   interfaces.
3. **game-main (2011Scape, rev 667).** Independent implementation evidence;
   valuable precisely because it was reconstructed separately from Darkan, so
   agreement between the two is real corroboration and disagreement is a flag.
   The labels `game-main` and `2011Scape` identify the same local checkout, not
   two independent implementations.
4. **The remaining dated caches** (728, 729, 736, 741, 742). Use the newest for
   the closest-to-cutoff state, and the spread when a date of introduction or a
   configuration change matters.
5. **The RuneScape Wiki**, at a pinned pre-cutoff `oldid`.

### Corroboration gate (applies to every value, from any tier)

Finding a value first does not close it. Cross-corroborate against at least one
independent layer, and prefer a pinned pre-cutoff wiki revision as that check
wherever the wiki states the value at all. An emulator can invent: Darkan's
`pickDoor()` accumulates a `numbFingers` counter and hands out flat bonuses that
appear in no period source, and its `checkTrapsChest` ignores traps entirely
despite the name. Implementation evidence that survives no corroboration and
conflicts with the period record is a lead, not a fact.

Dated Wayback material stands in for the wiki where histories are missing or
moved, and for official guides and update posts.

Current RS3 pages, OSRS pages, and modern emulator commits locate questions and
candidate values. They never independently close parity.

No single source proves more than it contains. In particular, cache item
existence does not prove obtainable gameplay, and wiki prose does not prove a
hidden probability it never states.

## RuneScape Wiki Procedure

For every concrete value or gate:

1. Find the nearest relevant revision strictly before `2012-11-20T00:00:00Z`.
2. Record page title, oldid, and UTC timestamp.
3. Inspect literal article wikitext—not merely the rendered `?oldid=` page.
4. Trace templates, calculators, exchange calls, inline tables, modules, and
   subpages to their own historical revisions. If that dependency is missing,
   mark the value unresolved or use a dated Wayback capture.
5. Cross-check surprising or implementation-critical values against a second
   independent period source or the appropriate dated cache/config.
6. Record conflicts explicitly; do not silently choose the convenient value.

## Dated OpenRS2 Cache Set

The archives are read-only research inputs under
`/Users/ArmanTarkhanian1/Library/Caches/codex/2012scape-openrs2/`:

- rev 727 — 2012-07-24 — `runescape-727-2012-07-24-openrs2-309-disk.zip` — SHA-256 `ba79072542d1bda4d8140be38839b540133e79bc40c80665ef1772be178b29f8`
- rev 728 — 2012-08-01 — `runescape-728-2012-08-01-openrs2-310-disk.zip` — SHA-256 `7cbddfea4df57307e6a427fd1a27922062d45896eaf1ce4c2080ece888b4e936`
- rev 729 — 2012-08-11 — `runescape-729-2012-08-11-openrs2-311-disk.zip` — SHA-256 `bb492440353b6ec6a60faca6ac63ec1153de970505ee504101e5c8305ffd555f`
- rev 736 — 2012-10-09 — `runescape-736-2012-10-09-openrs2-313-disk.zip` — SHA-256 `68c5deaed6b5eb97e97df0f9e4c16d8728289ba5ccf1dba13b2e0a4131ef264d`
- rev 741 — 2012-11-04 — `runescape-741-2012-11-04-openrs2-1468-disk.zip` — SHA-256 `61855e4c9f18e5ae25124277506c5b4d24317caf96f8e0a5cd1b06a037db7180`
- rev 742 — 2012-11-07 — `runescape-742-2012-11-07-openrs2-544-disk.zip` — SHA-256 `9f5fdba0d22cdc1b4ad86c984cc0ba4bcd4b3c22039f3290ba48f5083bc100b8`

Use the newest relevant cache for the closest-to-cutoff state and compare
earlier builds when the date of introduction or configuration change matters.
The latest available cache predates EOC by thirteen days, so it cannot prove a
change made from November 8 through November 19.

**rev 727 is Darkan's own cache base.** Darkan agreeing with 727 therefore
corroborates nothing on its own — it is one source, counted twice. Corroborate
against 742 first.

Each archive is also **extracted in place**, so queries do not pay a ~500 MB
unzip on every lookup (2 seconds against an extracted cache versus roughly a
minute against a zip):

```
~/Library/Caches/codex/2012scape-openrs2/extracted/<rev>-<date>/cache/
```

for example `extracted/742-2012-11-07/cache/`. The zips are kept alongside them
as the immutable originals the SHA-256s above attest to; the extracted trees are
disposable and can be regenerated with `unzip -q <zip> -d extracted/<rev>-<date>`.

A cache proves what the *client* shipped: object, NPC, and item identities,
names, interaction options, interface definitions, and client-owned CS2
behavior in a given build. It can directly supply those client facts. It cannot
prove XP, rolls, timers, or any other server-side value, for which it remains
corroboration only.

Four tools read definitions and interfaces. `tools/query_openrs2_cache.sh`
searches **item** definitions;
`tools/query_openrs2_cache_definitions.sh <cache> <npc|object>` searches **NPC
and object** definitions, while its `--id` and `--params` modes print exact rows
and deterministic client parameters; and
`tools/query_openrs2_cache_configs.sh <cache> <enum|struct|param>` counts, dumps,
or searches the corresponding client configuration definitions.
`tools/query_openrs2_interfaces.sh` counts, dumps, and searches index-3 client
interface components. All four accept either a zip or an extracted cache
directory and never modify it.

For interface arithmetic, displayed formats, rounding rules, and tooltip
thresholds, inspect the relevant CS2 with
`tools/OpenRs2Cs2Disassembler.java` before classifying a value as
`source_blocked` or `provisional/<emulator>`. Rev 727 is the only local build
that decodes symbolically because Jagex renumbered the opcode table in later
builds; confirm later revisions structurally through hook bytes, script length,
and constant offsets. `source-audits/ge-offer-price-controls-2026-07-24.md`
records the worked interface-105/script-4112/varc-85 example and the boundary
between client-owned evidence and unrecoverable server behavior.

The config reader is verified against all seven dated caches, including exact
rev-727 enum, struct, and param fixtures. Cache configuration still proves only
client-shipped data; a numeric row is not evidence of a server mechanic merely
because it is readable. All six caches consistently
contain ammo mould with `Add-to-toolbelt` (4), rabbit snare with `Lay` (10031),
and overload (3) with `Drink`/`Empty` (15333), while none contains an item named
javelin head. The broader rev-742 proof pass confirmed period client definitions
for cannonball (2), ammo mould with `Add-to-toolbelt`
(4), Goldsmith gauntlets (776), ordinary and poisoned bronze-rune javelins
(825-836 and 5642-5653), raw/cooked/poison karambwan (3142/3144/3146), rabbit
snare with `Lay` (10031), ferret with `Release` (10092), tatty/perfect pitfall
furs (10093-10104), long kebbit spike with `Craft` (10107), Grenwall spikes
(12539), overload doses (15332-15335), and related items. No javelin-head or
javelin-shaft definition was found, supporting—but not solely proving—the
historical wiki statement that javelins were not smithable/fletchable.

## Darkan and Implementation Gate

- Exclude every `src/main/java/com/rs/web/*AuditProbe.kt` file unconditionally.
  These files are audit instrumentation, not period evidence, regardless of
  their date.
- For every other Darkan file, inspect `git log -- <path>` and record the exact
  path and supplying commit. A date cutoff is not a provenance test: upstream
  files may have recent refactors, while restoration commits are unit-scoped.
- Where the Darkan restoration has frozen a unit contract under
  `memory-bank/audit/reports/`, that contract is authoritative for what the
  sources prove, what is inference, and what remains deferred. Read it instead
  of inferring provenance from a source path.
- Determine whether candidate behavior is original Darkan material, a later
  reconstruction, or a stub. Repository branding or a 2012 cache base is not
  sufficient.
- Reconcile every user-visible requirement, formula, roll, output, failure,
  timer, and side effect with the historical evidence.
- If Darkan is incomplete or conflicts with the period record, wait for its
  high-fidelity work or implement only the independently proven subset.

## Wiki Section Provenance

A revision timestamp dates the page, not every sentence on it. Record the
section that supplies each claim. Treat Trivia, update-history, scam, exploit,
and glitch material as historical or unclear unless an independent live-period
source proves otherwise. Check page-level markers such as `{{beta}}`; an
otherwise in-period revision may still describe beta content and require a
second oldid or independent corroboration.

## Search Discipline and Negative Results

A negative search result is not evidence of absence until the same probe has
passed a positive control. Before acting on a miss, use the same command,
parameters, parser, path depth, and data-access method to find something known to
exist. Until then, state only: "my search with these parameters did not find it."
A clean false negative is more dangerous than an explicit error because it invites
a decision instead of a retry.

A search can also fail by finding a hit and stopping rather than finding the hit.
Before reading the first match as the answer, check whether more than one row can
satisfy the predicate. This caught a Dragon impling drop table that contained both
finished-ammunition and component rows for the same conceptual items: the first
match was real but wrong, while the correct Dragon arrowheads row sat four entries
away. Positive controls guard probes that cannot hit; multiplicity checks guard
probes that hit too easily. Either rule alone leaves a gap.

This rule was added after seven false negatives in one day:

- a reachability query requested the nonexistent `reachable_items` key, so an
  empty set briefly looked like lost reachability;
- a quest-combat query used `getattr` only, missed dict-form
  `guaranteed_drops`, and falsely reported zero guaranteed drops across 294
  encounters when the investigated item was present;
- `git branch --list '*wyvern*' '*bone*'` could not match an existing duplicate
  on a branch named `breadth`;
- a wiki search used `5,000` where the page wrote `5000`;
- a Gradle probe passed `-Pdarkan.cache.path` while the build reads
  `darkanCachePath`;
- `find -maxdepth 6` searched for a file at depth eight; and
- an unquoted path containing `2012scape with bots` resolved to a plausible but
  unrelated sibling tree instead of the intended Darkan checkout.

## Required Audit Record

Every implemented parity family should leave a durable source audit containing:

- scope and cutoff;
- page title, oldid, and timestamp for each historical claim;
- cache build and IDs/options used for cross-reference;
- exact item model/recolour/bonus rows may be reproduced with
  `tools/query_openrs2_cache.sh <cache> --id <id> [id ...]`;
- exact NPC combat levels may be reproduced with
  `tools/query_openrs2_cache_definitions.sh <cache> npc --combat-levels <id> [id ...]`;
- local source paths and commits;
- values proven, values intentionally abstracted by AnkiScape, and unresolved
  values left source-blocked;
- conflicts and their resolution; and
- tests mapping the implemented contract to the evidence.

## Breadth-Phase Placeholders

Amended `2026-07-25` by owner decision. This relaxes the rule above for one
purpose and one phase, and it expires when the breadth phase does.

The owner's goal is that every settled family reaches mechanical completion. The
rule above blocks that: content that needs an intense dig stays `source_blocked`
and waits, so a family with one unrecoverable number cannot ship at all, and
twenty-three families were parked behind exactly that.

A **placeholder** may now stand in for a value that would need an intense dig,
so the mechanic around it can ship complete. Four conditions hold, and the first
two are what stop a placeholder from quietly becoming canon:

1. **It is marked at the value.** The code carries
   `# PLACEHOLDER(<id>): <what would settle it>` on or above the line. The id is
   unique and stable.
2. **It is listed in `memory-bank/placeholder-values.md`**, with what the value
   is, what it blocks, and the specific evidence that would replace it.
   `tests/test_placeholder_register.py` fails if a marker is missing from the
   register or a register row names a marker that no longer exists, so the two
   cannot drift apart and a placeholder cannot hide.
3. **Everything around it still ships exactly as attested.** A placeholder never
   licenses a second one nearby, and never licenses inventing *content* — a
   target, item, reward or gate the period record does not attest. Those still
   wait.
4. **Nothing describes it as period-accurate**, in code, comments, docs or UI.

The distinction that matters, learned twice on the day this was written: a
placeholder is a value the period had and we could not recover. An invention is a
value the period did not have. The Daily Challenges reroll and the Fish Flingers
weight were inventions, and both survived review because they were written up as
though settled. A placeholder is honest about being temporary. An invention
pretends to be finished.
