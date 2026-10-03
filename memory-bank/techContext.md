# Tech Context

## Runtime
- Python Anki add-on running inside Anki/AQT.
- Qt UI is accessed through `aqt.qt`.
- Persistent data is stored in Anki collection config via `mw.col.get_config` and `mw.col.set_config`.

## Development Setup
- Source lives directly in an Anki add-ons directory.
- This working copy should live in `addons21/ankiscape_fork`, not the AnkiWeb-managed numeric folder `addons21/1808450369`.
- The canonical checkout is the only AnkiScape checkout allowed inside
  `addons21`. Linked worktrees belong in the sibling
  `Anki2/ankiscape_worktrees/` directory and must be created/audited through
  `python3 tools/worktree_guard.py`; otherwise Anki loads each enabled worktree
  as a separate add-on copy.
- Delegate through Codex's native subagent tools. Give each writer a pooled
  worktree from `tools/worktree_guard.py lease` outside `addons21`.
  The retired Workflows route must not be used. Return a lease only after its
  owner has finished; an absence of open file handles does not prove that.
  On 2026-08-19, a handle-only check caused a live research checkout to be
  removed. Preserve dirty and unmerged worktrees.
- Future AnkiWeb updates may recreate or update `addons21/1808450369`; treat that folder as upstream and manually diff/merge changes into `ankiscape_fork`.
- Public release must use a new AnkiWeb listing rather than reusing
  `1808450369` and declare the original package as a conflict where Anki
  packaging supports it. The hard-coded review link to that original item was
  removed in `3e4a5cb2`. The governing release record is
  `memory-bank/public-release-lineage-and-license-2026-07-17.md`.
- The local working copy is a solo-project git repository on `main`.
- The canonical checkout is the live add-on. Commit maintenance work in its
  assigned worktree. The root uses `tools/promotion_gate.py` to verify the
  candidate and promote the exact accepted tree to local main.
- Product execution uses the MacBook Pro mirror through
  `tools/run_remote_tests.py`. The root owns that mirror and reconciles any
  pending run before sync. Local static inspection does not establish runtime
  acceptance.
- Tests use Python's built-in `unittest`, not pytest.
- `tools/audit_docs.py` reads the Git index and runs only in a Git checkout; the Git-free MacBook mirror's `git ls-files ... exit status 128` is a runner failure, not an audit result.
- `run_tests.py` adds the repository root to `sys.path`; tests and direct probes import `pkg_alias` before package-relative `ankiscape.*` modules.
- `python3 tools/audit_item_reachability.py --json` emits a deterministic declared-route graph. `--rank-roots N` ranks roots by simulated transitive item/action gain, and `tests/test_item_reachability_audit.py` pins the instrument. The audit measures declared routes; check runtime access gates before a claim of player acquisition.

### Bounded operator commands

- Discover moved files without shell globs with `python3 tools/repo_search.py
  'cadence|clock' logic memory-bank --names`. Search contents through the same
  tool; it caps results and columns and excludes giant generated/archive files
  unless `--include-large` is explicit.
- Broad tree searches ended four agents through context exhaustion on
  2026-08-10 and 2026-08-11. Single outputs reached `355.5 KB`, `758.3 KB`, and
  `610.4 KB`. First use `rg --files` to list exact paths. Then search only those
  paths through `tools/repo_search.py`.
- Run focused product tests through the same MacBook runner. For example,
  `python3 tools/run_remote_tests.py "$PWD" plain --select tests/test_remote_test_host.py --expected-tests <n>`,
  where `python3 run_tests.py --count tests/test_remote_test_host.py` prints `<n>`.
  Repeat `--select` for additional selections. The exact count and zero skips
  are required; focused success never replaces full promotion checks.
- Inspect the pinned worktree pool with `python3 tools/worktree_guard.py status --json`.
  Return leases through the guard; it refuses gate markers and uncertain lease
  identity before detaching a checkout.
- Keep long test and audit output in separate logs with `python3
  tools/run_logged.py --label <lane> -- <complete command>`. The wrapper
  preserves the command's exit code, prints a bounded tail, and reports the
  full temporary-log path without relying on zsh's read-only `status` name.
- Check undefined names and unused locals in the combat facade with
  `uvx ruff check --no-cache --select F821,F841 logic_pure/logic_pure_combat_engine.py`;
  broad F811 checks are noisy because the facade repeats re-exports.
- Locate this checkout's installed Anki source with
  `.venv-qt/bin/python -B -c "import sysconfig; print(sysconfig.get_path('purelib') + '/aqt')"`;
  report a missing environment instead of searching the whole filesystem.
- Delegation briefs must state the assigned files, allowed actions, evidence
  and acceptance checks. A read-only brief must prohibit checkout writes.
