---
name: ankiscape-skill-expansion
description: >-
  Guides AnkiScape skill and action-family expansions. Use when adding or
  expanding AnkiScape skills, Utility/Activities, item chains, target lists,
  achievements, pre-EOC parity audits, wiki/cache scraping, asset scraping, XP
  balancing, or gameplay settings.
---
# AnkiScape Skill Expansion

## Task Description

AnkiScape is an Anki add-on that turns successful card reviews into lightweight RuneScape-style game progress. A skill expansion is any change that adds or expands a skill, action family, Utility/Activity, target chain, item economy slice, achievement set, XP/batch balance rule, or gameplay setting.

Use this skill before planning or implementing a skill expansion. The goal is to avoid rediscovering the same workflow each time: audit the source data, choose a playable scope, add backend data and pure mechanics, fetch assets, expose the UI, add achievements, test the review loop, and update the memory bank.

## Non-Negotiables

- Split backend and frontend work explicitly.
- Target full RuneScape immediately before the Evolution of Combat, with a
  strict content cutoff of **2012-11-20**. Cite period evidence before claiming
  XP, levels, materials, outputs, unlocks, rolls, timers, or rates. Do not infer
  these from memory or from a modern implementation.
- Treat current RS3, OSRS, and modern emulator behavior as research leads only.
  They never prove pre-EOC parity without independent pre-cutoff evidence.
- Keep source data honest: preserve audited pre-EOC base XP in data, then apply
  AnkiScape pacing knobs separately.
- Preserve historical time limits through AnkiScape's global answered-card
  clock, not the wall clock: 10 answered cards equal one game hour and 240 equal
  one game day, matching NPC shops and the parked GE design. Daily/weekly charges
  reset on simulated-day boundaries without stacking, and shorter world events
  derive from the same clock. All answered cards advance time; undo must roll it
  back with the triggering review.
- The global clock governs background/world/economy timers and reset cadence;
  it does not turn every skilling review into six minutes of action. Skilling
  remains one sourced action tick per successful review unless that activity has
  an independently approved action grouping.
- Do not build standalone transportation systems or persistent player-location
  state. Canoes, hot-air balloons, lodestones, and comparable transport-only
  content are out of scope even when operating them incidentally awards skill
  XP. Abstract necessary travel inside the target or activity that needs it;
  travel friction may remain an internal action phase without becoming a map or
  a selectable transport network.
- Do not grill the owner on facts or behavior already determined by pinned
  period evidence and settled AnkiScape rules. Resolve and document those
  autonomously, batching routine source-shaped decisions. Ask only when two or
  more reasonable implementations would create a materially different player
  experience and the existing product contract does not choose between them.
- Use stable IDs for skills, recipes, targets, and items. Do not use display names as durable target identifiers when outputs can collide.
- Build source-backed content **fully and live by default**, wiring each target/action into the UI as a normal, functional entry that is **indistinguishable from every other entry** — even when its inputs cannot be obtained yet. Such content is not special: it is simply, *emergently* un-runnable right now because the player holds zero of a material whose acquisition route (a drop, market, another skill, or Utility/Activity) does not exist yet. That is the **exact same state** as any normal recipe whose materials you happen to lack (e.g. a sapphire ring when you hold zero sapphires).
  - **Do NOT** delete it, hide it, "coming soon" it, add a `locked until later` gate, or give it any distinct tag, label, badge, tooltip note, colour, or visual/semantic state. The internal term "input-starved" is for design notes only and must **never** surface in the player UI.
  - The **only** gate is the standard "you do not have the materials / level" check that every other target already uses. Adding the missing acquisition/use route later lights the content up with **zero change to the recipe row itself**.
  - Example: dragonstone-cutting and dragonstone-jewellery targets exist and are wired now, looking and behaving like any gem recipe; they just sit material-locked until dragonstone acquisition (GE, crystal chest, rare drop table) ships. An enchant action appears under Magic when Magic ships.
