# 12: Feed talismans to the hood

**What to build:** Each talisman and tiara the hood can take gets "Feed to Wicked hood" in its Bank right-click menu. Feeding consumes it at once through the existing feed rule as an undoable direct action. The review-driven "Hood feeding" Runecrafting targets go. Feed XP comes from the Darkan source if it has an amount; otherwise the feed stays at 0 XP as a registered placeholder.

**Blocked by:** 01 (Bank right-click menu in its own module), 11 (Wicked hood right-click menu)

**Status:** done

- [x] Right-clicking an air talisman with a hood owned offers "Feed to Wicked hood"; feeding unlocks the Air altar in the hood menu and consumes the talisman.
- [x] Undo restores the talisman and the hood's previous state.
- [x] An already-fed talisman or one the hood cannot take shows no feed entry, or a disabled one with the reason.
- [x] The "Hood feeding" target group is gone, with no stale save pointing at it.
- [x] The feed XP is sourced, or registered as a placeholder.
- [x] Offscreen Qt capture of the talisman menu at 560 px with clean text-fit checks; one play-checklist line.

## Feed XP source

Darkan checkout `/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server`, commit `1912a55cb245cc4410e51b200f9ad4c5e480510f`, awards 50 Runecrafting XP at `src/main/java/com/rs/net/decoders/handlers/InventoryOptionsHandler.java:115`, immediately after consuming the item at line 114. The feed branch spans lines 97–131. `git blame` attributes the XP line to original Darkan commit `bc2a69e481`, not a restoration probe. The ticket explicitly selects Darkan's amount when found; this is implementation evidence, not independent closure of the unknown amount in Talk:Wicked hood oldid 6341451 (2012-10-03T14:41:48Z). The amount remains uncorroborated and is marked `PLACEHOLDER(wicked_hood.feed_xp)` in code and registered in `memory-bank/placeholder-values.md`. The ticket's Darkan preference supplies the working amount, while the verification standard still requires independent corroboration.

The current retired feed target becomes `craft_air_runes`. `core/target_retirement.py` also removes retired feed IDs from every carried per-target map, the active bank run and the pending bank-run request, without changing Bank item totals. The Bank menu renders the feed view; the direct hood command owns refusal, consumption and upgrades. The shared direct-action transaction awards XP and restores the complete save on Undo. The full Darkan feed handler was reconciled: ordinary new altar, Elemental and Omni feeds pay the registered 50 XP placeholder; repeated feeds refuse without consumption or XP; the Elemental talisman after an Omni feed is consumed for the extra rune withdrawal with 0 XP (lines 103–109). Feeding the four elemental altars separately does not set Darkan's Elemental flag, so a later Elemental talisman still pays the placeholder amount. The handler and Player flag accessors are original Darkan material; the updated messages and Omni-tiara condition came from `ab4707ee4b`.

## Verification

- Focused plain: 90 tests passed. Registry suite after its retired-target count was updated: 69 tests passed.
- Offscreen Qt: 13 tests passed, including talisman feeding, tiara feeding, disabled repeated feeds, the removed group and text fit at 720 × 560. Before/after captures and clean fit records are under `/Users/ArmanTarkhanian1/Documents/ankiscape-pass16/evidence/12/`.
- Real review-handler probe: instant feed awards 50 XP without a card-clock change; the next review crafts all 28 essence using the fed hood, reaching 190 Runecrafting XP. Rune count follows the existing probabilistic multiplier.
- Full plain: `Ran 5453 tests in 1152.025s`; `FAILED (failures=2, errors=2, skipped=608)`. Three are the brief's known local failures. The fourth was the obsolete 76-target registry assertion; it now expects the 49 remaining targets, and the complete registry suite passed. No gameplay code changed after that full run.
- Documentation, test-quality, item-reachability and worktree audits passed; the diff has no whitespace errors. The integration promotion gate owns the full Qt and native checks.
