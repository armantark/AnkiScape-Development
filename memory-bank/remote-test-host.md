# MacBook remote verification host

The headless test mirror is on `Armans-MacBook-Pro.local` at
`/Users/armantarkhanian/ankiscape-remote-test-host`. It is a disposable mirror,
not a canonical checkout and not an Anki add-on directory.

## On-screen computer use

The owner's standing direction from 2026-07-31 is: "Use the MacBook Pro for
onscreen work as needed." Connect with
`ssh ArmanTarkhanian@armans-macbook-pro`; use the tailnet name because mDNS is
unreachable. The laptop-local Codex binary is
`/Applications/ChatGPT.app/Contents/Resources/codex`. Its first GUI run needs
Screen Recording and Accessibility approval on the laptop screen. For
AnkiScape, this laptop is the pass-6 prober host; the original setup and role
record remains in `memory-bank/pass5-triage-2026-07-31.md`.

Per-slice native Anki checks run through that laptop Codex CLI over SSH with
its computer-use tool, against a frozen copy of the tree under
`/Users/armantarkhanian/ankiscape-native-mirror/<commit>/`. Never start one
while a gate lane runs on the MacBook: one was part of the load when the Qt
lane passed its 1300-second cap on 2026-09-23. Doorbell the Darkan restoration seat before
and after each GUI run, because both seats share the one screen.

Run the active full promotion procedure from the promotion worktree:

```bash
python3 tools/promotion_gate.py run <promotion-worktree> --remote-lanes
python3 tools/promotion_gate.py land <promotion-worktree>
```

`--remote-lanes` changes only the two serial test-lane commands. The promotion
controller still runs documentation, test-quality, reachability,
worktree-layout, clean-tree, and diff checks locally, while locks, logs,
evidence, exact-commit checks, and landing state remain in the canonical Git
common directory. Omitting the flag keeps the supported local default.

For focused verification, use the checked-in runner directly from any local
AnkiScape worktree:

```bash
/opt/homebrew/bin/python3 tools/run_remote_tests.py "$PWD" plain
/opt/homebrew/bin/python3 tools/run_remote_tests.py "$PWD" qt
```

The runner uses exactly
`ssh -o BatchMode=yes -o ConnectTimeout=10 armans-macbook-pro '<remote command>'`,
rsyncs to `/Users/armantarkhanian/ankiscape-remote-test-host/ankiscape_fork`, and excludes
`.git`, `__pycache__`, `.venv-qt`, and `ankiscape_debug.log*`. After sync, it links
the mirror's `.venv-qt` to the existing remote environment at
`/Users/armantarkhanian/ankiscape-remote-test-host/.venv-qt`. Both lanes check that
interpreter before sync because the surface guard uses it in either lane. The
old `repo` mirror and existing reports remain intact. It launches the
lane through `nohup`, writes logs and completion reports under
`/Users/armantarkhanian/ankiscape-remote-test-host/reports`, and polls those
files. Dispatches started on this machine share the fixed mirror, so the runner
holds an exclusive local flock at `~/Library/Caches/ankiscape-remote-test-host.lock`
through rsync and polling while the local dispatching process lives. A promotion
gate with `--remote-lanes` takes that lock itself before its lanes, waits at most
3,600 seconds for it, logs the wait, and holds it across both lanes. Its lane runs
inherit the held descriptor, so focused runs queue behind the gate and the fixed
lane limits count only each lane's own sync and execution. The flock does not coordinate a dispatcher
on another machine and cannot outlive the local process. If the local poller is
interrupted or times out, its detached `nohup` MacBook lane can continue after
the lock is released; a later dispatch can then sync or run while that orphan is
active and fail spuriously. Run-specific IDs keep logs and reports separate and
prevent false evidence mixing, but an operator must reconcile an orphaned lane
before retrying. A successful summary must report at least 4,506 discovered
tests and at least 3,994 active plain tests or 4,503 active Qt tests, where active
tests equal `tests - skipped`. There is no absolute skip cap: legitimate Qt-only
tests can increase plain skips while active plain coverage stays constant.

## Python environments

