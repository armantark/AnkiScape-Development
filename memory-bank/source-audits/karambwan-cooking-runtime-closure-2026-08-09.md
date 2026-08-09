# Karambwan Cooking runtime closure

Date: 2026-08-09  
Cutoff: RuneScape immediately before EOC, 2012-11-20.

## Period evidence

| Action | Period facts | Evidence |
| --- | --- | --- |
| Cook poison karambwan | Raw karambwan becomes Poison karambwan at level 1 for 80 Cooking XP. It can burn into Burnt karambwan, stops burning at level 20, and remains available during and after Tai Bwo Wannai Trio. | `Poison karambwan` oldid 6250179, 2012-09-16T05:45:03Z; `Tai Bwo Wannai Trio` oldid 6529797, 2012-11-03T22:12:48Z. Immutable caches: `/Users/ArmanTarkhanian1/Documents/2012scape with bots/memory-bank/audit/sources/poison-karambwan-oldid-6250179.json` and `tai-bwo-wannai-trio-final-preeoc-oldid-6529797.json`. |
| Cook karambwan thoroughly | Raw karambwan becomes Cooked karambwan at level 30 for 190 Cooking XP. It never burns. The player must complete Tai Bwo Wannai Trio and speak to Tiadeche to learn the method. | `Cooked karambwan` oldid 6154936, 2012-08-28T04:16:14Z. Immutable cache: `/Users/ArmanTarkhanian1/Documents/2012scape with bots/memory-bank/audit/sources/cooked-karambwan-oldid-6154936.json`. |
| Cook raw karambwanji | Raw karambwanji becomes Karambwanji at level 1 for 10 Cooking XP on a fire or range. The quest's additional-reward section assigns the ability after Tai Bwo Wannai Trio. | `Karambwanji` oldid 5838218, 2012-06-26T04:34:21Z; `Tai Bwo Wannai Trio` oldid 6529797, 2012-11-03T22:12:48Z. |

The final pre-EOC master table, `Cooking` oldid 6548144 dated
2012-11-11T16:17:12Z, independently lists level 1/80 XP/no-burn 20 for Poison
karambwan, level 30/190 XP/never-burn for thorough karambwan, and level 1/10 XP
with an unknown no-burn level for Karambwanji.

Rev-667 item definitions pin the live identities and tradeability:

- 3142 Raw karambwan, non-stackable and tradeable.
- 3144 Cooked karambwan, non-stackable and tradeable.
- 3146 Poison karambwan, non-stackable and non-tradeable.
- 3148 Burnt karambwan, non-stackable and non-tradeable.
- 3150 Raw karambwanji and 3151 Karambwanji, non-stackable and non-tradeable.

Source: `/Users/ArmanTarkhanian1/Downloads/game-main/data/cfg/items.yml:34771-34823`.

## Reconstructed values

The period pages do not expose either hidden success roll. Two registered
placeholders keep the sourced mechanics reachable without claiming invented
precision:

- `cooking.poison_karambwan_success_curve`: 50% minimum, rising to the sourced
  100% threshold at level 20.
- `cooking.karambwanji_success_curve`: 50% minimum, rising to 100% at level 28;
  failure creates Ashes. Level 28 and item 592 come from Darkan's reconstructed
  `RAW_KARAMBWANJI` row.

Darkan is corroborating implementation evidence only. Its karambwan enum is
internally inconsistent: the poison row uses Cooked karambwan as input, and its
quest row assigns level 30 to the poison output. Those fields were rejected in
favour of the dated pages. Source:
`/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/src/main/java/com/rs/game/content/skills/cooking/Cooking.java:52-63,80-99`.

## AnkiScape implementation

- Three separate `karambwan` targets preserve deliberate method choice. The
  edible method never replaces or hides poison cooking.
- Poison cooking unlocks when Tai Bwo Wannai Trio has started. Thorough cooking
  and Karambwanji unlock on completion; the thorough row names Tiadeche's
  instruction in its lock reason.
- One answered card consumes one raw input and atomically resolves the output,
  XP, telemetry, persistence, and review undo through the shared Cooking path.
- New period sprites cover Poison karambwan, Burnt karambwan, and Karambwanji.
  Raw and cooked sprites, plus Ashes, reuse existing normalized assets.
- No new UI pattern was added. The standard grouped Cooking selector owns all
  three rows.

## Explicit omissions

- The hidden period burn curves remain placeholders.
- The app does not add a separate post-quest conversation state for Tiadeche;
  the completion gate is the settled quest-substrate flattening and the target
  copy preserves the teaching requirement.
- Heat-source geography and animations remain outside AnkiScape's locationless
  one-review action model.

## Verification

Focused pure/runtime/registry/integration coverage passes 464 tests. Focused
real offscreen Qt selector coverage passes two tests, including grouped rows,
icons, tooltips, and inert quest locks. Full plain and real offscreen Qt
discovery each pass 3,982 tests; plain has 486 expected environment skips and
Qt has three intentional skips.

Documentation audits 540 Markdown and 431 HTML files. Test quality reports
zero hard issues across 3,948 tests in 180 files. Compilation, tracked JSON,
diff whitespace, global UI-asset normalization, and worktree safety pass. The
known reachability ledger improves to 1,542 actions and 2,344 reachable items,
with 166 orphan inputs and 186 unresolved actions.

Offscreen Qt proves the real widget implementation but is not claimed as a
native Anki visual or interaction check. This slice adds rows to the existing
Cooking selector rather than a new UI surface.
