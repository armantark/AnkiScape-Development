# AnkiScape (expanded fork)

AnkiScape is an Anki add-on where every successful card review runs one action in a RuneScape-style progression game. You train skills, fight, work through quests, collect items, keep a bank, shop, and chase achievements. The game copies RuneScape as it stood on November 19, 2012, the day before the Evolution of Combat update, so nothing after that date and nothing from Old School RuneScape gets in. It's a fork of the AnkiScape add-on by Wilson Yeh, whose version had four skills, and it has grown well past that. It's one person, me, in my spare time, mostly by running Claude Code and Codex on whatever is left of my monthly quota after other work.

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

## FAQ

### What is the origin of this project?

This is based on [AnkiScape](https://ankiweb.net/shared/info/1808450369) built by Wilson Yeh. I always had the idea of expanding his plugin out to encompass all the skills of RuneScape, so that's exactly what I did once AI got good enough to source all the information for me.

### Why 2012 RuneScape? Why not OSRS or modern RS3?

The time I first played RuneScape was exactly right before Evolution of Combat came out, 2011-2012. I actually, for one, didn't absolutely hate EoC like most people, and it didn't really drive me to quit, just that I was a kid at the time and bounced around from game to game over the years. That being said, 2012 is probably a definitional version of RuneScape that I've never been able to engage with since it's a bygone era, and I wanted to experience it one way or another with this project, particularly while I'm studying on Anki. As for why not a modern vanilla RuneScape: I think both are very expansive in content and have evolved past the simplicity of something that can be easily translatable to an asynchronous format like this. 2012Scape was very simplistic for the most part and can be easily mapped onto discrete actions. I think I wouldn't do it justice if I flattened all the mechanics of more modern RuneScape into this, plus it would expand the content scope to something untenable and unreachable, even if there is a bigger wealth of sources I could pull from in comparison.

### Where are you sourcing your data from?

I'm primarily taking information from [Darkan](https://darkan.org), a 2012 private server of RuneScape ([server code](https://gitlab.com/darkanrs/world-server)), some [2011Scape](https://github.com/2011Scape/game), along with [game caches](https://archive.openrs2.org/caches) from that era, and pinned wiki revisions from just before EoC. Some things, because they are lost content/information, have to be inferred heuristically, which is an unfortunate artifact of that server code truly being lost. Some things I also derive from the modern wikis, but very limited.

### What is your design philosophy? How the heck are you taking RuneScape, which is mostly a synchronous game, and converting it to Anki, which is asynchronous?

If you think about it, RuneScape is a glorified incremental clicker game. I took this idea and ran with it. Anything that requires synchronous input, I've flattened into autonomous actions while still providing the user with enough agency to explore different things and go about his/her own path with the same exploratory "horizontal" progression of the original. This *does* remove *some* of the depth, but ultimately AnkiScape is a means to an end: studying flashcards.

To this end, I've written a few "design pillars," if you will:

1. **Study comes first.** One successful review = one action. The game is quiet enough to not interrupt the flow of studying. One example of a major change regarding this pillar is that inventory management is all automatic, although you can specify exact loadouts in the advanced mode.
2. **Every value has a 2012 source.** See above. I take special care to make sure there is at least one form of evidence, and make it clear when it's an interpolation, and usually only small things like success rolls and catch chances, almost never items, levels, XP, or rewards.
3. **Breadth-first development.** I want a working end-to-end slice before shipping, even if it's just a small version of the skill to start with.
4. **Translation > simulation.** Kind of tying in with earlier points, but I am not aiming to create a 1:1 exact replication of the game. You can play Darkan if you want that. Every game design decision has been carefully mapped onto what would work if you were not paying attention to every minute background detail of the game. There's no world map, no travel. For example, Agility simply makes some actions take a certain amount of cards fewer for movement-heavy actions, rather than having a simulation of walking paths and teleportations.
5. **Similar grinding requirements.** The game is still just as grindy as the real game. I expect it to take several years (rough estimate, of course) even at an average of ~240 cards per day to completely max and finish a character. Pacing is still something I'm actively tweaking, though. However, the user can set actions per review multipliers as he/she wishes to speed up progress.

### Will you ever backport content from modern RuneScapes?

I don't think so, even though I really love post-2012 RS3 questlines. That being said, I have incorporated some basic QoL UI changes from the modern games that I prefer.

### Do I need to know RuneScape?

It would certainly help you to appreciate the nuances, but no, it does not require any knowledge of RuneScape. I have help sections for some of the more complicated parts of the add-on which should hopefully clear things up for anyone new to the game.

### What's your policy on GitHub issues and PRs? If I have issues with game design or bugs or whether something's not clear, etc.

I'm always open to feedback if something doesn't make sense. Just open up an issue or even submit a PR and I'll check.

### What does each Anki card answer option map to in terms of the game? Is there any RNG involved? Do the different answer levels give extra rewards? How does in-game time work?

No, there is no RNG when it comes to picking Again, Hard, Good, or Easy. I specifically decided against that because I think RNG would require too much micromanagement and I don't want to overly influence honest answering. "Again" simply interprets time as if you were idle (in the case of combat, a tick just lapses without any effect on you or the enemy), and the other three options just advance time normally, one simulated action.

There are two levels of "time" in the game: world time, and active training time. Answering "Again" typically advances the world time and not the active training time. For example, say you're chopping wood. If you answer "Again," the world clock, with stuff like Grand Exchange, farming, shops, etc. will progress, but you don't have an action occur like a swing to the tree you're chopping. By default the world clock counts 10 answers as one in-game hour, so a study day of 240 cards moves the world forward one in-game day.

### Is it free?

Yes, it will always be free and open source (mostly due to legality, but anyway...). Feel free to star and share though, and check out my other repos and projects if you want to support me in other ways.

### Does it change my cards or scheduling?

Nope, it doesn't even read those values besides (hopefully soon) calibrating your "per day" average to help pace content, and obviously the answer button you press.

### Does it send data anywhere? Sync? Does it work on mobile Anki? Where is my save?

The add-on itself makes no network calls, but the save does get attached to your collection which does tag along for the ride with your AnkiWeb syncs, so it automatically transfers to other computers you have Anki installed on with sync enabled. I currently do not support mobile for gameplay, and any mobile studying will be lost to the ether, but I do have plans to have progress retroactively sync back to your computer's game data.

### Can I start over?

Not currently with the UI, and because the save syncs to your Anki collection, you cannot simply reinstall the add-on. You have to start an entirely new profile. That being said, I will have functionality to delete a character sooner or later, or even have multiple saves.

### Can I play ironman or other special game modes? What even is ironman? How does the Grand Exchange even work?

Ironman is a game mode where you can't trade with other players to help speed up progress. Everything you do has to be mined/chopped/looted/whatever by your own hand. That being said, this game is not truly multiplayer (I do not have plans for this), so the only way to "trade" is by setting up offers in the Grand Exchange. The Grand Exchange is an entirely simulated market that runs on your computer in the background with every tick, mimicking the real game's Grand Exchange market. You can buy any normally-tradable item on there with the same market limits as the real game. Turning on ironman mode simply disables any Grand Exchange functionality; you can "de-iron" your character but you can't make your character into an ironman. The game will ask you upon the first look at the GE tab what mode you want to play. There are currently no plans for any other official game modes such as bronzeman or hardcore, but I will consider it.

### Where's my player model? Fashionscape?

I don't currently have plans to show anything visual beyond the inventory/bank/equipment items, along with basic icons. Sorry.

### Did you use AI to make this?

Yes, as stated above. I've used plenty of models, mostly GPT models and a bit of Claude, since around May 2026 to contribute to this massive hulking codebase. I often let the models just run unattended for hours at a time to source harvest and implement data based on its source. That being said, I do dogfood the add-on to my own usage, so I'm constantly nitpicking issues and picking up bugs. And as I said, I've taken painstaking care to ensure everything fits to my design philosophy and maintain a proper level of quality. I don't consider this "slop" in the least regard.

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

Add `--processes 8` to run whole test modules in parallel worker processes.

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
