# Pass 15b review fixes, 2026-10-02

## Art cutoff

The 37 release-day-end fetchers and all eleven release-day-midnight fetchers now import `PRE_EOC_CUTOFF` from `tools/fetch_assets.py`. `HttpWikiClient` accepts timestamps less than or equal to its bound, so midnight was not strictly before release day. No midnight fetcher was left unchanged: Cooking, Dominion Tower, Gnome Restaurant, Herblore, Mage Training Arena, Mobilising Armies, Ranging Guild, Shattered Heart, Summoning, Temple Trekking and Troll Invasion.

The Crafting regression exercises the real client and dry-run fetch path with only network responses replaced. OSRS supplies only release-day art; RS3 supplies both historical and release-day art. The historical case must select RS3, and the release-day-only case must fail. Request bounds use the shared constant. The public User-Agent remains `AnkiScape parity audit`.

## Shades of Mort'ton

Tool belt oldid 6538396, `2012-11-06T01:19:10Z`, names Hammer and Tinderbox and general basic-tool use. Its exceptions name other quest interactions, but its literal wikitext does not establish belt use for temple repair or the Shades altar. Shades of Mort'ton oldid 6397774, `2012-10-13T23:44:30Z`, names a regular Hammer or owned Flamtaer hammer for repair and a Tinderbox for the altar; it does not state belt use. General availability is not proof of this specific use. Owner note 6 authorizes quests, Farming and Vinesweeper, without naming this activity.

Decision: revert the entire Shades portion of `987f4bcc`, including the altar-test inventory change; restore the original missing-Hammer test exactly. The Hammer and Tinderbox refusal guards are reachable again and must remain. The belt import is removed. Sources: https://runescape.wiki/w/Tool_belt?oldid=6538396 and https://runescape.wiki/w/Shades_of_Mort%27ton?oldid=6397774 .

## Fremennik shield conflict

Reject automatic replacement of 54 with 56. Fresh literal wikitext confirms that shield oldid 5641898 (`2012-05-22T11:53:12Z`) says 54 without a beta marker. Oldid 5827384 (`2012-06-25T19:52:33Z`) repeats 54 with a beta marker. The review's claim that the only 54 source has a beta marker is false. Quest oldid 6540919 (`2012-11-07T09:46:34Z`) explicitly says 56 for making the shield.

The existing source contract records Darkan `craftShield` supplying commit `adb5dd15fe6272fd3c639d5de698f3633ba117b0` and the dependency on the quest restoration source; this is not established independent corroboration. The evidence hierarchy separates search order from corroboration and gives no automatic priority to a newer quest guide over an older item article. The branch retains 54 while the historical threshold remains unresolved. Remove the unsupported owner-ruling claim and record both values, sources and the current value as an open owner question. No claim of historical conflict closure is made.

Sources: https://runescape.wiki/w/Fremennik_round_shield?oldid=5641898 , https://runescape.wiki/w/Fremennik_round_shield?oldid=5827384 , https://runescape.wiki/w/The_Fremennik_Isles?oldid=6540919 .

## Retained raw responses

All requests used curl with `User-Agent: AnkiScape parity audit`, three retries, and a 45-second timeout. The evidence directory is `/Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/.git/ankiscape-promotion-evidence/pass15b-logic-followups/review-fixes/`.

- `tool-belt.json` SHA-256 `6e86ce8b51c3c88e866910f3ea3992e61c822ae7dc0e718aad34a3b22050ee23`.
- `shades.json` SHA-256 `f88c0cf6fdb66caeeeee0d79f385e8bc1d013e1fa84848abd7d2cc00c2a76a89`.
- `shield-revisions.json` SHA-256 `56ab6ce48932d993772de4a767b505f39b40aac44ae0e3849a25a949a7a9c553`.

Live Darkan provenance check on 2026-10-02: checkout `1912a55cb245cc4410e51b200f9ad4c5e480510f`; `git blame -L 416,427` assigns `craftShield` and its Woodcutting 56 check to `a7e91cb9769642e3e833a523fd5f0688eef21924`. The earlier audit hashes remain labeled as retained audit records. This live supplying commit is used in the owner question; it remains a restoration, not independent period server evidence. The path is `/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/src/main/java/com/rs/game/content/quests/fremennikisles/FremennikIsles.kt`.

## Other review dispositions and verification

Remove the unused production `target_unlock_locked_reasons_pure` import. Delete the redundant Chisel=1 metadata block and name the test for bank-free availability. Restore the carried-Chisel fixture and preservation assertion. The 2026-10-02 20:43 orchestrator ruling drops fix 8: keep both potion calls and the equipment annotation collapsed. Compact the carried-pack assertion without changing its expected items. No tests, audit instruments or pinned baselines were weakened.

Both earlier full MacBook lanes passed in one invocation each, before the final Shades revert and fixes 6–7. The result lines are copied verbatim into `memory-bank/progress.md`; `verification-results.json` records the announced run identities, remote log/report paths and SHA-256 hashes of the complete captured logs.

## Final commit blocked

The asset fixes are committed as `e547be09`. All remaining fixes and the 15-line progress note are staged. Both full lanes passed before the final commit attempt. The unchanged slop-gate rejected the required line growth; no further production/test change or gate bypass was attempted. Exact output:

```text
slop-gate: code files above 1000 lines were grown:
  runtime/runtime_actions_production.py: 1442 lines (was 1439)
  tests/test_runtime_actions.py: 5917 lines (was 5916)
  tools/generate_equipment_data.py: 1415 lines (was 1413)
  -> Split along module seams (a cohesive unit per file), not at an arbitrary line count.
```

## Commit-blocker resolution

The 2026-10-02 20:43 ruling supersedes the formatting request and staged-blocker state above. Fix 8 is dropped, the carried-Chisel assertion remains intact, and all three files are line-neutral or smaller against main and HEAD. The final code snapshot must pass both full lanes again; the final results belong in `memory-bank/progress.md`. No gate or test instrument is changed.
