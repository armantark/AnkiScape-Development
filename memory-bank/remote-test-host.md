# MacBook remote verification host

The headless test mirror is on `Armans-MacBook-Pro.local` at
`/Users/armantarkhanian/ankiscape-remote-test-host`. It is a disposable mirror,
not a canonical checkout and not an Anki add-on directory.

Use the checked-in runner from any local AnkiScape worktree:

```bash
/opt/homebrew/bin/python3 tools/run_remote_tests.py "$PWD" plain
/opt/homebrew/bin/python3 tools/run_remote_tests.py "$PWD" qt
```

The runner uses exactly
`ssh -o BatchMode=yes -o ConnectTimeout=10 armans-macbook-pro '<remote command>'`,
rsyncs to `/Users/armantarkhanian/ankiscape-remote-test-host/repo`, and excludes
`.git`, `__pycache__`, `.venv-qt`, and `ankiscape_debug.log*`. It launches the
lane through `nohup`, writes logs and completion reports under
`/Users/armantarkhanian/ankiscape-remote-test-host/reports`, polls those files,
and rejects any success below 4,100 tests, a plain success above 500 skips,
or a Qt success above 10 skips.

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
ssh -o BatchMode=yes -o ConnectTimeout=10 armans-macbook-pro '/opt/homebrew/bin/python3 -m venv "$HOME/ankiscape-remote-test-host/.venv-qt" && "$HOME/ankiscape-remote-test-host/.venv-qt/bin/python" -m pip install --retries 5 -r "$HOME/ankiscape-remote-test-host/repo/tools/remote_test_host_requirements.txt"'
ssh -o BatchMode=yes -o ConnectTimeout=10 armans-macbook-pro 'mkdir -p "$HOME/ankiscape-remote-test-host/plain-site" && /opt/homebrew/bin/python3 -m pip install --target "$HOME/ankiscape-remote-test-host/plain-site" --retries 5 -r "$HOME/ankiscape-remote-test-host/repo/tools/remote_test_host_plain_requirements.txt"'
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
and the Qt imports before it changes the mirror. The three source-reading generators exercised by the test corpus honour
`ANKISCAPE_GAME_MAIN` and `ANKISCAPE_DARKAN_WORLD_SERVER`; generated
provenance remains pinned to the caller's logical source path so mirroring
does not rewrite checked-in data. Other source-reading generators, harvesters,
and gap tools still use Studio-only source paths.

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