- Before selecting the next slice, read `memory-bank/goal-priority-matrix.md`
  and the newest `memory-bank/pickup-*.md`. Use the supporting packet from
  `python3 tools/memory_bank_queue_packet.py
  <repository-or-worktree-root> [<root> ...]`; the packet does not replace
  those selection records. The
  deterministic packet defaults to a 32,768-byte UTF-8 cap, retains repository
  line references, and reports every source omitted or truncated by either a
  context limit or the byte cap; raise `--max-bytes` only deliberately.
- Treat a packet-size record as a fixpoint because `activeContext.md` and
  `progress.md` enter the packet. Rebuild twice after each count edit until the
  size is stable, especially when digit width changes. Keep the SHA-256 outside
  packet sources so the digest does not become self-referential.
- Import `pkg_alias` before direct `ankiscape.*` probes, or set
  `PYTHONPATH="$PWD"` for a harness outside the checkout. Run the equipment
  generator directly or as a module; its `--game-root` is the external
  `/Users/ArmanTarkhanian1/Downloads/game-main` checkout, and
  `data/cfg/items.yml` is relative to that external root rather than this repo.

### Parallel quest and family work

Quest definitions have lived in per-quest modules under `data/quest/` since
`5c87ba05` (2026-09-05); `data/quest_data.py` is a re-export facade. Give
parallel quest writers different modules, and never give two writers one shared
module such as `data/quest/stage_cleanups.py`. The history below records why:
before the split, quest repairs were batched by distance in one file. The
alphabetical batch two containing Carnillean Rising, Deadliest Catch,
Dealing with Scabaras, and Demon Slayer produced conflicts in three of four
branches, left the merged tree unable to import, and required a dedicated
13-minute merge agent. The distance-batched follow-up used Shield of Arrav at
2617, Priest in Peril at 3309, Holy Grail at 5252, and Dwarf Cannon at 9535,
with a smallest gap of 692 lines, and had zero `data/quest_data.py` conflicts.
Prefer quests outside the entry-3.32 route-gate class so a landed repair is
finishable.

Every quest branch also re-pins the seven values in
`tests/test_item_reachability_audit.py`; that conflict is expected and must be
resolved by re-measuring the merged tree. In the distance-batched follow-up,
merged `reachable_item_count` was 2392 while branches held 2390 and 2383, and
merged `seed_item_count` was 1145 while branches held 1143 and 1136. No branch
contained the merged truth.

Keep complex family briefs to one family per agent. On 2026-07-27, both
Troll Invasion + Shattered Heart and Mage Training Arena + Temple Trekking
overflowed Sol's context, although the same two-family shape had completed
Tears of Guthix + Enchanted Key on 2026-07-26. Both failed runs left a
`feat: complete X` commit written before review fixes were applied; one
"complete" claim still had three unapplied MEDIUM findings. Use targeted greps
and no whole-file re-reads, never trust a dead agent's final commit message, and
diff its commit against the last reviewer report. A successor in the same
worktree can recover from a findings-list brief.

### Family-branch integration

Never resolve a family branch's code conflicts by textual union. Three
integrations on 2026-07-27/28 interleaved parallel additions at import blocks,
dispatch chains, sanitizer and migration chains, and panel construction anchors.
The result included truncated functions, imports inside other imports'
parentheses, and duplicated guard chains; twice this broke at least six files,
and once the broken merge reached main and prevented the owner's Anki from
loading.

When main has moved by more than documentation since the family branch fork:

1. If a trial merge conflicts in code, run `git merge --abort` immediately. Do
   not leave main with markers or hand-union the hunks there.
2. Rebase the branch onto main in its worktree with a dedicated Sol agent. Keep
   both semantic additions, run `ast.parse` on every resolved Python file, keep
   migration chains in numeric order, renumber forked migrations, union asset
   JSON dictionaries with main winning key clashes, and make version tests
   assert `CURRENT_CONFIG_VERSION`.
3. Require both test lanes green in the worktree and
   `git merge-tree --write-tree main HEAD` to exit clean. Only then merge on
   main, and rerun the default lane on main before reporting the family landed.

After a merge is reverted on main, a plain re-merge drops the reverted changes;
rebasing gives them new commit IDs and avoids that history trap.

### Long-running background processes

Long plain background shells are not durable in this environment. On 2026-08-15
at 00:37, 01:40, and 02:10 PDT, three long-running background Bash tasks, Codex
exec runs and an SSH watcher, were killed externally with no user message;
foreground calls and short background tasks survived. A plain background
`codex exec` dies with its shell, losing 15-30 minutes of agent time even though
repository edits survive and the session can be resumed with
`codex exec resume --last`.

For a run expected to exceed about 10 minutes, launch it detached with
`nohup ... & disown`, send output to a scratchpad log, write the final report to
a scratchpad file with `-o`, and poll that report file from a cheap disposable
background loop. The detached process can finish and commit even if every
polling shell is reaped.

