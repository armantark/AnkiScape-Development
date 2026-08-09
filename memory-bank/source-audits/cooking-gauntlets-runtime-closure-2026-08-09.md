# Cooking gauntlets runtime closure — 2026-08-09

Backlog id: `cook-cooking-gauntlets-runtime`

Status: implemented and verified. This audit supersedes the unresolved affected-
fish and Monkfish clauses in `gap-grill-17-final-firemaking-cooking-provenance-
2026-07-10.md` and `gap-grill-decisions-2026-07-10.md`. The settled product
shape in the latter remains authoritative.

## Period evidence

- RuneScape Wiki `Cooking gauntlets` oldid `6556123`, timestamp
  `2012-11-15T02:31:56Z`, says the worn gloves reduce fish-burning risk, Family
  gauntlets convert through Caleb, changing an already enchanted pair costs
  25,000 coins, and Dimintheis replaces a lost pair free with the same
  enchantment. It explicitly lists no-burn levels Tuna 63, Lobster 68,
  Swordfish 81, Monkfish 90, and Shark/Cavefish/Rocktail 94. Literal wikitext
  fetched with `tools/wiki_parity.py content --revid 6556123`, SHA-256
  `14f12d06e213a3f44e5c397bfd12b18829c9e064bc4824612c9eeecb5b4b3890`.
- The later and more specific RuneScape Wiki `Cooking/Burn level` oldid
  `6572206`, timestamp `2012-11-18T06:47:37Z`, explicitly lists the gauntlet
  no-burn column as Trout 50, Tuna 63, Lobster 68, Swordfish 81, Monkfish 87,
  and Shark/Cavefish/Rocktail 94. Literal wikitext fetched with
  `tools/wiki_parity.py content --revid 6572206`, SHA-256
  `0cefe4145d957232bbcf9058f248b4a61eb94af30f9859e487c056bc4995c012`.
  This later table resolves the stale Monkfish 90 row and adds the explicit
  Trout threshold. Its own `Incomplete` marker means it does not prove that
  these eight rows are an exhaustive list of every affected fish.
- Local 2011Scape `data/cfg/items.yml:6714-6845` establishes item ids 775-778,
  hands-slot identity, the common modeled bonuses (+2 stab/slash/crush attack,
  +8/+9/+7 stab/slash/crush defence, +2 melee strength), and the per-variant
  destroy/recovery text. The period page independently confirms Cooking
  gauntlets' displayed bonuses.
- Darkan restoration commit
  `4f704bd15dd3bc163d8a3701199020064855c80d` (`2026-07-19T05:25:14-07:00`)
  reconciles the final dated table against the rev-667 curve. Its immutable
  normalized source artifact is
  `memory-bank/audit/sources/cooking-burn-mechanics.json`, SHA-256
  `b2386c9a9632ae9b57fe0bbb4dbeb597d3f8d200a66384a91706dd1d2a7364b8`;
  its target contract is SHA-256
  `e74b49582e8a27dcbcd62e1006f3a8cf45b5444528920476044943a0625c6347`.

## Reconciliation and abstraction boundary

- AnkiScape keeps the existing rev-667 low/high interpolation below each exact
  threshold. When Cooking gauntlets are worn, a listed fish becomes 255/255 at
  its dated threshold. Below it, the existing probability is preserved; if
  that ordinary curve already guarantees success, as it does for Trout at
  level 49, wearing gauntlets cannot make the outcome worse. No shifted
  probability curve was invented.
- Only the eight rows explicitly present in the final dated table receive the
  modifier. The older prose says all fish have reduced risk, but neither period
  source exposes a complete affected-food table or a numerical reduction for
  omitted fish. Those intermediate or omitted-row effects remain
  `source_blocked`; they do not block the mechanically complete equipment,
  conversion, recovery, and exact-threshold slice.
