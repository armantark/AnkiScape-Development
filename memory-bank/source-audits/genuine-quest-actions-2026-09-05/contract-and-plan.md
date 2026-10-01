# Genuine quest actions: source contract and implementation plan

> **Fremennik shield supersession — 2026-10-01:** Ruling 4.29.7 resolved the
> Woodcutting conflict by adding no separate recipe threshold: the existing
> quest eligibility and a stage-5 traditional-rites gate govern the action. The
> source-only implementation block below remains applicable to the two spells.

Status: source-only review for the two spell actions. Their implementation remains blocked by the unresolved rod-state identity and applicable file-size prerequisites; the shield action is superseded above.

## Outcome

Bind three existing quest requirements to the named successful player actions. Generic jewellery enchantment must not satisfy either quest enchantment requirement. Possession of an item must not create an action proof. Each action must consume its real inputs, retain its tools, produce its real output, award the correct skill XP, and persist its proof through the existing action recorder.

| Deed | Proposed event | Existing proof text | Source disposition |
| --- | --- | --- | --- |
| Cast Level 2 Enchant on the emerald sickle | `magic:enchant_emerald_sickle` | `Cast Enchant Level 2 Jewellery for the emerald preparations` | The action, input/output identity, runes, normal spell XP, and input preparation are bound. |
| Cast Level 1 Enchant on the Silvthrill rod | `magic:enchant_silvthrill_rod` | `Enchant sapphire for the Myreque preparations` | The action and recipe are bound. The raw/enchanted numeric item transition remains unresolved. |
| Make a Fremennik round shield | `crafting:craft_fremennik_round_shield` | `Make a Fremennik round shield` | Recipe, retained hammer, output, XP, and rites gate are bound. Woodcutting 54 versus 56 remains unresolved. |

The event IDs are proposals, not existing implementation. No proof ID needs to be renamed.

## Bound mechanics

### Emerald sickle

Legacy of Seergaze revision 6521668, dated `2012-11-02T22:17:22Z`, requires the player to fit an emerald to the blessed sickle, then cast Level 2 Enchant. Its literal wikitext lines 146–154 identifies Safalaan's material grant and the retained chisel route. The retained cache rows bind `Silver sickle emerald (b)` to 13155 and `Enchanted sickle emerald (b)` to 13156 in builds 727–742. These names are different from the informal harvest label “enchanted emerald sickle.”

Silver sickle emerald (b) revision 5504656, dated `2012-04-17T22:42:34Z`, explicitly grants 20 Crafting XP for embedding one emerald in one blessed silver sickle with a chisel. The chisel stays in inventory. The article gives no additional Crafting threshold. Do not invent one. The current quest eligibility already includes Crafting 47, and the acquisition stage must be reached before the recipe is available. A Crafting recipe's required `level` field may use 1 to mean no additional action threshold, provided the quest-stage gate is enforced separately; it must not claim that 1 is a recovered period requirement.

The following Magic cast consumes one item 13155, one Cosmic rune and three Air runes, produces one item 13156, and uses the ordinary Level 2 Enchant requirement of Magic 27 and 37 Magic XP. Legacy's separate quest eligibility includes Magic 49. Do not confuse that quest requirement with the standard spell's level. The existing generic enchant implementation and current Magic table agree on the standard spell values. The period quest explicitly calls that standard spell and supplies its exact runes; no period exception is stated. Applying the normal spell mechanic is direct reuse, not an invented quest-specific XP award.

The later Darkan restoration differs from these mechanics. `LegacyOfSeergaze.kt:750–763` fits the emerald with a chisel but makes no XP award; the period item article explicitly gives 20 Crafting XP. This is an implementation omission relative to the period evidence, not proof that the period award was zero. Its enchant handler at lines 766–779 checks Magic 49. The proposed spell metadata uses standard Level 2 Enchant at 27 while retaining Legacy’s own quest eligibility at 49; that level difference is unobservable on the valid quest route. Do not add a new source blocker or remove the quest gate because of these implementation differences. Both functions were introduced by restoration commit `63b3c901cb8debf42d66cbf50fe84eaeb79fcc92`.

### Silvthrill rod