### Fast Qt UI loop (no Anki restart)
- A dedicated `uv` venv at `.venv-qt` (git-ignored) has `aqt` installed, which bundles PyQt6.
- This lets us build the *real* dialogs headlessly instead of iterating by restarting Anki.
- Pattern (see `tests/test_main_menu_widget.py`):
  - `QT_QPA_PLATFORM=offscreen` so Qt runs without a display.
  - Monkeypatch `QDialog.exec` to capture the live dialog and return immediately (otherwise `exec()` blocks).
  - Monkeypatch `ui.get_config_bool` to control flags like developer mode.
  - Drive the actual widgets (`setCurrentRow`, `.click()`, `processEvents()`) and assert on the resulting widget tree (panel header text, etc.).
- Run it with:
  - `source .venv-qt/bin/activate && QT_QPA_PLATFORM=offscreen python tests/test_main_menu_widget.py`
- These tests are skipped automatically under the plain `run_tests.py` env (no `aqt`), so the core suite stays Qt-free.
- This loop caught the Skills-hub `_select_skill` closure-shadow bug in under a second; prefer it over manual Anki restarts for UI-behavior regressions.
- Offscreen Qt remains a fast regression harness, not visual acceptance. For
  asset/UI closure, fully close any modal, confirm the Anki process actually
  terminates, relaunch, decline unrelated update prompts, and inspect the
  native compositor result. A modal-blocked quit can leave the old Python
  process and stale assets looking deceptively current.

### Optional cloud test lane
- When ChatGPT Work or Codex cloud is included in the existing ChatGPT plan at
  no extra cost and is easy to initialize, use it as a preferred optional test
  lane for pure Python logic, quest and data work, migrations, audits, no-Qt
  integration tests, and offscreen Qt tests whose packages install reliably.
- Cloud results supplement local closure. Keep final loading in the real Anki
  profile, interactive GUI and visual checks, packaging and installation
  checks, and macOS-specific checks local.
- Existing dirty-tree, worktree-safety, and closure gates apply unchanged in
  both environments. Do not add paid cloud infrastructure or invent a
  cloud-only substitute for an unavailable check.

## Testing Coverage
Existing tests cover:
- core game logic and level/XP math
- probability helpers
- storage migration/default data shape
- settings toggles and UI gating
- hook registration dry-runs
- JavaScript injection contracts
- a no-Qt integration smoke test for package loading and hook flow

## Debugging
- Debug logging is centralized in `core/debug.py`.
- Logging is disabled by default.
- `ANKISCAPE_DEBUG=1` enables logs for local debugging (Developer Mode also enables it in-app).
- Logs are written near the package as `ankiscape_debug.log` and rotate automatically.
- The Skills hub emits `hub.*` trace lines (`hub.select_category`, `hub.skill_row`, `hub.select_skill`, `hub.render_panel`). A fired `hub.skill_row` with no following `hub.select_skill`/`hub.render_panel` means a click was misrouted rather than a Qt/signal failure — that gap is exactly how the closure-shadow bug was found.

## Constraints
- Code must remain importable outside Anki/Qt for tests.
- Anki runtime imports should be guarded where possible.
- UI behavior should be optional and resilient; add-on failures should not interrupt studying.
- Storage migrations must be idempotent.
- New Python code should be fully typed where practical, especially new public helpers and data models.

## Package Management
The add-on has no runtime package dependency. If one becomes necessary, use `uv` unless the project adopts another tool explicitly.

Developer-only scripts can use `uv run` inline script metadata when optional tooling dependencies should not become add-on runtime dependencies. `tools/fetch_assets.py` uses this pattern for Pillow-based PNG normalization.

## Source Data (full pre-EOC parity)
AnkiScape targets RuneScape immediately before EOC, with a strict cutoff of **2012-11-20**. The 2011Scape rev-667 source remains a strong baseline for unchanged systems, but 2012 content is a substantial required layer rather than a negligible exception. The project-wide evidence and blocking rules live in `memory-bank/pre-eoc-source-verification-standard.md`; the `ankiscape-skill-expansion` skill supplies the working expansion workflow.

