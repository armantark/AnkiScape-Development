# Shallow tools cleanup proof: 2026-10-04

Base: `ca859eb0ef06a0b298d25bcedd9338a1120afabc`.
Branch: `goal/shallow-tools-cleanup-2026-10-04`.
Checkout: `/Users/ArmanTarkhanian1/Library/Application Support/Anki2/ankiscape_worktrees/pool/.treehouse/ankiscape_fork-091389/7/ankiscape_fork`.

The two asset commands use one manifest command in `tools/fetch_assets.py`.
The commands retain their names, script metadata, data imports, root bootstrap, flags and return values.
The shared command preserves manifest order, cutoff, RS3 source, interval, conversions, paths, print output and failure behavior.

Root authorized removal of the gap driver, its prompt and its four dedicated tests.
Root's check covers configured local schedulers and processes, not the whole machine.
Check time: `2026-10-04T07:29:56.212300+00:00`.
Check record: `/Users/ArmanTarkhanian1/Library/Application Support/Anki2/ankiscape_worktrees/.orchestrator/shallow-cleanup-2026-10-04/gap-callers.json`.
The deleted prompt held all live instructions to run the driver.
The historical backlog and dated Jev decision retain their historical references.

## Proof

All logs and disposable probes are in `/tmp/ankiscape-tools-cleanup-2026-10-04`.

| Check | Result | Record |
| --- | --- | --- |
| Isolated command comparison | 16 cases match the base; 24 asset/provenance fingerprints match | `before.json`, `after.json`, `compare_commands.py` |
| Real `fetch_asset` dry-run | Four cases pass; manifests contain 15 and 8 rows; downloads and writes are forbidden | `real-fetch-dry-run.json`, `probe_dry_run.py` |
| Both `--help` commands from `/tmp` | Exit 0; names and flags match | `dominion_tower-help.log`, `gnome_restaurant-help.log` |
| Focused inventory and tests | 121 tests; `Ran 121 tests in 33.018s`; `OK`; zero skips | `focused-proof.json`, `tools-focused-onr_te3b.log` |
| Full plain inventory and tests | 5216 tests; `Ran 5216 tests in 845.130s`; `OK (skipped=579)` | `full-inventory-nmwjrt3h.log`, `full-plain-q9f7ng1g.log` |
| Documentation audit | Exit 0; 895 Markdown and 455 HTML files | `audit-docs-final-rn1ynj6p.log` |
| Test quality | Exit 0; 5181 tests across 331 files; hard issues: 0 | `audit-test-quality-li0jf66g.log` |
| Item reachability | Exit 0; 1674 actions; 2356 reachable items; 161 orphan inputs; 246 blocked actions | `audit-reachability-o58jix30.log` |
| Worktree layout | Exit 0; layout safe | `worktree-layout-oopmao82.log` |
| Compilation and `git diff --check` | Exit 0 | Branch operator output |

Focused command:

```sh
python3 run_tests.py test_fetch_assets historical_assets.test_fetch_assets_source_urls test_dominion_tower test_gnome_restaurant.GnomeRestaurantDataSourceAssetTests test_gnome_restaurant.GnomeRestaurantEntryAndOrderTests test_gnome_restaurant.GnomeRestaurantDeliveryRewardTests test_gnome_restaurant.GnomeRestaurantPersistenceRuntimeTests
```

Use `--count` before the selectors for a fresh inventory.
The full plain command is `python3 run_tests.py`.
The audit commands are `python3 tools/audit_docs.py`, `python3 tools/audit_test_quality.py`, `python3 tools/audit_item_reachability.py --check`, and `python3 tools/worktree_guard.py audit`.
The command probes used no network calls and changed no repository asset or provenance file.
No test, audit, limit or baseline was weakened.

## Not done

The branch Qt lane is omitted under the standing promotion-gate exception.
Root owns both remote lanes on the integrated commit through `promotion_gate.py --remote-lanes`.
This slice ran no remote runner, native Anki session, live profile or browser.