- Locked/greyed targets must **not be selectable**: a click on a disabled row must not change the active target (Qt still fires `itemClicked` on disabled items, so guard the handler). Selecting an unrunnable target only to fail the next review is a bug, not a feature.
- Skills-hub target lists should use `target_metadata.TargetRowMetadata` row builders instead of adding new per-skill row plumbing in `ui.py`. Flat lists render through the shared Qt flat-list helper; grouped target trees render through the shared grouped `QTreeWidget` helper.
- **Assets are mandatory, every pass, without being asked.** A skill expansion is not done until its target/output/material icons are fetched (via `tools/fetch_assets.py` or a skill-specific `tools/fetch_<skill>_assets.py` deriving its manifest from the data module), wired through the item registry, provenance-recorded, and covered by an asset-path test. Rows may degrade gracefully to text-only when a single icon genuinely will not resolve, but skipping the asset step entirely is not acceptable.
- Separate XP-bearing skill actions from no-XP Utility/Activities.
- Keep persisted save keys flat unless a migration is deliberately planned.
- Every review reward must remain compatible with Anki undo rollback.
- Quest XP rewards for skills that are not implemented yet must not be dropped
  or left as Memory Bank-only reminders. Store them as structured pending
  reward data in flat player state, keyed by the future skill XP key or stable
  skill id, then apply them programmatically once that skill becomes
  implemented. The later LLM/agent task may add the skill and tests, but reward
  delivery must not depend on an LLM remembering an old note.
- For normal interactive expansions, add pre/post HTML status artifacts in
  `memory-bank/status-updates/` and update the memory bank when patterns change.
  The automated gap-fill workers launched by `tools/gap_driver.py` are the
  deliberate exception: they must not create, open, upload, or surface per-item
  HTML artifacts. Their private `impl_report.md`, `review_report.md`, logs, tests,
  and verdict JSON are the intermediate trace. The orchestrator produces one
  consolidated human-facing artifact only after the terminal completeness audit.

## Source Hierarchy (Full Pre-EOC Parity)

The canonical target is the live game immediately before EOC, not a 2011
subset. Follow `memory-bank/pre-eoc-source-verification-standard.md` for the
full evidence contract and cache manifest. Use sources according to what each
can actually prove:

1. **Pinned pre-cutoff RuneScape Wiki evidence.** Prefer the nearest useful
   `runescape.wiki` revision at or before 2012-11-20 and inspect its literal
   wikitext through the MediaWiki API. Follow referenced templates, modules,
   calculators, and tables to their own period revisions; a rendered old page
   backed by modern dependencies is not period proof.
2. **Dated Wayback captures.** Use them when history is missing, moved, or when
   a period dependency cannot be recovered from wiki revision history.
3. **Period OpenRS2 caches.** Use the local rev 727, 728, 729, 736, 741, and 742
   disk caches for client-side identity/config evidence: IDs, names, options,
   sprites/models, interfaces, scripts, and varbits. They normally cannot prove
   server XP, success rolls, gates, timers, drop rates, or economy behavior.
4. **Local implementation evidence, with reconciliation.** The 2011Scape rev
   667 source is baseline evidence only for mechanics verified unchanged through
   the cutoff. Modern Darkan is reconstruction evidence, not automatic period
   proof; treat its high-fidelity revamped content as server-behavior evidence
   only after reconciling it with period wiki, cache, or archive evidence.
5. **Research leads only.** Current RS3, OSRS, community wikis, and modern
   emulators may identify questions or candidate mechanics but cannot establish
   November 2012 parity on their own.

Record conflicts instead of silently choosing a convenient source. If the
required evidence is incomplete, mark the row `source_blocked` and wait for a
better historical source or the relevant high-fidelity Darkan work. Never fill
the gap from modern RS3/OSRS behavior. Existing generated quest rows, including
the 194-row catalog, are scaffolding rather than proof of full quest parity.

## Specific Instructions

Think through these steps before making code changes:

1. Audit sources:
   - Start with the nearest useful pre-cutoff RuneScape Wiki oldid and literal
     wikitext. Resolve period template/module/calculator dependencies.
   - Use dated Wayback captures for missing or moved history, and the local
     period caches only for client-side facts they can prove.
   - Use 2011Scape and Darkan implementation evidence only within the
     reconciliation rules above. Do not promote either source beyond its date
     or demonstrated fidelity.
   - Extract action tables: level, item/action, materials, outputs, XP, members/F2P, quest gates, tool requirements.
   - Record page title, oldid, timestamp, cache build and IDs/options, local
     source path/commit, proven vs abstracted values, conflicts, and tests.
   - Mark incomplete evidence `source_blocked`; mark post-cutoff or OSRS-only
     behavior out of scope instead of guessing.