- **The OSRS wiki is NOT a 2011 source.** OSRS branched from a 2007 backup; treat OSRS data as 2007 baseline + OSRS-only additions, useful only as a cross-check for 2007/2011-unchanged content.
- **Baseline implementation evidence:** the local `2011Scape/game` emulator source (Apache-2.0, client rev 667 = Oct 4 2011; upstream `github.com/2011Scape/game`) at `/Users/ArmanTarkhanian1/Downloads/game-main`. It is authoritative only for mechanics unchanged between that snapshot and the cutoff; later content and changed mechanics require pre-EOC 2012 evidence.
- **Historical semantics:** literal wikitext from exact pre-cutoff RuneScape Wiki `oldid` revisions, backed by dated Wayback captures where page histories or transcluded dependencies are unavailable.
- **Dated cache cross-checks:** the six OpenRS2 disk caches listed in `memory-bank/pre-eoc-source-verification-standard.md` (revisions 727, 728, 729, 736, 741, 742; a seventh archive, revision 652, sits in the cache directory but is not part of the standard). They can prove client-side identities and configuration present in a particular build—item/NPC/object names and IDs, enum/struct/param rows, options, sprites/models, interfaces, scripts, varbits—but normally cannot prove server-side XP, random rolls, quest gates, drop rates, action timing, or economy behavior. `tools/query_openrs2_cache_configs.sh` and `tools/query_openrs2_interfaces.sh` read the Java launcher from `JAVA_BIN` (default `/opt/homebrew/opt/openjdk@25/bin/java`) and the Darkan core jars from the local Gradle cache; the scripts pin the Darkan version (2.0.5 when verified on 2026-09-16).
- **Darkan:** use the fidelity-revamped implementation as server-mechanics evidence only after reconciling it with pinned pre-EOC sources. A modern Darkan commit is a reconstruction, not automatically period proof. Wait when the necessary high-fidelity behavior or corroborating history does not yet exist.

Seven tools read the Darkan thread's checkout at
`/Users/ArmanTarkhanian1/Documents/2012scape with bots/` by absolute path:
`audit_citation_drift.py`, `build_pre_eoc_quest_catalog.py`,
`generate_construction_data.py`, `generate_npc_shop_data.py`,
`generate_achievement_diary_data.py` through its harvest input,
`harvest_achievement_tasks.py`, and `harvest_music_log.py`. Every one is
read-only there. That checkout belongs to another team, so never write to it and
never run a mutating Git command in it. Two tools pin exact commits, so a
rebase, a force-push, or a garbage collection in `darkan-world-server` can break
an AnkiScape citation audit. `tools/generate_construction_data.py:101` and
`tools/audit_citation_drift.py:153-155` reach that repository through `git -C`,
which no working-directory scan can observe; detect such a reader by matching
full process argument strings.

Generator output identity is proved with `--check`, never a hand-built
`find | shasum` manifest, whose hash changes with the working directory and path
spelling. `tools/generate_smithing_data.py --check`,
`tools/generate_summoning_catalog.py --check`, and
`tools/generate_achievement_diary_data.py <harvest> --items-yml <items.yml> --check`
regenerate in memory, compare bytes with every file a write would touch
(including `generated/source_digests.json`), name each differing file, print
`OUTPUT_CHECK: <n> of <m> files unchanged`, and exit 1 on any difference.
Cite that line and exit code as the proof.

Woodcutting backend parity data lives in `data/woodcutting_data.py`, with a detailed audit at `memory-bank/source-audits/woodcutting-2011scape-2026-06-01.md`. It stores raw 2011Scape low/high chop chances and hatchet ratios, then lets `logic_pure/logic_pure_gathering.py` adapt them to Anki review cadence.

Mining backend parity data lives in `data/mining_data.py`, with a detailed audit at `memory-bank/source-audits/mining-2011scape-2026-06-01.md`. It stores raw 2011Scape low/high Mining chances, respawn-time data, pickaxe roll cadence, scoped simple historical targets, gem-drop tables, tradability, and Mining bonus metadata consumed through worn equipment. Storage config version 8 migrates old display-name Mining targets to stable IDs; storage config version 10 moves passive bonus ownership into `player_data["equipment"]`.


Crafting backend parity data lives in `data/crafting_data.py`, with a detailed audit at `memory-bank/source-audits/crafting-2011scape-2026-06-03.md`. It stores stable recipe IDs, source family/station metadata, real requirements/outputs, corrected 2011Scape XP values, and notes for input-starved content; the Kanban owns its acquisition gaps. Storage config version 11 migrates legacy display-name `current_craft` values to stable IDs.

Smithing backend parity data lives in `data/smithing_data.py`, with detailed audits at `memory-bank/source-audits/smithing-2011scape-2026-06-01.md` and `memory-bank/source-audits/cannonball-smithing-implementation-2026-07-10.md`. `tools/generate_smithing_data.py` emits 9 ordinary smelt recipes, 158 anvil recipes, and the separate source-backed cannonball furnace process. Storage config version 9 migrates old `current_bar` saves to stable `current_smith` recipe IDs and normalizes legacy `Adamantite bar`/`Runite bar` inventory keys to source item names.

Equipment backend data lives in generated `data/equipment_data.py`. `tools/generate_equipment_data.py` combines checked-in `data/smithing_data.py`, the external 2011Scape checkout's `/Users/ArmanTarkhanian1/Downloads/game-main/data/cfg/items.yml` equipment blocks, and `data/mining_data.py` Mining bonus items. Storage config version 10 adds flat `equipment` state, removes `owned_equipment`, and normalizes combat level/exp defaults so equipment gates use the real levels trained by unified Combat.

