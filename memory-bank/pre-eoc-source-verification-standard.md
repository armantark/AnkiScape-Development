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
  mark it `source_blocked` and wait. Missing evidence is not permission to copy
  current RS3, OSRS, a modern calculator/template, or an emulator guess.
- The Darkan high-fidelity parity revamp is an acceptable dependency. Features
  that need its missing server behavior should remain parked rather than ship a
  plausible substitute.

## Evidence Hierarchy

1. **Literal pre-EOC RuneScape Wiki wikitext.** Resolve an exact `oldid`, verify
   its timestamp through the MediaWiki revisions API, and read `prop=wikitext`.
2. **Dated Wayback material.** Use it for official guides, update posts, pages
   with missing/moved histories, and transcluded dependencies whose oldids were
   not preserved.
3. **Period cache/configuration evidence.** Use the dated OpenRS2 caches for
   client-side identity and configuration: names and IDs, inventory/object/NPC
   options, models, sprites, interfaces, CS2 scripts, varbits, and evidence that
   an asset/config existed in that build.
4. **Snapshot implementation evidence.** The local 2011Scape source can prove
   unchanged rev-667 behavior. Fidelity-revamped Darkan can prove reconstructed
   server behavior only after it is reconciled with the historical layers.
5. **Research leads only.** Current RS3 pages, OSRS pages, and modern emulator
   commits may locate questions or candidate values. They cannot independently
   close parity.

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

`tools/query_openrs2_cache.sh` searches item definitions directly from one of
these zip files without modifying the archive. All six caches consistently
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

- Record the exact Darkan path and commit that supplies a candidate behavior.
- Determine whether it is original period material, a later reconstruction, or
  a stub. Repository branding or a 2012 cache base is not sufficient.
- Reconcile every user-visible requirement, formula, roll, output, failure,
  timer, and side effect with the historical evidence.
- If Darkan is incomplete or conflicts with the period record, wait for its
  high-fidelity work or implement only the independently proven subset.

## Required Audit Record

Every implemented parity family should leave a durable source audit containing:

- scope and cutoff;
- page title, oldid, and timestamp for each historical claim;
- cache build and IDs/options used for cross-reference;
- local source paths and commits;
- values proven, values intentionally abstracted by AnkiScape, and unresolved
  values left source-blocked;
- conflicts and their resolution; and
- tests mapping the implemented contract to the evidence.