In Aid of the Myreque revision 6555220, dated `2012-11-14T12:32:46Z`, lines 148–155 binds the route: read the books, open Ivandis' tomb with a hammer, use one Soft clay on the tomb for a Rod clay mould, make the rod at a furnace with one Silver bar, one Mithril bar and one Sapphire, then cast Level 1 Enchant. The dated walkthrough does not state mould retention. The retained-tool claim comes from current `data/crafting_data.py:232` (`required_items`) and the local 2011 `SilverAction.kt:20–49,79–81`: the action checks the mould, removes only the Silver bar and extra ingredients, and retains the mould. The existing Crafting recipe supplies Crafting 25 and 55 Crafting XP, corroborated by the local 2011 `SilverData.kt` implementation. No new rod recipe is needed.

The cast consumes the raw rod, one Cosmic rune and one Water rune. It uses ordinary Level 1 Enchant, Magic 7 and 17.5 Magic XP. The subsequent rope-and-well charge into Rod of Ivandis is a separate deed and must not be silently folded into the enchantment event. Tablet routes are documented alternatives, outside these two requested spell casts; this plan does not automatically add them.

The current `Silvthrill rod` title has no pre-cutoff revision. Following its current redirect found `Silvthril rod`, revision 6359850, dated `2012-10-06T22:07:55Z`. That article confirms the recipe and enchantment sequence but states no numeric item IDs. The raw negative lookup and redirect response are both retained.

### Fremennik shield

The November quest revision 6540919, dated `2012-11-07T09:46:34Z`, line 171 says “two arctic logs”; the shield article names “two [[arctic pine logs]]”. Both bind one Bronze nail, one Rope, a retained Hammer, and 34 Crafting XP. The player learns the action from Mawnis at the traditional rites step. The woodcutting stump is the station; it does not change the awarded skill to Woodcutting. The retained cache binds the shield to item 10826. Existing Woodcutting already produces `Arctic pine logs`.

Neither the shield article nor the quest's shield instructions states a separate Crafting threshold. Use no additional Crafting-level gate. The Crafting schema requires a numeric level, so 1 can represent the absence of an additional gate when the rites and Woodcutting gates are enforced separately. Crafting 46 is the yak-body requirement and must not be copied onto the shield.

## Two unresolved source fields

### Rod state IDs

The retained 727–742 cache gives IDs 7620, 7637 and 7638 the same name, `Silvthrill rod`. IDs 7637 and 7638 both have `Look-at`; 7620 does not. This establishes three client identities, not the enchantment transition.

The local 2011 crafting implementation emits 7637. Current Anki follows it; this existing value is disputed implementation data, not a neutral default or a proven raw-state identity. The later Darkan restoration instead uses raw 7620 and enchanted variants 7637/7638. Its target contract repeats that mapping. The dated item article supplies no IDs, and the bounded existing 2011 enchant implementation contains ordinary jewellery only. Therefore neither the cache name nor the restored mapping closes the transition. Do not invent an output ID or relabel the current rod as enchanted. A distinct inventory key for the enchanted state will be needed after identity is resolved, because the source names collide.

### Shield Woodcutting requirement

The item article revision 5827384, dated `2012-06-25T19:52:33Z`, says: “The Fremennik round shield can be obtained by making it with level 54 [[Woodcutting]]”. It carries `{{beta}}`. The one inspected prior revision, 5641898, dated `2012-05-22T11:53:12Z`, has the same 54 statement and no beta marker. Therefore beta qualification alone cannot discard 54.

The November quest revision explicitly says at line 52: `[[Fremennik round shield]] (can be made during the quest if you have 56 woodcutting or bought from the GE)`. This is a shield-specific statement, not only a quest summary. The current Darkan action checks 56, but its frozen qualification assigns Woodcutting 56 to split-log production and merely says Crafting for the shield. Existing Anki's arctic chopping and split-log targets use 54. None of these facts independently resolves the contradictory shield statements.

The same November quest revision also states at line 36: `{{Skillreq|Woodcutting|56}} (Not actually required for the quest if you buy the Round Shield and the split logs from the [[Grand Exchange]])`, and at line 46: `*8 [[Split log]] (only if you are under 56 Woodcutting)`. These describe related production requirements in the same article; they are not independent corroborating sources for the shield threshold.

