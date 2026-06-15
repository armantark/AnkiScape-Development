---
name: ankiscape-skill-expansion
description: Guides AnkiScape skill and action-family expansions. Use when adding or expanding AnkiScape skills, Utility/Activities, item chains, target lists, achievements, source audits, wiki scraping, asset scraping, XP balancing, or gameplay settings.
---

# AnkiScape Skill Expansion

## Task Description

AnkiScape is an Anki add-on that turns successful card reviews into lightweight RuneScape-style game progress. A skill expansion is any change that adds or expands a skill, action family, Utility/Activity, target chain, item economy slice, achievement set, XP/batch balance rule, or gameplay setting.

Use this skill before planning or implementing a skill expansion. The goal is to avoid rediscovering the same workflow each time: audit the source data, choose a playable scope, add backend data and pure mechanics, fetch assets, expose the UI, add achievements, test the review loop, and update the memory bank.

## Non-Negotiables

- Split backend and frontend work explicitly.
- Source data from the 2011 era (see Source Hierarchy). Cite the exact source before claiming XP, levels, materials, outputs, or unlocks. Do not infer these from memory.
- Do not treat the OSRS wiki as a 2011 source. OSRS branched from a 2007 backup, so OSRS data is 2007 baseline plus OSRS-only additions, not 2011. Use it only as a cross-check for content that was unchanged between 2007 and 2011.
- Keep source data honest: preserve audited 2011 base XP in data, then apply AnkiScape pacing knobs separately.
- Use stable IDs for skills, recipes, targets, and items. Do not use display names as durable target identifiers when outputs can collide.
- Build source-backed content **fully and live by default**, wiring each target/action into the UI as a normal, functional entry that is **indistinguishable from every other entry** — even when its inputs cannot be obtained yet. Such content is not special: it is simply, *emergently* un-runnable right now because the player holds zero of a material whose acquisition route (a drop, market, another skill, or Utility/Activity) does not exist yet. That is the **exact same state** as any normal recipe whose materials you happen to lack (e.g. a sapphire ring when you hold zero sapphires).
  - **Do NOT** delete it, hide it, "coming soon" it, add a `locked until later` gate, or give it any distinct tag, label, badge, tooltip note, colour, or visual/semantic state. The internal term "input-starved" is for design notes only and must **never** surface in the player UI.
  - The **only** gate is the standard "you do not have the materials / level" check that every other target already uses. Adding the missing acquisition/use route later lights the content up with **zero change to the recipe row itself**.
  - Example: dragonstone-cutting and dragonstone-jewellery targets exist and are wired now, looking and behaving like any gem recipe; they just sit material-locked until dragonstone acquisition (GE, crystal chest, rare drop table) ships. An enchant action appears under Magic when Magic ships.
- Locked/greyed targets must **not be selectable**: a click on a disabled row must not change the active target (Qt still fires `itemClicked` on disabled items, so guard the handler). Selecting an unrunnable target only to fail the next review is a bug, not a feature.
- **Assets are mandatory, every pass, without being asked.** A skill expansion is not done until its target/output/material icons are fetched (via `tools/fetch_assets.py` or a skill-specific `tools/fetch_<skill>_assets.py` deriving its manifest from the data module), wired through the item registry, provenance-recorded, and covered by an asset-path test. Rows may degrade gracefully to text-only when a single icon genuinely will not resolve, but skipping the asset step entirely is not acceptable.
- Separate XP-bearing skill actions from no-XP Utility/Activities.
- Keep persisted save keys flat unless a migration is deliberately planned.
- Every review reward must remain compatible with Anki undo rollback.
- Add pre/post HTML status artifacts in `memory-bank/status-updates/` and update the memory bank when patterns change.

## Source Hierarchy (2011-Era Parity)

AnkiScape replicates the **skilling** side of a compressed early-2010s RuneScape. The canonical baseline is the **2011Scape snapshot: RuneScape as of October 4, 2011 (client rev 667)** — the same era as the primary source below. This era sits *between* OSRS (2007 baseline) and current RS3 (post-EOC, Nov 2012), so neither live wiki is a clean source for it.

Treat the Oct-2011 snapshot as the source of truth. The ~13 months of pre-EOC 2012 content (e.g. Runespan, bonfires) changed training *methods*, not the skilling item/recipe tables, so the 2011-vs-2012 delta is negligible for our scope. Adopt a specific pre-EOC-2012 feature only as a deliberate, documented exception; never chase moving "2012 parity," since no equivalent clean dataset exists. Post-EOC content is out of scope.

Use sources in this priority order:

