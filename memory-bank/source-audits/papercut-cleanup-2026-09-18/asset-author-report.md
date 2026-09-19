# Asset maintenance handoff

Recorded: 2026-09-18T13:33:29-07:00

## Result

The three asset tools have source fixes and offline regression coverage. Root must complete acceptance on the MacBook Pro.

Worktree: `/Users/ArmanTarkhanian1/Library/Application Support/Anki2/ankiscape_worktrees/pool/.treehouse/ankiscape_fork-091389/4/ankiscape_fork`

Baseline: `7f736d5c63ca0d301b1789798e75fa2737435f4c`.

## Changes

1. `fetch_asset` skips an existing regular file before wiki access unless `--force` or `--dry-run` applies. It preserves file and provenance bytes. Unknown source fields are `None`, so the generic JSON output uses `null`.
2. Seven display callers use `existing` for a skipped file. Ten source-label expressions changed. The generic JSON output retains honest null values.
3. The Hunter fetcher shares the existing image-owner map through `core/constants_parts/hunter_assets.py`. The registry retains the same map name, values, export list and order. The fetcher excludes shared items from its manifest.
4. The trimmer validates all selected directories before it selects a backend or processes a file. A missing path or file argument exits with an explicit error. The backend error gives the complete Qt command.

No asset or provenance file changed. No dependency, hook, configuration, threshold or surface pin changed in this leaf. Root owns Git and acceptance.

## Verification

- Static syntax passed for all 14 owned Python files.
- The Hunter map declaration has the same abstract syntax tree as the baseline declaration.
- The `skill_assets.py` export-list abstract syntax tree matches the baseline.
- Five offline utility cases passed. They cover the existing-file skip, dry-run resolution, forced replacement, invalid mixed targets, and dry-run/live trim behavior.
- The same rejection cases fail on the baseline utilities in memory. The fetch case raises on unavailable wiki metadata. Both invalid trim target subcases fail the stop requirement.
- A separate inert Hunter manifest check excludes shared names, preserves an unrelated item, and collapses duplicate input.
- The owned-path `git diff --check` passed.

These checks used standard-library-only utility execution, fake clients and temporary files. They did not import product code or make network calls. The Hunter regression in the repository remains pending on the MacBook Pro.

## Root acceptance

1. Run the focused files from the MacBook mirror root with its ordinary interpreter.
2. Run the same files through the real offscreen Qt interpreter.
3. Run the unchanged full source and promotion gates.

Run these commands from the provisioned MacBook mirror root:

```
/opt/homebrew/bin/python3 run_tests.py tests/test_fetch_assets.py tests/test_ui_asset_normalization.py tests/test_module_surface.py
QT_QPA_PLATFORM=offscreen .venv-qt/bin/python run_tests.py tests/test_fetch_assets.py tests/test_ui_asset_normalization.py tests/test_module_surface.py
```

The frozen constants surface and export-order checks must remain unchanged. The five added methods and the strengthened skip method must run.

## Owned files and frozen source bytes

The table records the source after this leaf stopped edits.

| File | SHA-256 |
| --- | --- |
| `tools/fetch_assets.py` | `d2119efa9c9fec578ef1e44295e8c22d577994aa13458004083ede3f8c8344ed` |
| `tools/fetch_hunter_assets.py` | `2fbc4c964edbf3e397c918195b96eef1d3f80fb5ba223bd1e3021f059dfeeb5d` |
| `tools/trim_icons.py` | `e17f849632db18d6ec8dd476ab1ee02ca5735cf63f7be003a192c3211557b6e3` |
| `core/constants_parts/skill_assets.py` | `f163bbb8876f7d2f6e896779c86966ca13f9cd0d82b1a31ea4c7071d79ef7a93` |
| `core/constants_parts/hunter_assets.py` | `4217caeed033497fd0c54fc5bb913c27b973a4eaed8919f6e67f6c76cd3989c8` |
| `tests/test_fetch_assets.py` | `d06843f41acb98e67486d9ba183906567d5c8a81c17fc127fefbbea5212830c6` |
| `tests/test_ui_asset_normalization.py` | `b507d00fc980cd8af8aeff3c892ece8c43fdc8a9a0377d0e8d4c3f25549e361a` |
| `tools/fetch_summoning_assets.py` | `b7b974c37a33f9cc6387611f72020d91c98ed80dfbfb5595d18b91af8badbb2b` |
| `tools/fetch_herblore_assets.py` | `0e4c492b20ffd2255925a27455f9fd974b3cb96fc4c4c11a544a067d5a35f3f6` |
| `tools/fetch_construction_assets.py` | `fb76de018f2c261150471281937e36e84b0c61c588a799b6d0b52e360a28b38a` |
| `tools/fetch_magic_assets.py` | `dd34f6ff9d1dde8ac3b5fcc6470598598eb3bc4bdb9737ba0c38f12b9a842eec` |
| `tools/fetch_pet_assets.py` | `0589e541f8011f6e0e3a703a27cdd447f592495ac5fab3ade4b9336bc1bf7638` |
| `tools/fetch_prayer_assets.py` | `05c672a1e76b3b5b7a1c6d5f179131188638e99afd68b5d14cd5842909923479` |
| `tools/fetch_potion_assets.py` | `9bd14e2470e5ab64735f37365a03bd0b68cc9f4c93cca0a1f86c26ddc557fd8d` |

## Audit friction for the shared papercut log

These were operator mistakes during the read-only audit. Root can append them to the shared log.

- 2026-09-18T13:33:29-07:00 — Combined startup reads exceeded the tool output bound: `Warning: truncated output (original token count: 21343)` and later `Warning: truncated output (original token count: 10406)`. Bounded file reads recovered the source.
- 2026-09-18T13:33:29-07:00 — Asset ownership inspection guessed `core/constants_parts/assets.py` and `data/asset_map_data.py`; both returned `No such file or directory (os error 2)`. `rg --files` located `core/constants_parts/skill_assets.py`.
- 2026-09-18T13:33:29-07:00 — A remote-tool inspection used optional shell glob `tools/remote_tests/*.py`; zsh stopped with `zsh:1: no matches found: tools/remote_tests/*.py`. Exact filename discovery located `tools/run_remote_tests.py`.
- 2026-09-18T13:33:29-07:00 — The first inventory classifier assigned incident 131 twice and stopped with `ValueError: ('permission_safety_boundary', {131})`. The final inventory assigns all 796 starts once and has no gaps.
- 2026-09-18T13:33:29-07:00 — A source audit initially stated that `tools/workflow_manifest_guard.py` was absent. Exact path discovery proved the file exists; the parent received the correction before the inventory was finalized.
- 2026-09-18T13:33:29-07:00 — A surface-test lookup guessed `tests/test_module_surface_contracts.py` and failed with `No such file or directory (os error 2)`. The current test is `tests/test_module_surface.py`.