Feathers enter through live NPC shop stock and Combat drops. The temporary
`scavenge_chicken_feathers` Utility bridge documented in the dated
`memory-bank/source-audits/feather-utility-2026-06-15.md` was retired during the
shop-economy integration pass and must not be re-added.

Firemaking data lives in `data/firemaking_data.py`, with the audit at
`memory-bank/source-audits/firemaking-2011scape-2026-06-16.md`. It stores 13
local-2011Scape burnable targets, stable target IDs, input item IDs, source XP,
`Ashes` output metadata, raw source low/high lighting odds, and explicit
deferred bonfire/fire-spirit notes. Runtime review behavior adapts the source
lighting roll in `logic_pure/logic_pure_production.py`; storage config version 12 adds
`firemaking_level`, `firemaking_exp`, and `current_firemaking`.

Runecrafting data lives in `data/runecrafting_data.py`, with the audit at
`memory-bank/source-audits/runecrafting-2011scape-2026-06-17.md`. It stores
standard rune, combination rune, tiara binding, pouch, and Wicked hood feed
metadata from the local 2011Scape Runecrafting source. `data/quest/definitions/free/rune_mysteries.py`
stores Rune Mysteries, and `data/quest/ledger.py` stores the one-time Wicked hood claim. Runtime review behavior
lives in `logic_pure/logic_pure_runecrafting.py`; storage config version 15 adds
`runecrafting_level`, `runecrafting_exp`, `current_runecrafting`,
`current_quest`, `quests`, `quest_points`, `claims`, `wicked_hood`,
`runecrafting_pouches`, and `item_charges`.

## Asset Scraping (icons)
`tools/fetch_assets.py` pulls one wiki icon at a time and records provenance. Every fetcher writes `assets_provenance.json`, so run fetchers one at a time (`systemPatterns.md`, "Asset provenance writes are serialized"). For pre-EOC RuneScape content, pass `--source rs3` so a same-named modern OSRS file cannot silently win. Use OSRS art only after independently proving that exact art belongs to the target era. Two practical asset gotchas remain:

- **Skill icons use period highscores art.** Every skill icon `icon/<skill>_icon.png` is the period RuneScape Wiki `<Skill> icon highscores.png`, as `assets_provenance.json` records. Fetch a new skill icon the same way so the skill rail stays uniform.
- **Item sprites render small unless they fill the frame — fix it in the asset, not at runtime.** Wiki item sprites are tightly cropped (e.g. an arrow is a thin diagonal, and Flax's real art is only ~30x23 inside a 64x64 file). Historically `--size N` normalized by `thumbnail((N,N))` then centering on a transparent NxN canvas, which *preserved* those transparent margins — so at the fixed 28px list icon box the visible sprite was much smaller than the legacy bundled icons (full-frame photos that fill the box edge-to-edge). The fix is to bake a trim into the PNG so the UI just does `QIcon(path)` like everything else (a brief experiment with per-paint runtime cropping was reverted: it scanned the 1000–1500px crafted photos pixel-by-pixel and beachballed when opening Crafting). Two pieces keep assets display-ready:
  - **Scrape time (new fetches):** `tools/fetch_assets.py` trims the alpha bounding box (`getchannel("A").getbbox()`) *before* thumbnail/pad, so freshly fetched icons fill the frame. Lossless — only removes invisible pixels.
  - **Existing assets / batch fix:** `tools/trim_icons.py` audits and trims small padded sprites (`<= 256px`) across every top-level UI asset family. It is idempotent and skips large full-frame photos, where trimming would change the intended composition. Run it with `/opt/homebrew/bin/python3` (Pillow) or `.venv-qt/bin/python` (the `QImage` fallback) after adding sprites; `tests/test_ui_asset_normalization.py` fails if a new top-level family is omitted or any small asset retains transparent margins.
  - **New downloads:** `tools/fetch_assets.py` crops invisible margins before applying its optional maximum dimension. The `size` argument is a maximum visible-art box, not a request to re-center the art on a padded square canvas.
  - The UI renders normalized assets with a plain `QIcon(path)`. The UI does no runtime cropping.

### Woodcutting asset wiring (the log/hatchet/nest fetch)
- **Batch driver:** `tools/fetch_woodcutting_assets.py` (`uv run …`) fetches the whole Woodcutting manifest through one rate-limited `HttpWikiClient` so provenance is recorded per file and a single failure doesn't abort the rest. Re-run with `--force` to refresh.
- **Logs reuse `trees/`.** The `trees/<Name>.png` files *are* the log item sprites (see `WIKI_TITLE_OVERRIDES`: `Oak` → `Oak logs.png`). So `constants.LOG_IMAGES` just re-keys those files by log item name (`Oak logs` → `trees/Oak.png`) for the Bank/Stats registry — no second fetch. New tree rows only needed `Achey` (Achey tree logs) and `Hollow` (Bark).
- **Hatchets resolve on RuneScape Wiki, not OSRS.** OSRS calls them "axe"; the 2011 naming is "hatchet". Fetch them explicitly with `--source rs3`.
- **Hatchets / nests / seeds live in `woodcuttingitems/`**, keyed by `constants._asset_slug(name)` and wired via `WOODCUTTING_EXTRA_ITEM_IMAGES`. Both `LOG_IMAGES` and that map are existence-guarded so `missing_required_asset_paths()` (asserted empty by tests) never trips on an unfetched item.
- **Ivy uses the Choking ivy interface icon.** Ivy has no inventory/log item, and `File:Ivy.png` (OSRS) is a full castle-wall *screenshot*, not an icon. The usable art is `File:Choking ivy icon.png` (RS3) — fetched into `trees/Ivy.png` so the (XP-only, no-output) row still shows a vine icon. Egg bird-nests and bird's eggs stay iconless (wiki titles don't resolve; vanishingly rare drops). Nest *ring* contents reuse the existing crafted ring sprites.

