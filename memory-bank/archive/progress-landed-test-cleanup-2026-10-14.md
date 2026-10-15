# Landed assertion and method cleanup checkpoint

Historical completed work, preserved verbatim from progress.md. Current source and native queues stay in activeContext.md and their source checkpoints.

Root verified main `ca859eb0ef06a0b298d25bcedd9338a1120afabc` clean at 2026-10-04T04:24:05.550171+00:00. Seven October 3 landings are on main: documentation `06480995`, S01 `046d5f53`, S03 `da02e004`, S12 `58438c4d`, assertion trims `d2aa35d2`, covered-method deletions `28481d9295db918396d5d0188f69c1ea36f102b5` and documentation `ca859eb0ef06a0b298d25bcedd9338a1120afabc`.

The ten assertion trims landed at `d2aa35d20d7b8ef18f2af42f88018641b439a8c8` through the official land command after all nine promotion checks passed. The exact receipt records `remote_lanes=true` and `plain_only=false`. Both lanes ran 5223 tests: plain 453.956s with 581 skips; Qt 673.591s with 7 skips. Root verified all nine final test-file hashes on main. No test method was removed in that slice.

Current review of all 614 historical nominations yields 601 keep, 10 landed assertion trims and 3 landed method deletions. Sol and GLM agree on each deletion; root verified the actual methods, fixtures and surviving fault assertions. Of 35 covered nominations, 32 stay. Firemaking stays because its independent fixture and lane gap remain.

The deletion operator passed ten refusal canaries without writes. It removed three methods across three files, with 24 net lines removed. Whole-module AST comparisons show only these method deletions. All three broader methods and the Firemaking file remain unchanged. The three-method deletion slice landed at `28481d9295db918396d5d0188f69c1ea36f102b5` through the official land command. All nine promotion checks passed. Both lanes ran 5220 tests: plain 461.986s with 581 skips; Qt 677.356s with 7 skips. The exact receipt records `remote_lanes=true` and `plain_only=false`. Root verified all three final test-file hashes on clean main.

The fresh coverage subset contains 146 cases, with 21 plain skips and no Qt skips. Independent raw-map verification passed. This subset is not a whole-suite coverage map.


## Official historical-asset timestamp landing — 2026-10-14

**Historical asset timestamps — 2026-10-14:** [Repair812e0ec1](../source-audits/asset-cutoff-landed-2026-10-14.md) officially landed through its exact full remote gate. Both independent reviews accept; plain5330/595.358s/580skips and Qt5330/804.317s/5skips passed. Main is clean; nothing was pushed.

## Quest refresh retry allowlist — 2026-10-03

The retry allowlist and concrete transient-error fixtures are committed at `2592a56d2e95d20c0927a09f4db8452df814524f`. PermissionError and certificate-validation URLError raise after one request with no sleep or cache publication. Generic OSError and URLError reasons do not qualify as transient failures. The behavior and recount probe passed on the current tree; complete output is `retry2-retry-recount-probe.log` in the established promotion evidence folder.
The catalog remains unchanged against base `60d7bd83`. Recounting the documented oldids found 6 `item_rewards[].source` references and 4 `stage_requirements[].source` references, as recorded in `tools/generation/quest_sources.md`. The unchanged remote inventory selects 53 tests for the builder, catalog and refresh controls; final MacBook execution requires `--expected-tests 53`.

Source2592 is not a main ancestor. Root verified both production and behavior-test blobs identical to fully gated main812e0ec1 on2026-10-14; [the byte binding](/Users/armantarkhanian/Documents/ankiscape-goal-evidence-2026-10-14/quest-refresh-allowlist-main-binding.json) closes the tooling implementation history without claiming the original53-case focused execution.

## Dated catalog tooling checkpoints — preserved on2026-10-14

## Quest catalog retained inputs — 2026-10-02

Assigned tooling slice `goal/quest-catalog-reproducible-2026-10-02`, base `60d7bd83`. The builder reads checked-in `tools/generation/quest_sources.json.gz`: retained wiki responses and parsed emulator journals, wearable-item flags and NPC lookup tables. Reviewed quest-specific variants still come from `tools/combat/quest_stat_sources.json`. No generated catalog row changed. Missing retained inputs fail without fetching replacements. Live Darkan parsing helpers remain available to the combat-gap audit.