2. Cut scope:
   - Implement every candidate that has clear pre-EOC source data, fully wired and selectable, regardless of whether its inputs are obtainable yet. The recipe/action is real now.
   - The only thing deferred is missing supporting infrastructure: an acquisition route for an input (drop, market, another skill, Utility/Activity) or a downstream use/action that belongs to a not-yet-built skill. Track those gaps as notes, not as gates on the action.
   - Do not artificially block, hide, or "coming soon" a fully-source-backed action. Rely on the existing normal material/level gating; an action with no obtainable input is simply inert until that input has a source.
   - Reserve `future_content` for content lacking clear source data, and `not_applicable` for dev/test/shop-tool/quest-only junk with no useful AnkiScape semantics.

3. Add backend data:
   - Update `skill_registry.py` for skill identity, category, save keys, review eligibility, handler key, and visibility.
   - Update `constants.py` or a focused data module with stable target IDs, display names, level requirements, XP, inputs, outputs, batch size, and source notes.
   - Update `item_registry.py` so outputs and required materials have stable item definitions and asset paths.
   - Add storage defaults/migrations through `storage_pure.py` without deleting unknown inventory entries.

4. Fetch assets:
   - Use `tools/fetch_assets.py` for item icons where possible.
   - Item *art* changed across eras; prefer a period cache sprite or pinned
     pre-EOC wiki asset. Use modern art only after verifying it is unchanged.
   - Normalize PNGs, avoid overwriting unless intentional, and update `assets_provenance.json`.
   - Add tests that required manifest asset paths exist.

5. Implement mechanics:
   - Add pure logic first in `logic_pure.py`.
   - Model one successful card as one action tick by default.
   - For no-XP Utility/Activities that represent quick material prep, use explicit batches capped by inventory (for example, up to 28 items per successful card).
   - Apply any global XP multiplier after base XP is calculated and before level checks.
   - Keep no-XP Utility/Activities from awarding skill XP.

6. Update frontend:
   - Keep the current UI style unless a redesign is explicitly requested.
   - Add registry-driven target lists, icons, level/material gates, and concise tooltips.
   - For target lists, add or update the relevant `target_metadata.py` row builder, then render it through `ui.show_main_menu`'s shared flat-list or grouped-tree helper.
   - Label Utility/Activities clearly as no-XP material prep.
   - If touching settings, preserve existing toggles and group related controls into clear sections.

7. Add achievements:
   - Prefer registry-generated achievement patterns over hand-written lambdas.
   - Add generic milestones first: first action, level 10/30/60/99, 100/1,000/10,000 outputs or actions where sensible.
   - Add only a few stable skill-flavored achievements per slice.
   - Avoid completionist achievements for content whose target list is still experimental.

8. Handle quest unlocks and deferred rewards, when quest content is in scope:
   - Add source-backed quest definitions before adding completion gates.
   - For broad quest catalog work, use `tools/build_pre_eoc_quest_catalog.py`
     to refresh `quest_catalog_generated.py` instead of hand-entering rows.
     The cutoff snapshot is the quest set available before the 2012-11-20
     Evolution of Combat release, including quests that only became
     `former` after that date. Do not hand-edit the generated catalog; update
     the generator or the focused override layer in `quest_data.py`.
   - Preserve hand-audited quest overrides for unlock-critical rows when
     the generated/current wiki requirement surface is looser than the
     pinned pre-EOC evidence.
   - Enforce quest start requirements strictly, including required skills and
     prerequisite quests. If a required skill or prerequisite quest is not
     implemented yet, the quest must be impossible to start rather than
     approximated.
   - Use completion gates for source-backed unlocks, and keep route/location
     gates out of global target locks until a route/acquisition model exists,
     except when the current AnkiScape target effectively represents that route.
  - Grant concrete rewards that the current game can represent safely.
  - Broad quest imports must carry source-backed journal text whenever it is
    available. Prefer exact 2011Scape `QuestStage` objectives; use
    source-backed quick-guide checkpoints only as an explicit fallback instead
    of pretending generated placeholder text is a copied journal.
  - Recipe for Disaster is not one aggregate quest row. Model its cook intro,
    each freed guest, and the Culinaromancer finale as separate quests with
    their own requirements and rewards.
  - Import quest rewards as structured data: quest points, direct XP, item
    rewards, unlock notes, and XP lamp/choice rewards. Flatten historical lamp
    interfaces into Bank Claims while preserving allowed skill options and
    minimum-level constraints.
  - Store XP rewards for unimplemented skills as structured pending rewards in
    flat player state; auto-apply them programmatically during load/migration
    once the skill exists, with tests proving one-time application.
  - Route/location gates stay out of global locks unless the current
    AnkiScape target effectively represents that route. Current flattened
    precedents are `gem_rocks` -> Shilo Village, Morytania-flavored slimy
    eel/snail rows -> Priest in Peril, and Neitiznot-flavored yak/arctic pine
    rows -> The Fremennik Isles; later location modeling can split alternative
    routes without changing the base skill tables.