The Studio's canonical `.venv-qt` was Python 3.13.5. Its exact 2026-08-19
`pip freeze` is checked in as `tools/remote_test_host_requirements.txt`. Static
import inspection found that the tests directly import `aqt` in 14 files,
`PyQt6` in one file, and `anki` in one file; the remaining pins are their
runtime dependencies. The laptop uses Homebrew Python 3.14.6, and every frozen
wheel installed successfully.

Build the laptop environments after the repository mirror exists:

```bash
ssh -o BatchMode=yes -o ConnectTimeout=10 armans-macbook-pro '/opt/homebrew/bin/brew install ripgrep openjdk@25'
ssh -o BatchMode=yes -o ConnectTimeout=10 armans-macbook-pro '/opt/homebrew/bin/python3 -m venv "$HOME/ankiscape-remote-test-host/.venv-qt" && "$HOME/ankiscape-remote-test-host/.venv-qt/bin/python" -m pip install --retries 5 -r "$HOME/ankiscape-remote-test-host/ankiscape_fork/tools/remote_test_host_requirements.txt"'
ssh -o BatchMode=yes -o ConnectTimeout=10 armans-macbook-pro 'mkdir -p "$HOME/ankiscape-remote-test-host/plain-site" && /opt/homebrew/bin/python3 -m pip install --target "$HOME/ankiscape-remote-test-host/plain-site" --retries 5 -r "$HOME/ankiscape-remote-test-host/ankiscape_fork/tools/remote_test_host_plain_requirements.txt"'
```

The isolated `plain-site` contains Pillow 12.3.0. Do not use `pip install
--user`: Homebrew Python 3.14.6 rejects it with
`error: externally-managed-environment` even when `--user` is supplied.

## Source and cache mirrors

The full lane also reads local source and cache fixtures. Keep these laptop
paths populated from the Studio copies:

- `/Users/armantarkhanian/ankiscape-remote-test-host/sources/game-main`
- `/Users/armantarkhanian/ankiscape-remote-test-host/sources/darkan-world-server/developer-information/npcList.txt`
- `/Users/armantarkhanian/ankiscape-remote-test-host/sources/darkan-world-server/developer-information/beasts.txt`
- `/Users/armantarkhanian/ankiscape-remote-test-host/sources/darkan-world-server/data/npcs/combatdefs`
- `/Users/armantarkhanian/Library/Caches/codex/2012scape-openrs2/extracted/{652-2011-06-08,727-2012-07-24,741-2012-11-04,742-2012-11-07}`
- `/Users/armantarkhanian/.gradle/caches/modules-2/files-2.1` entries for Darkan core 2.0.5, fastutil 8.5.15, log4j-api 2.20.0, and log4j-core 2.20.0

`tools/run_remote_tests.py` preflights these paths, ripgrep, Pillow, Java 25,
and the Qt imports before it changes the mirror. `tools/generate_equipment_data.py`
and `tools/generate_smithing_data.py` honour `ANKISCAPE_GAME_MAIN`;
`tools/build_pre_eoc_quest_catalog.py` honours both `ANKISCAPE_GAME_MAIN` and
`ANKISCAPE_DARKAN_WORLD_SERVER`. Generated provenance remains pinned to the
caller's logical source path so mirroring does not rewrite checked-in data.
Other source-reading generators, harvesters, and gap tools still use
Studio-only source paths.

## Proven result

The 2026-08-19 laptop run against the 4,144-test main corpus completed both
lanes:

```text
Ran 4144 tests in 125.215s
OK (skipped=499)
```

```text
Ran 4144 tests in 295.116s
OK (skipped=3)
```

The directly measured 2026-08-27 main baseline established the current floors:

```text
Ran 4506 tests in 251.835s
OK (skipped=512)
```

```text
Ran 4506 tests in 446.244s
OK (skipped=3)
```

Those results establish 4,506 discovered tests, 3,994 active plain tests, and
4,503 active Qt tests as the current-main minimums.

The 2026-08-27 pending UI branch measured the current invariant directly. Its
plain lane ran 4,507 tests in 247.142s with 513 legitimate skips, leaving 3,994
active tests; the obsolete absolute skip cap rejected the result only after
`OK`. Its Qt lane ran the same 4,507 tests in 444.064s with three skips, leaving
4,504 active tests:

```text
Ran 4507 tests in 247.142s
OK (skipped=513)
```

```text
Ran 4507 tests in 444.064s
OK (skipped=3)
```