### Utilities and Activities row icons
- No-XP activity rows use dedicated `activityicons/` PNGs instead of relying only on output-item material art. The row contract is `UTILITY_ACTIVITY_DATA[activity_id]["icon_path"]`.
- The Qt Utilities and Activities target lists prefer `icon_path` and fall back
  to `UTILITY_ITEM_IMAGES` for output-producing rows. Missing icons therefore
  degrade to output art or a text-only row without changing action behavior.
- The distinct surface cards reuse the provenance-tracked
  `questitems/toolkit.png` and `agilityitems/agility_arena_ticket.png` sprites.
  Qt scales both through the same 28-by-28 `KeepAspectRatio` contract as skill
  and target icons; no duplicate synthesized artwork is checked in.
- Fetch activity-row icons with `uv run tools/fetch_assets.py <item> --out activityicons/<activity_id>.png --wiki-title <File title> --size 64`, then confirm `assets_provenance.json` contains the `activityicons/` key.
- `assets_provenance.json` records each activity icon's source wiki and file title; Soft clay, Wool, and Flax come from the RuneScape Wiki.

### Firemaking asset wiring
- `tools/fetch_firemaking_assets.py` derives the Firemaking-only asset manifest
  from `firemaking_data.FIREMAKING_TARGETS` and uses the shared
  `tools/fetch_assets.py` client/provenance writer.
- The shipped skill icon `icon/firemaking_icon.png` is the period RuneScape
  Wiki `Firemaking icon highscores.png`, as `assets_provenance.json` records.
- Most logs reuse existing Woodcutting log art via `LOG_IMAGES`. Firemaking-only
  inputs plus Ashes live in `firemakingitems/` and are wired through
  `FIREMAKING_ITEM_IMAGES`: `ashes.png`, `arctic_pine_logs.png`,
  `eucalyptus_logs.png`, `curly_root.png`, and `cursed_magic_logs.png`.
- Provenance is recorded in `assets_provenance.json`.

### Runecrafting asset wiring
- `tools/fetch_runecrafting_assets.py` derives the Runecrafting manifest from
  `data/runecrafting_data.py` and uses the shared `tools/fetch_assets.py`
  client/provenance writer.
- The shipped skill icon `icon/runecrafting_icon.png` is the period RuneScape
  Wiki `Runecrafting icon highscores.png`, as `assets_provenance.json` records.
- Runes, talismans, tiaras, pouches, the Wicked hood, and Binding necklace live
  in `runecraftingitems/` and are wired through `RUNECRAFTING_ITEM_IMAGES`.
- Rune/Pure essence reuse Mining ore art.

### Prayer passive asset wiring
- `tools/fetch_prayer_assets.py` derives Prayer materials and passive-item rows from `data/prayer_data.py` and `data/prayer_passive_data.py`.
- Its fetch path is explicitly restricted to `RS3_WIKI`; do not restore the shared OSRS-first fallback for these pre-EOC assets without independent exact-period art proof.
- Bonecrusher and Ectoplasmator live at `prayeritems/bonecrusher.png` and `prayeritems/ectoplasmator.png`; `tests/test_urns.py` requires `source_wiki == "rs3"` for both provenance rows.

### Herblore asset wiring
- `uv run tools/fetch_herblore_assets.py` derives its manifest from the live,
  already-filtered `CLEAN_TARGETS + UNF_TARGETS + FINISHED_TARGETS` catalog.
- The row outputs are fetched through the RS3-only source path. The skill
  rail `icon/herblore_icon.png` is the period RuneScape Wiki
  `Herblore icon highscores.png`, as `assets_provenance.json` records, not
  modern RS3 `Herblore detail.png`.
- `HERBLORE_ITEM_IMAGES` is existence-guarded and target metadata looks up each
  row's output item, so clean herbs, unfinished potions, and finished potions
  render their own sprites.

### Thieving target portraits

- `tools/fetch_thieving_assets.py` owns the cutoff-aware 19-person manifest and
  writes portraits into the existing normalized `combatenemies/` family.
