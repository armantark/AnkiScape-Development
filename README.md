# AnkiScape (expanded fork)

AnkiScape is an Anki add-on where every successful card review runs one action in a RuneScape-style progression game. You train skills, fight, work through quests, collect items, keep a bank, shop, and chase achievements. The game copies RuneScape as it stood on November 20, 2012, the day before the Evolution of Combat update, so nothing after that date and nothing from Old School RuneScape gets in. It's a fork of the AnkiScape add-on by Wilson Yeh, whose version had four skills, and it has grown well past that. It's one person, me, in my spare time, mostly by running Claude Code and Codex on whatever is left of my monthly quota after other work.

## Install

There is no AnkiWeb listing yet (see [Publishing to AnkiWeb](#publishing-to-ankiweb) for when there will be). Until then you install from this repository. Anki 23.10 or newer is required; development happens on Anki 26.9.

### Option A: copy the folder (simplest)

1. Get the code. Either clone it:

   ```
   git clone https://github.com/armantark/AnkiScape-Development.git
   ```

   or press **Code → Download ZIP** on GitHub and unzip it.
2. In Anki open **Tools → Add-ons → View Files**. That opens your `addons21` folder.
3. Move the code folder into `addons21` and rename it to `ankiscape`.
4. Restart Anki. A small floating button appears in the reviewer, and the review screen gains a skill HUD.

### Option B: install from a zip

1. Zip the **contents** of the code folder so that `__init__.py` sits at the root of the zip, not inside a subfolder. From inside the folder:

   ```
   zip -r ../ankiscape.zip . -x '.git/*' '.claude/*' '.cursor/*' '.venv*/*' '.vscode/*' '.pytest_cache/*' 'memory-bank/*' 'tests/*' 'tools/*' '__pycache__/*' '*/__pycache__/*' '*.log*'
   ```

   The game does not import anything from the excluded folders; they are development material and design notes.

2. In Anki open **Tools → Add-ons → Install from file** and pick `ankiscape.zip`.
3. Restart Anki.

### Updating

Replace the folder (or install the new zip over the old one) and restart Anki. Your progress lives inside your Anki collection, not in the add-on folder, so it survives the swap.

### Two things to avoid

- Keep exactly one copy of the add-on under `addons21`. A second copy, including a git worktree placed there, registers duplicate menus and hooks.
- If you have the original AnkiScape from AnkiWeb (item 1808450369) installed, disable it. Both add-ons read and write the same save data.

## What you get

- A review HUD showing the active skill or activity, its level, and progress, plus XP and item toasts, level-up and achievement popups.
- A Skills hub with a training screen for 19 of the 25 skills. Attack, Strength, Defence, Constitution, and Ranged train through the shared Combat screen. Dungeoneering covers the Frozen floors only.
- Quests with a stage engine and combat encounters, Slayer assignments, minigames and activities, a Grand Exchange with period prices and buy limits, NPC shops, equipment, and a bank.
- Undo-aware rewards. Undoing a review in Anki reverses the game action too.
- An `Actions per review` setting (1 to 10) if you want the game to move faster per card.

All options are under **Tools → Add-ons → AnkiScape → Config** in Anki: the review HUD, floating XP toasts, popups, the floating widget and its corner, actions per review, and a developer mode that turns on debug logs and test actions.

## Roadmap

The table below gives a target for each remaining work layer. The estimates are based on the pace I actually kept between June and September 2026, when skill breadth went from four skills to nineteen. That pace depends on my spare Claude Code and Codex quota, which varies a lot from month to month, so treat the numbers as rough. Where I genuinely cannot estimate something, the table says "unknown", and I mean it. Some things are excluded outright, like a world map, a transportation network, and any post-2012 or Old School content, since I will never build those.

Estimates as of September 2026.

| Layer | What it means for a player | Target |
|---|---|---|
| Remaining skill depth | Dungeoneering beyond the Frozen floors; Slayer bestiary and reward depth | end of 2026 |
| Quest fights | 91 of 293 quest encounters have no combat stats yet and show a "not modelled" notice instead of a fight | end of 2026 |
| Activities, bosses, item routes | Remaining minigames and distractions with their real currencies and rewards; boss instances; every item reachable through some drop, shop, quest, or skill | first half of 2027 |
| Collections | Clue scrolls, the remaining achievement diary rows, a collection log | second half of 2027 |
| Hidden mechanics | Reconcile drop rates and success rolls that no wiki recorded against the Darkan server restoration, once it is stable | unknown (external dependency) |
| Balance and release | Level 1 to 99 pacing pass, save migration and real-profile testing, packaging, the AnkiWeb listing | unknown |

Pace so far: first commit on 2026-05-29, about 2,600 commits by 2026-09-19.

## Publishing to AnkiWeb

AnkiWeb is Anki's official add-on directory, and publishing there would give one-click download, install, and update inside Anki. I won't consider the add-on good enough for that until a few things are true. All 25 skills need to be complete or explicitly excluded with a reason. Quests, activities, bosses, and the economy need to work end to end the same way skills do. Saves need to migrate safely between versions. Wilson needs to have acknowledged the fork in writing, the repo needs an explicit license compatible with AGPL-3.0-or-later, and every shipped image needs a recorded source. The listing would be a new AnkiWeb item under a distinct name, never an update pushed over Wilson's original listing. Until then it's a zip from GitHub.

## Development

### Tests

Core suite (Python's built-in `unittest`, no Qt, no Anki):

```
/opt/homebrew/bin/python3 run_tests.py
```

Qt behavior suite through the checked-in offscreen environment:

```
QT_QPA_PLATFORM=offscreen .venv-qt/bin/python run_tests.py
```

See `README-tests.md` for layout and conventions.

### Documentation audit

```
/opt/homebrew/bin/python3 tools/audit_docs.py
```

Checks every tracked Markdown and HTML file for encoding, fences, local links, and parseable HTML.

### Debug logging

Set `ANKISCAPE_DEBUG=1` before launching Anki or running tests. Logs are written next to the package as `ankiscape_debug.log`, rotate automatically, and are git-ignored.

### Worktrees

Never place a second checkout under `addons21`; Anki loads it as a live add-on. Use `python3 tools/worktree_guard.py add <branch>` to create linked worktrees in the sibling `Anki2/ankiscape_worktrees/` directory, and `python3 tools/worktree_guard.py audit` before and after worktree changes. See `CLAUDE.md` for the full rule.

### Where the design lives

`memory-bank/future-work-kanban.md` is the live work board. `memory-bank/roadmap.md` holds the layer plan behind the table above. Dated audits under `memory-bank/` are historical evidence, not current status.

## License and credits

This repository does not carry a license file yet. AnkiWeb treats add-ons without a stated license as AGPL-3.0, and the fork will add an explicit AGPL-3.0-or-later compatible license before any public release.

AnkiScape was created by Wilson Yeh ([original repository](https://github.com/wilsonhyeh/ankiscape), [original AnkiWeb listing](https://ankiweb.net/shared/info/1808450369)). This fork is independently maintained by Arman Tarkhanian and has diverged extensively in scope, systems, and content.

RuneScape and all in-game names, art, and data are the property of Jagex Ltd. This is an unofficial fan project, not affiliated with or endorsed by Jagex. Item, skill, and NPC images come from the [RuneScape Wiki](https://runescape.wiki); each shipped file's source page and revision are recorded in `assets_provenance.json`.