The frozen qualification summary and the restored function must be distinguished. The summary assigns 56 to split logs. The source itself explicitly checks 56 in `craftShield`, separately from `splitLogs`. In `/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/src/main/java/com/rs/game/content/quests/fremennikisles/FremennikIsles.kt:418`, the relevant code is:

```kotlin
fun craftShield(player: Player): Boolean {
    if (stage(player) !in FremennikIslesState.DECREE_ISSUED..FremennikIslesState.RITES_READY || player.skills.getLevelForXp(Skills.WOODCUTTING) < 56 || !inventoryHas(player, FremennikIslesIds.HAMMER)) return false
    // Inventory transaction and capacity handling omitted.
    if (!consume(player, FremennikIslesIds.ARCTIC_PINE_LOGS to 2, FremennikIslesIds.BRONZE_NAIL to 1, FremennikIslesIds.ROPE to 1)) return false
    // Output grant and rollback handling omitted.
    player.skills.addXp(Skills.CRAFTING, 34.0)
    return true
}
```

`git blame` attributes that function to `adb5dd15fe6272fd3c639d5de698f3633ba117b0`, “Restore the November 2012 Fremennik Isles route.” The supplying file was created by that July 2026 restoration, not recovered unchanged from a period server. The current checkout is `6277992980582f7b3da3a48e722e96cfa5b0a57d`; the file’s latest commit is `161542997012a031807930112f31e767419dd99b`. The restoration and its cited quest article cannot be presumed independent. This history proves where the check came from in the local code, not that the number is historically correct.

The project source standard requires independent corroboration and explicit conflict retention. The standard explicitly separates “two axes”: search order and corroboration. Its first search position for Darkan is not an authority ranking. It gives no rule that automatically lets Darkan, the newer quest guide, or the more focused item article win. Record the field as `source_blocked`; do not choose a threshold silently. All agreed shield mechanics remain ready for implementation once this field is resolved.

## Ordinary acquisition and stage ordering

Rod clay mould has an icon binding and a retained-tool requirement in the current recipe, but no ordinary producer was found in the bounded current data scan. Add the proven Soft clay-to-mould action through the existing quest-stage transaction model. Do not seed inventory in the gameplay path or grant the mould at quest completion. The player's real hammer, books/tomb stage, and Soft clay must gate the acquisition. Use the existing recipe afterwards.

Nature Spirit already converts a Silver sickle into a Silver sickle (b). Legacy's dated route also returns the sickle and emerald through Safalaan. Add the minimum genuine stage acquisition needed for the emerald preparation, then a separate 20-XP Crafting action with a retained chisel. Do not grant the already enchanted item or credit its proof from the grant.

The current generated journal and requirement rows do not align with these acquisition steps: Legacy's proof is required at stage 5, while its material grant appears in stage 6; In Aid's enchant proof is required at stage 6, while the tomb and rod production appear in stage 7. Adding producers after these proof gates would deadlock both quests. Before code, define a bounded stage transaction/requirement patch that puts acquisition before its proof check and preserves the sourced action order. This is an implementation requirement exposed by the three deeds, not permission for a full quest rewrite. Preserve unrelated encounter and quest requirements.

## Minimal implementation seams

1. Extend the existing Crafting and Magic tables. Add only the emerald attachment, the two named transforms, and the shield recipe. Reuse the existing silver rod recipe and normal rune/material handling. Keep source IDs, inventory keys and proof events distinct.
2. Add structured stage and secondary-skill requirements where existing target metadata cannot express them. Magic's current `quest_gate` means quest completion, so it cannot gate an action needed inside the same quest. Do not set that field to the action's own quest. Crafting currently has a Crafting level and retained `required_items`, but no secondary skill or stage gate.
3. Reuse the existing start-side check at `runtime/runtime_actions_gates.py:589–596`: `_can_start_crafting_action` already calls `crafting_target_locked_reasons_pure`. The target selector also uses that pure readiness function. Add the matching check immediately before inventory mutation in `handle_crafting_answer`, which currently checks only materials and Crafting level. Do not duplicate the existing start gate; the mutation check must also handle state changes after an action starts. Magic already validates its target through its pure readiness path. Use the established quest-current-stage helper rather than a separate progress format.
4. Add the three exact event rules and matching reachability sources to the existing proof tables. Both runtime handlers already call `_record_action` after success. Do not add a second proof store, migration, or generic enchantment credit.
5. Add the minimum stage acquisition transactions and requirement corrections. Inputs and tools must come from existing ordinary skill/shop/quest paths. Verify reachability from those paths and prove that the generated stage mismatch is removed.