1. **Primary, authoritative: the local `2011Scape/game` emulator source.** Open-source (Apache-2.0), pinned to client **revision 667 (October 4, 2011)**. It is the source of truth for exact numbers: level requirements, XP per action, inputs/outputs, and tool tiers. Game balance numbers are facts (not copyrightable) and Apache-2.0 covers the code, so reading and referencing it is fine. `grep` it locally; never import it into the add-on runtime.
   - Local path: `/Users/ArmanTarkhanian1/Downloads/game-main` (update this line if the folder moves; upstream is `https://github.com/2011Scape/game`).
   - Skill mechanics: `game/plugins/src/main/kotlin/gg/rsmod/plugins/content/skills/<skill>/`. Each skill defines a `*Type.kt` enum holding per-target `level` and `xp` (for example `woodcutting/TreeType.kt`) plus a `*Type.kt` for tool tiers (for example `woodcutting/AxeType.kt`).
   - Item/object/npc data: `data/cfg/items.yml`, `data/cfg/objs.yml`, `data/cfg/npcs.yml`.
2. **Human-readable cross-check: the 2011Scape community wikis.** `https://rs2011.miraheze.org` and `https://2011scape.fandom.com`. Same reload, prose form. Thin coverage, so use to confirm intent, not as the only source.
3. **Canonical wiki with revision pinning: `https://runescape.wiki`.** Use page history / `?oldid=` filtered to 2011, plus the dated `Update:` pages and the month-by-month `/w/2011` archive to confirm what existed by Oct 2011 and when it changed.
4. **Raw cache (rarely needed): OpenRS2 Archive (`https://archive.openrs2.org`).** Dated binary cache dumps the emulators build from. Only for exact item IDs/sprites at the binary level.

OSRS wiki (`oldschool.runescape.wiki`) is a *cross-check only* for 2007/2011-shared content, never the primary 2011 authority.

## Specific Instructions

Think through these steps before making code changes:

1. Audit sources:
   - Start from the local 2011Scape source (see Source Hierarchy) for the skill's content plugin and data. Capture exact level/XP/material/output values.
   - Cross-check against the 2011Scape wikis and runescape.wiki 2011 revisions; reconcile any discrepancy in favor of the emulator data unless it is clearly a known emulator bug.
   - Extract action tables: level, item/action, materials, outputs, XP, members/F2P, quest gates, tool requirements.
   - Record the exact source (repo file path or wiki oldid) used for each implemented recipe.
   - Mark uncertain, post-2011, or OSRS-only-divergent content instead of guessing.

2. Cut scope:
   - Implement every candidate that has clear 2011 source data, fully wired and selectable, regardless of whether its inputs are obtainable yet. The recipe/action is real now.
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
   - Item *art* changed across eras; for items whose 2011 icon differs noticeably, prefer 2011-era art (runescape.wiki historical revision or a 2011Scape source). OSRS wiki art is an acceptable practical fallback for items whose icon is effectively unchanged.
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
   - Label Utility/Activities clearly as no-XP material prep.
   - If touching settings, preserve existing toggles and group related controls into clear sections.

7. Add achievements:
   - Prefer registry-generated achievement patterns over hand-written lambdas.
   - Add generic milestones first: first action, level 10/30/60/99, 100/1,000/10,000 outputs or actions where sensible.
   - Add only a few stable skill-flavored achievements per slice.
   - Avoid completionist achievements for content whose target list is still experimental.

8. Test:
   - Unit tests for pure logic, data integrity, source assumptions, and batch caps.
   - Integration tests for review dispatch, XP/inventory mutation, storage migration, and Anki undo rollback.
   - Offscreen Qt tests for target panels, gating, tooltips, settings controls, and registry-driven surfaces.
   - Manual Anki test instructions for runtime review flow.
   - Run `python3 run_tests.py`; for Qt behavior also run `QT_QPA_PLATFORM=offscreen .venv-qt/bin/python -m unittest discover tests`.

## Tool Guidelines

- Grep the local 2011Scape source (path in Source Hierarchy) as the first stop for source audits; use web fetch/search of the 2011Scape wikis and runescape.wiki 2011 revisions to cross-check.
- Use `tools/fetch_assets.py` for assets and provenance.
- Use pure tests before Anki/Qt tests when adding backend mechanics.
- Use offscreen Qt tests for UI behavior rather than restarting Anki repeatedly.
- Use status artifacts for pre/post implementation communication instead of long chat summaries.

## Handoff Format

When planning or summarizing, split work like this:

- Backend: source audit, data tables, item manifest, pure logic, storage, dispatch, achievements, tests.
- Frontend: Skills hub/Utility UI, target lists, tooltips, settings, Stats/Bank/HUD, Qt tests.
- Assets: scrape list, output folders, provenance, missing/deferred assets.
- Balance: 2011 base values (from the 2011Scape source), Anki batch sizes, XP multiplier implications, known pacing risks.

## Dynamic Project Context

- Current source base: Anki add-on Python package in `addons21/ankiscape_fork`.
- Current review model: one eligible successful card is one game action tick unless a target declares batching.
- Current save pattern: flat `player_data` keys stored in Anki config.
- Current source policy: 2011-era parity. Primary source is the `2011Scape/game` emulator repo (rev 667, Oct 4 2011); 2011Scape wikis and runescape.wiki 2011 revisions are cross-checks; OSRS wiki is 2007 baseline and a cross-check only. See Source Hierarchy.
- Current pacing policy: keep audited base XP data separate from gameplay multipliers.

For detailed templates, use [reference.md](reference.md).
