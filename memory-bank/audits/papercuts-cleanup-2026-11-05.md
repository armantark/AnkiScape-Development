# Papercut cleanup — 2026-11-05

Worktree: `goal/papercuts-2026-11-05`. Initial source: `c710813faa75528ea2619740a3bf5de198539692`. Final open-log source: `faf5994930596bfd433c887968f328259b4fb10d`.

Measured open log: **793 → 782 lines** (`wc -l memory-bank/papercuts.md`). Moved 12 entries verbatim with `tools/memory_bank/move_papercuts.py` into `memory-bank/papercuts-fixed-2026-11-05.md`. Two cleanup incidents were appended; the source-root commit refusal was repaired and moved, while the output-budget recurrence remains open. The append tool also normalizes trailing empty lines.

Implemented repairs: complete the two dark-capture palettes, honor ANKISCAPE_GAME_MAIN for NPC shop generation, and accept qualified metric selections when the bare name is file-unique. No gameplay, generated catalog, save schema, product interface, fleet file, hook or guard changed.

## Closed causes and evidence

| Cause | Entries | Repair or current-code check |
|---|---:|---|
| Incomplete dark capture palettes | 3 | Set missing row/button colors; 14 palette/selection tests passed after red regressions. |
| NPC generator ignored the configured source root | 1 | Honor ANKISCAPE_GAME_MAIN; 33 source-input tests passed after a red digest-binding regression. |
| Qualified metric selection refused | 1 | Accept only exact, file-unique qualified names; 11 metric tests passed after a red CLI regression. |
| Recompressed historical asset bytes | 1 | Existing uncached retries and SHA-1 verification checked; 29 tests, 3 Pillow skips. |
| Wrong historical wiki move | 1 | Current source requests ledir=newer, lelimit=1 and advances the move timestamp. No network check. |
| Mixed Qt/runtime imports in dye fixtures | 1 | Existing module restoration and alias retention checked; 4 tests passed. |
| Dispatcher RNG leaked to later tests | 1 | Existing callable/state cleanup checked; 51 dispatcher/undo/Fight Caves tests passed. |
| Earned inventory normalized after the undo snapshot | 1 | Existing save/load before the snapshot checked; Pirate hook fixture passed 1 test. |
| Worktree lacked repository rules | 1 | git ls-files --error-unmatch AGENTS.md succeeded; file read. No rules content changed. |
| Source-root commit grew an oversized file | 1 | Resolution belongs to source_inputs.py; generator remains 1257 lines and the normal hook accepted the commit. This incident was added and closed during cleanup. |

## Checks actually run

- Palette regressions failed before repair; palette/selection modules passed 14 tests.
- Source-root regression failed before repair; NPC source-input module passed 33 tests after the final module-boundary repair.
- Qualified-method regression failed before repair; function-metrics module passed 11 tests.
- Asset URL/downloader modules passed 29 tests, with 3 Pillow-only skips.
- Dye fixture module passed 4 tests; dispatcher/Slayer-undo/Fight Caves union passed 51; Pirate hook fixture passed 1.
- Combined focused run: **Ran 143 tests in 33.075s; OK (skipped=3)**. Log: `/tmp/ankiscape-papercuts-final-check-2026-11-05.log`.
- Direct-script CLI smoke: python3 tools/generate_npc_shop_data.py --help exited 0 without source/output access.
- Code inspection verified earliest-post-cutoff wiki moves; git ls-files verified tracked AGENTS.md; wc verified the shop generator stayed at 1257 lines.
- The source-bound inventory audit passed with 778 dated entries, no missing/extra/repeated assignments, and 2 separately retained non-dated entries. Documentation audit passed (1148 Markdown and 2 HTML files).
- Papercut line-preservation check passed against the initial source. No remote lane, promotion gate, native Anki run, real profile database, real player save, push or merge was used.

## Remaining entries by primary cause

The source-bound JSON inventory accounts for every dated incident; its two non-dated entries remain separately recorded. Counts below include both forms. Broad categories preserve composite incidents when any cause remains. Classification is not proof that an old incident is fixed.

| Cause | Entries | Why open |
|---|---:|---|
| Output built without an aggregate budget | 186 | Oversized agent reads and diagnostics; the bounded repository reader already exists, but agents bypass it. This includes the new cleanup-startup incident. A tool change cannot close these operator recurrences. |
| Guessed paths, symbols or selectors | 161 | Guessed paths, symbols and selectors belong to agent operation. Existing inventory and strict-selector tools refuse invalid input; blanket aliases would hide mistakes. |
| Assumed data shape or representation | 74 | Ad hoc research/proof readers assume incompatible record shapes. A shared typed evidence-reading contract is a separate design; no historical packet was repaired or replayed. |
| Native observation, lifecycle or Qt verification | 65 | Native Anki, macOS Qt/offscreen behavior and GUI ownership need dedicated native verification. Product interface changes are outside this task. |
| Record composition, formatting or quality-hook rejection | 45 | Formatting, record composition and quality-hook refusals remain as recorded. Larger product/module decomposition and fleet guard policy are outside this cleanup; constraints remain enforced. |
| Shell expansion or command construction | 40 | Shell expansion, command construction and status masking are agent/fleet launcher mistakes. Existing correct commands are not a repository defect that warrants a compatibility layer. |
| Fixture or test environment differs from runtime | 35 | Surviving fixture/environment incidents include external source archives, interpreter dependencies, real-save schema validation and route-specific fixtures. Closing them needs isolated source/native fixtures or a broader shared-fixture design. |
| Asynchronous sequencing or resource ownership | 35 | Cross-process sequencing and shared resource ownership remain. Cross-Mac mirror coordination and gate/landing handoff need a protocol across tools and the Sol loop; no remote lane was used. |
| Evidence identity, provenance or binding | 32 | Evidence identity, provenance and binding incidents require the original external proof packets and a retention/receipt design. Existing successful product checks were preserved. |
| Unchecked CLI or API contract | 23 | Invalid CLI/API use and intentionally unsupported operations remain open. Conditional-class metric omissions originate in fleet instrument tables, which were not changed. |
| Provider, process or runtime limits | 23 | Provider capacity, quotas, OS permissions and launcher/runtime limits belong to Codex/providers/fleet or the host environment. |
| Search scope and bounded misses | 23 | Bounded search stops and misses are correct tool signals. Removing those stops would hide incomplete reads; operator query selection remains open. |
| Product, layout or source fidelity debt | 20 | Gameplay, interface, quest/source fidelity and product architecture debt are excluded from this task. |
| Worktree capacity or shared promotion lock | 18 | Worktree capacity and active promotion locks are intentional machinery. No cap, lock or guard was weakened, and no worktree was changed. |

Total: 780 open entries across 14 primary cause groups. The line count includes headings and blank lines.

Stop boundary: further repairs need a broader evidence/source/fixture or cross-process design, dedicated native access, product changes excluded by this brief, or ownership outside this repository. Historical records were kept open rather than closed by age.