## File boundaries and size prerequisites

Measurements below are static counts at the recorded baseline. The complete hashes are in `baseline-file-hashes.json`.

| Existing file | Lines | Expected relation to this work |
| --- | ---: | --- |
| `data/crafting_data.py` | 530 | Recipes, retained-tool data and any required gate fields. |
| `data/magic_data.py` | 626 | Named transformations and stage metadata. |
| `data/quest_action_proof_data.py` | 55 | Exact event and reachability bindings. |
| `logic_pure/logic_pure_magic.py` | 547 | Own-quest stage readiness. |
| `logic_pure/logic_pure_production.py` | 988 | Crafting readiness has only 12 lines before the cap. Keep the final file within 1000 lines. |
| `runtime/runtime_actions_production.py` | 1450 | Crafting mutation gate. Its structural prerequisite must be completed before this file is changed. |
| `data/quest_data.py` | 12667 | Stage acquisition and proof ordering. Its structural prerequisite must be completed first. |
| `tools/audit_item_reachability.py` | 2165 | Reuse existing generic action discovery if sufficient; any required change first needs its size prerequisite. |
| `core/target_metadata.py` | 2002 | It already consumes pure Crafting readiness. Avoid a new direct dependency; any necessary change needs its prerequisite. |
| `core/constants.py` | 2991 | Do not insert hand-written icon rows into this oversized module. Resolve any required asset registration through its approved split. |

Use existing generic registration where it covers the new targets. Do not evade the cap by placing a long body on one line or by adding a wrapper that leaves the actual edited file oversized. The pool baseline also predates retained-shop-proof candidate `66bcbc6fbc2482c87c78ef75ff5a440c83c5c85b`, which passed focused verification but still awaits full regression and native verification. Parent integration must preserve that candidate and compose it only after its remaining checks and promotion decision.

## Verification contract after implementation approval

Write focused behavioral cases before the new production logic. Check each successful action's exact inventory delta, retained tools, XP, one save and one exact proof. Check missing material, missing tool, inadequate skill, and a stage below the unlock; failure must not consume inventory or create proof. Ordinary sapphire/emerald jewellery enchantment must create neither quest proof. Owning or injecting a finished item must not create a proof.

Run integration paths through the real runtime handlers, then save/reload and undo through the normal parent-owned harness. Check that each quest's matching blocker clears and the other two remain. Prove the full ordinary prerequisite chain, including the mould and emerald preparation, without a seeded intermediate. Test stage order to prevent acquisition from sitting behind its own proof blocker.

Add end-to-end cases for the normal player route and parent-run native checks for target selection, visible locked reasons, action result, XP and persisted proof. Inspect visible labels for truncation. Run the established plain and Qt discovery/count checks and full regression gate under the parent's exclusive MBP ownership. Record raw output and source hashes. This source audit makes no runtime pass claim.

## Evidence retained

`period-sources.json` lists the raw period pages, exact oldids, timestamps and SHA-256 values. `retained-cache-identity.json` holds selected rows with JSON pointers and snapshot metadata from the existing cache packets. `local-source-hashes.json` identifies the read-only implementation and qualification files. `current-stage-scaffolding.json` records the exact AST-extracted quest rows that expose the stage mismatch. `pre-fetch-gaps.json` preserves the gap list before the bounded fetch. `papercuts.md` records lookup and packet-shape friction. `opus-source-review.txt` preserves the independent review, `opus-review-dispositions.md` addresses all eight corrections, and `review-provenance.json` retains supplying history and exact source excerpts. `manifest.json` covers this audit directory.