- `THIEVING_NPC_IMAGES` overrides representative loot art only for pickpockets,
  Menaphite thug, and the locked Lletya elf. Stalls and safes still use their
  object/output images.
- The Watchman and locked Lletya elf use explicitly named historical renders
  uploaded after cutoff; they are presentation-only exceptions and do not
  establish mechanics.
- The ordinary top-level alpha-normalization audit covers these files; no
  Thieving-specific runtime crop or scale helper exists.

### Reviewer context actions

- `core/review_context.py` owns pure, registry-shaped projection and sanitization for
  short-lived reviewer decisions; Qt never infers a feature's pending state.
- `ReviewContextActionStrip` is a sibling of ReviewHUD, not a permanent menu
  setting. It renders at most three actions, collapses additional families
  behind a queue badge, and hides completely when no context is pending.
- Explicit choices use the direct-command undo stack. Ignored safe-default or
  remembered choices resolve inside the next answered card's atomic snapshot,
  so review undo restores the pending decision and RNG state.
- Storage config version 45 adds sanitized per-family remembered choices,
  introduced with The Pit's `Take XP / Gamble` family; stable family IDs allow
  later contract-owned surfaces without feature-specific Qt inference.

## Retained standalone utilities

These scripts have no caller in code, tests or other tools. They stay for manual use, so this list is their caller record: a caller search that finds a tool only here has found a retained utility, not dead code. A finished one-off (such as the retired tier-package migration) is deleted instead of listed.

- **Cutoff-era asset fetchers.** `uv run tools/fetch_<name>_assets.py --dry-run` resolves every manifest row on the wiki without writing; drop `--dry-run` to write, and add `--force` to replace existing files. Run them one at a time, because each writes `assets_provenance.json`. `tools/fetch_brawling_gloves_assets.py` has no dry run and takes `--force` and `--size` (default 64). The others: `tools/fetch_barbarian_assault_assets.py`, `tools/fetch_castle_wars_assets.py`, `tools/fetch_combat_hud_assets.py`, `tools/fetch_daily_challenges_assets.py`, `tools/fetch_dominion_tower_assets.py`, `tools/fetch_enchanted_key_assets.py`, `tools/fetch_fishing_trawler_assets.py`, `tools/fetch_fist_of_guthix_assets.py`, `tools/fetch_gnome_restaurant_assets.py`, `tools/fetch_mage_training_arena_assets.py`, `tools/fetch_managing_miscellania_assets.py`, `tools/fetch_mobilising_armies_assets.py`, `tools/fetch_pest_control_assets.py`, `tools/fetch_pyramid_plunder_assets.py`, `tools/fetch_ranging_guild_assets.py`, `tools/fetch_shades_of_mortton_assets.py`, `tools/fetch_shattered_heart_assets.py`, `tools/fetch_sorceress_garden_assets.py`, `tools/fetch_soul_wars_assets.py`, `tools/fetch_tears_of_guthix_assets.py`, `tools/fetch_temple_trekking_assets.py`, `tools/fetch_treasure_trails_assets.py`, `tools/fetch_varrock_museum_assets.py`.
- **Offscreen Qt renderers for visual review.** `.venv-qt/bin/python tools/render_<name>_ui.py`, with optional `--width` and `--height`. Multi-state renderers take `--output-dir`, default in brackets: `tools/render_barbarian_assault_ui.py` (`/tmp/ankiscape-barbarian-assault-ui`), `tools/render_castle_wars_ui.py` (`/tmp/ankiscape-castle-wars-ui`), `tools/render_court_cases_ui.py` (`/tmp/ankiscape-court-cases-ui`), `tools/render_great_orb_project_ui.py` (`/tmp/ankiscape-great-orb-project-ui`), `tools/render_pest_control_ui.py` (`/tmp/ankiscape-pest-control-ui`), `tools/render_ranging_guild_ui.py` (`/tmp/ankiscape-ranging-guild-ui`), `tools/render_shades_of_mortton_ui.py` (`/tmp/ankiscape-shades-of-mortton-ui`), `tools/render_soul_wars_ui.py` (`/tmp/ankiscape-soul-wars-ui`), `tools/render_stronghold_player_safety_ui.py` (`/tmp/ankiscape-stronghold-player-safety-ui`), `tools/render_trouble_brewing_ui.py` (`/tmp/ankiscape-trouble-brewing-ui`), `tools/render_tzhaar_fight_pit_ui.py` (`/tmp/ankiscape-tzhaar-fight-pit-ui`), `tools/render_varrock_museum_ui.py` (`/tmp/ankiscape-varrock-museum-ui`). Single-card renderers take `--output`: `tools/render_barrows_ui.py` (`/tmp/ankiscape-barrows-ui.png`), `tools/render_dagannoth_kings_ui.py` (`/tmp/ankiscape-dagannoth-kings-ui.png`), `tools/render_fight_caves_ui.py` (`/tmp/ankiscape-fight-caves-ui.png`), `tools/render_penguin_hide_and_seek_ui.py` (`/tmp/ankiscape-penguin-hide-and-seek-ui.png`), `tools/render_vinesweeper_ui.py` (`/tmp/ankiscape-vinesweeper-ui.png`). These require `--output`: `tools/render_help_center_ui.py` (`--tab`, `--query`, `--theme`), `tools/render_shop_provider_ui.py` (`--provider`, `--coins`, `--spikes`), `tools/render_stats_ui.py` (`--skill`, `--theme`).
- **Dominion Tower harvester.** `python3 tools/harvest_dominion_tower.py [--pages monsters|rewards|all] > /tmp/dominion_bosses.json` prints the pre-EOC infobox fields of the tower's bosses and rewards as JSON.
- **Frozen combat comparators.** `tools/combat/compare_enemy_attack_rolls.py` (`--baseline`, `--candidate-sha256`, `--inventory`, `--output`, `--preflight`) and `tools/combat/compare_dragonfire_damage.py` (`--baseline`, `--candidate-engine-sha256`, `--candidate-specials-sha256`, `--inventory`, `--inventory-sha256`, `--output`, `--preflight`) compare the current engine with a frozen baseline on the test host. Their baselines are archived out of tree; `memory-bank/evidence/combat-enemy-attack-rolls-2026-09-05/SUMMARY.md` and `memory-bank/evidence/combat-dragonfire-damage-2026-09-08/SUMMARY.md` locate them.