9. Test:
   - Unit tests for pure logic, data integrity, source assumptions, and batch caps.
   - Pure tests for any `TargetRowMetadata` row builder changed or added.
   - Integration tests for review dispatch, XP/inventory mutation, storage migration, and Anki undo rollback.
   - Offscreen Qt tests for target panels, gating, tooltips, settings controls, and registry-driven surfaces.
   - Manual Anki test instructions for runtime review flow.
   - Run `python3 run_tests.py`; for Qt behavior also run `QT_QPA_PLATFORM=offscreen .venv-qt/bin/python -m unittest discover tests`.

## Tool Guidelines

- Start source audits from a pinned pre-cutoff wiki revision and literal
  wikitext; then use period caches and reconciled local implementations for the
  evidence classes they can prove.
- Use `tools/query_openrs2_cache.sh` to inspect exact item identities/options in
  the six local period caches. Do not infer server mechanics from cache output.
- Use `tools/fetch_assets.py` for assets and provenance.
- Use pure tests before Anki/Qt tests when adding backend mechanics.
- Use offscreen Qt tests for UI behavior rather than restarting Anki repeatedly.
- Use status artifacts for pre/post implementation communication instead of long
  chat summaries, except inside the automated gap-fill lane described above.

## Handoff Format

When planning or summarizing, split work like this:

- Backend: source audit, data tables, item manifest, pure logic, storage, dispatch, achievements, tests.
- Frontend: Skills hub/Utility UI, target lists, tooltips, settings, Stats/Bank/HUD, Qt tests.
- Assets: scrape list, output folders, provenance, missing/deferred assets.
- Balance: audited pre-EOC base values, Anki batch sizes, XP multiplier implications, known pacing risks.

## Dynamic Project Context

- Current source base: Anki add-on Python package in `addons21/ankiscape_fork`.
- Current review model: one eligible successful card is one game action tick unless a target declares batching.
- Current save pattern: flat `player_data` keys stored in Anki config.
- Current source policy: full pre-EOC parity at the 2012-11-20 cutoff. Pinned
  historical wiki/Wayback evidence establishes period semantics and values;
  period caches establish client-side facts; 2011Scape and Darkan require
  date/fidelity reconciliation; modern RS3/OSRS are research leads only. See
  Source Hierarchy and `memory-bank/pre-eoc-source-verification-standard.md`.
- Current pacing policy: keep audited base XP data separate from gameplay multipliers.
- Current target-list UI contract: `target_metadata.py` owns row metadata for Mining, Woodcutting, Fletching, Firemaking, Fishing, Smithing, Crafting, Cooking, Runecrafting, and Utility/Activities; Qt renders flat rows through a shared flat-list helper and grouped rows through a shared `QTreeWidget` helper.
- Current runtime-action contract: `action_registry.py` resolves handler keys, `runtime_actions.py` owns review-action mutation bodies and can-start checks, and `__init__.py` supplies Anki/save/HUD/achievement callbacks through `RuntimeActionContext`.

For detailed templates, use [reference.md](reference.md).