- AnkiScape does not model cooking surfaces. The ordinary target curve remains
  its existing one-action abstraction; this slice adds only the verified worn-
  gauntlet boundary.

## Live implementation

- `data/cooking_data.py` stores the eight exact target thresholds.
- `data/cooking_gauntlets_data.py` registers all four physical hands-slot items
  and their period bonuses.
- `logic/cooking_gauntlets_logic.py` owns Family Crest completion gating,
  free/25,000-coin conversion, separately remembered enchantment, free
  same-enchantment recovery, target-local Casual/Advanced policy, safe
  displacement, and restoration of only gear that automation moved.
- `logic_pure/logic_pure_production.py` applies the worn modifier without
  changing XP. `runtime/runtime_actions_production.py` reconciles physical gear
  before one Cooking roll. `logic/cadence_live.py` therefore routes `cook_shark`
  through its normal embedded-probability path instead of the retired modifier
  block.
- `ui/ui.py` exposes conversion from both Bank and worn Equipment context
  menus. Target Details holds one compact Gauntlets policy. Recovery appears
  only when the remembered pair is genuinely absent.
- Schema 114 persists and repairs the enchantment, target choices, and one
  automation displacement record. Old completed Family Crest saves infer an
  owned variant when present, otherwise the original Family enchantment.
- Conversion, payment, target equipment changes, recovery, manual Family-
  gauntlet equip/unequip, review outcome, inventory, burn/XP state, and random
  state use the established direct-action or review undo paths.

## Assets and visual review

The existing provenance-recorded quest sprites are reused. Family, Cooking,
Goldsmith, and Chaos gauntlets are each normalized to 30 by 26 pixels. Dark and
light 1000 by 640 offscreen renders preserve readable text and target-list
space. Kimi K3 and Fable independently requested the same primary taste fix:
hide the recovery button outside the actual loss state. The accepted pass also
renames the control to `Gauntlets`, makes the three policy labels outcome-
specific, and surfaces stale-action failures.

## Manual Anki proof

1. Complete Family Crest and right-click Family gauntlets in Bank. Confirm
   `Enchant for Cooking`, then use Anki Undo and confirm the original pair
   returns.
2. With Goldsmith or Chaos gauntlets and 25,000 Coins, confirm the context action
   consumes exactly 25,000 Coins and Anki Undo restores both item and balance.
3. Choose Shark at Cooking 94 with Cooking gauntlets in Bank and another hands
   item worn. Confirm Casual equips Cooking gauntlets, banks the displaced item,
   never burns Shark, and restores the displaced item after selecting an
   unaffected target or Advanced `leave hands slot unchanged`.
4. Discard the only pair, open Shark Target Details, recover the remembered pair
   for free, and confirm the button disappears. Undo restores the lost state.
5. Repeat at Cooking 93 and confirm Shark is not yet guaranteed; Cooking XP
   remains 210 only on success.

## Verification

- Focused pure, runtime, integration, cadence, and parity coverage: 562 tests
  passed in 150.810 seconds.
- Focused Cooking-gauntlet plain/offscreen-Qt coverage: 16 tests passed in each
  lane; the plain lane declares one expected Qt skip.
- Full plain discovery: 3,957 tests passed with 485 expected skips in 348.312
  seconds.
- Full real offscreen-Qt discovery: 3,957 tests passed with 3 intentional skips
  in 641.305 seconds.
- Documentation: 536 Markdown and 431 HTML files passed. Test quality reports
  3,923 tests across 179 files, zero hard issues, and the existing 19 structural
  clone groups.
- Compilation, tracked JSON, diff, and worktree safety pass. Reachability keeps
  its known ledger at 1,537 actions, 2,333 reachable items, 168 orphan inputs,
  and 188 unresolved actions.
- Native visual acceptance is not claimed. macOS reported: `The Mac is locked
  and automatic unlock is paused because physical input was detected. Ask the
  user to unlock the Mac manually before continuing.`