## Manual Testing Target
Manual verification should happen inside Anki when runtime behavior changes. Browser-based Pinchtab testing is only relevant if the change introduces browser-rendered surfaces that can be exercised outside Anki.

## Operator environment and evidence paths

- The citation-drift audit uses committed HEAD blame; edit and revert commits change citation provenance, so audit committed trees (`tools/audit_citation_drift.py:193`).
- As of 2026-10-02, `/Users/ArmanTarkhanian1/Downloads/game-main` is an extracted source archive with `data/cfg/items.yml` but no `.git`; check the input before relying on this host state and retain file hashes when Git provenance is unavailable.
- Every worktree test command must set its working directory explicitly; agent shell defaults can select the canonical checkout. For collection discrepancies, compare the imported module path and collected test IDs from the same checkout before attributing a cause (`tools/run_remote_tests.py` takes the source checkout as its first argument).
- As of 2026-10-02, the logged `/opt/homebrew/bin/jq` executable is absent on this host; check availability before relying on it and use Python JSON parsing for source probes.
- Raw quest-audit packets live under the common Git directory in `ankiscape-promotion-evidence/<producer-commit>/<original-path>`; each audit SUMMARY.md names its manifest (`source-audits/genuine-quest-actions-2026-09-05/SUMMARY.md`).
- As of 2026-10-02, `tools/.cache/pre_eoc_quest_catalog` is ignored; check cache availability before source generation and supply explicit research inputs because linked worktrees do not inherit ignored caches.
- Linked worktrees share the common Git directory and its stash reference; isolate staged verification without stash operations that affect other worktrees.
- zsh does not split scalar file lists on spaces; use arrays for multiple path arguments and quote glob-bearing arguments.
- The slop-gate can refuse different defect classes on successive attempts; retain its full verdict and do static spacing, import and complexity checks before the first commit without changing gate rules.
- zsh expands unquoted glob-bearing options and paths before a command runs; quote literal patterns or use `rg --files` to find exact paths.
- As of 2026-10-02, the `/opt/homebrew/bin/pyflakes` shim names absent `/opt/homebrew/opt/python@3.12/bin/python3.12`; check the interpreter before relying on it. A stderr-only shim failure is not a clean check; use `uvx pyflakes` when the shim is broken.
- The test runner is root `run_tests.py`, not `tools/run_tests.py`; find exact files with `rg --files` and keep source reads within the output budget.
- Verified by the orchestrator at 2026-10-02 18:27: in Claude Code agent shells, `grep` is a shell function from the Claude shell snapshot that runs ugrep 7.8.4, and a bounded-context regex such as `.{0,90}PATTERN.{0,90}` fails with "exceeds complexity limits"; in Codex shells and plain zsh, `grep` is `/usr/bin/grep` (BSD grep 2.6.0). Use `rg -o` or `tools/repo_search.py` for bounded context in either shell.
- `tools/worktree_guard.py add` defaults `--start-point` to `main`; a branch stacked on a slice must pass `--start-point <family-branch>`, or its brief must require a plain merge when histories have diverged instead of `git merge --ff-only`.
- Wiki research requests must send `User-Agent: AnkiScape parity audit`; never put the owner's identity or email in a public User-Agent.
- In PyQt6, `QStyleOptionViewItem.icon` returns a live reference; save `QIcon(opt.icon)` before assigning a new icon to the option.