Both required rebuild commands exited 0 with no catalog diff. The offline regression passed with absent emulator roots and denied network; the equipment control rebuild also reproduced its checked-in file. The count command is `python3 run_tests.py --count tests.test_pre_eoc_quest_catalog_builder tests.test_quest_catalog` because `tools/run_tests.py` does not exist. It selected 49 tests. MacBook focused plain: `Ran 49 tests in 1.632s`, `OK`, exit 0. The final full plain command and its result are recorded in `remote-full-plain.log` in the evidence directory below.

Commands, complete output, snapshot manifest and input/output hashes are under `/Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/.git/ankiscape-promotion-evidence/goal-quest-catalog-reproducible-2026-10-02/`.

## Quest catalog review fixes — 2026-10-02

NPC pins use paths relative to game-main and the Darkan world server; rendering restores canonical provenance and original field order. The builder remains offline. The pin is 6,805,262 bytes, down from 6,895,694 bytes. Retained tables: 16 local NPCs, 133 Darkan NPCs, 159 wearable entries and 9 journals; local rejected ambiguities remain.
`tools/generation/refresh_quest_sources.py` restores wiki, Kotlin NPC, Darkan ambiguity, journal and wearable extraction. It records emulator commits and hashes for contributing files. Offline regeneration with an absent input pin and blocked sockets produced identical pin bytes. Canary requests verified the anonymous User-Agent, cutoff and retry; missing cache and mismatched catalog gates refused publication.
Both required rebuild commands exited 0 with no catalog diff. The focused count is 49 from `python3 run_tests.py --count tests.test_pre_eoc_quest_catalog_builder tests.test_quest_catalog`; MacBook execution uses `--expected-tests 49`. The socket-level network guard replaces the ineffective urllib patch. Remote-host notes now describe provenance roots accurately.
All 19 inherited post-cutoff citations are listed in `tools/generation/quest_sources.md`; `memory-bank/papercuts.md` retains this source debt. Catalog rows and fixed test baselines did not change.
Review verification commands, reproduction logs, source manifest, safety probes and MacBook focused/full plain results use `review-*` files under `/Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/.git/ankiscape-promotion-evidence/goal-quest-catalog-reproducible-2026-10-02/`.
The unchanged pre-commit gate rejects a new root tools file; the refresh CLI lives under tools/generation, beside the pin loader. Parser control flow is flat; the builder is smaller than the reviewed slice.
Canonical NPC and journal paths precede pprint so mirror-path lengths and spaces cannot change bytes. The offline regression and refreshes through emulator-root aliases reproduce the catalog and pin with sockets blocked.
MacBook focused plain, with `--expected-tests 49`: `Ran 49 tests in 1.583s`, `OK`, exit 0 (plain-1790998782-f42118f5). The initial failed mirror regression and the source-root canaries remain in the review evidence; tests and baselines were not weakened.
Final MacBook full plain ran once: `Ran 5159 tests in 458.033s`, `OK (skipped=579)`, exit 0 (plain-1790999517-29e0d72a).

## Quest refresh error handling and retained provenance — 2026-10-02

MediaWiki error bodies now fail before cache publication, including cached errors. Transport retries cover connection resets or refusals, timeouts, incomplete reads, HTTP 429 and HTTP 5xx; all other failures raise immediately. Current-revision fallbacks emit the page title.
The manifest records only contributing-file hashes and emulator commits; complete scan digests, counts, trimming and the second scan are removed. The pin changed only in source_revisions: 6,805,262 to 6,805,024 bytes. A second offline refresh with denied sockets reproduced every pin byte.
Both catalog rebuilds passed git diff --exit-code with no generated catalog change. The socket guard has a positive connection control in the same patch context. Nested item reward and stage requirement citations are documented.
Local builder and refresh controls passed 16 tests. The focused MacBook selection includes the existing builder/catalog tests and new refresh controls; python3 run_tests.py --count reports 52. MacBook focused plain passed with --expected-tests 52: `Ran 52 tests in 1.621s`, `OK`, exit 0 (plain-1791004624-5c47395c). The full plain lane ran once: `Ran 5162 tests in 455.744s`, `OK (skipped=579)`, exit 0 (plain-1791006058-4cdd154c). Complete evidence uses review2-* in the established promotion evidence folder.
The code fix is c1b0a9dbc648fa0133991895e8e7001de9e6fd39; its unchanged pre-commit hook passed. Source hashes remained identical across both MacBook lanes. Shared mirror queue delay is recorded in papercuts.md.

These are historical source-run qualifications. Current main812e0ec1 includes byte-identical refresh code and behavior tests from final candidate2592, with its own accepted full gate. The original focused results and inherited citation debt remain qualified; this move neither claims a missing old run nor waives a source debt.
