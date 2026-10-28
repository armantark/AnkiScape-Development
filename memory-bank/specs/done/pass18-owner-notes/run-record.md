# Pass 18 run record

What the build left for the owner: decisions made during the build that he has
not approved, findings outside the tickets, and retro candidates. The landing
sequence is in `run-log.md`; the reviews are in
`/Users/armantarkhanian/Code/ankiscape-pass18/review/`.

## Native checks in real Anki (GPT-6.1 Terra, computer use)

| Run | Head | What it showed |
|---|---|---|
| `native/look-1/` | `32a19006d` | Before the build: queue box 2 rows with a scroll bar; tab arrows together at the right; GE and Bank normal with a 47-item seed |
| `native/look-2/` | `628d4a75e` | Before the build, owner's save copy: Bank rows overlap by about 14 points at the default size |
| `native/check-05-06-07/` | `ac93a440f` | Tab arrows at both ends; "Mix with" on dyes; Utilities mixes orange, green and purple; Wyson sells woad |
| `native/check-08/` | `fbc0c02bb` | Owner's save: 154 item kinds, no overlapping rows at any size |
| `native/check-03/` | `bee35c9c0` | Queue box shows 5 entries with no scroll bar, folds, confirms adds; GE whole with 5 entries; Smithing cut two rows at 720 (fixed in ticket 09) |
| `native/final-check/` | `bbe289398` | Exact counts in one card; Clear stops a hand-started action; Goblin Diplomacy in 9 cards from raw supplies; Smithing rows wrap and survive resizes; GE whole; no crash |

No native run crashed Anki in Pass 18.

## Decisions made during the build, for the owner

1. **Whole lots.** A step that can only make a whole lot (15 arrow shafts from one log) keeps the whole lot, and the entry ends at its count. Ticket 01 had deleted the extra products after their inputs were spent. Default: keep the whole lot.
2. **Wrapped skill rows.** Ticket 09 widened from the GE to every skill target list: long rows wrap onto two lines instead of ending in "...", so rows no longer share one height. This follows the owner's rule that cut text is fixed when seen. Default: keep.
3. **Combat panel layout.** Ticket 10 hid the prayer status line (its only text now is "No prayer points left."), moved two notes into tooltips, and removed "Used " from every Shop result chip. Default: keep.
4. **Wyson's result chip** reads "✓ Pay 20 coins for 2 woad leaves.", because the chip shows the offer's label. A past-tense chip needs a change to `ui/ui_tab_shop.py`, which the commit hook holds at its size.
5. **Duplicate Summoning points.** The Kimi taste review says the follower panel's "Summoning points: n/n" repeats the status line above it. Not changed.

## Findings outside the tickets (not fixed)

- Queue (ticket 01): a barehand Hunter entry never fills; a Dungeoneering entry pauses the queue as it starts; an attack entry against a finisher enemy (desert_lizard, gargoyle, gelatinous_abomination, mutated_zygomite_level_74, mutated_zygomite_level_86, rockslug) never fills; a Construction entry counted in Coins also counts the servant's wage; a Hunter Kit entry counts its 7 tools as 7 items; a gathering entry whose product is set to "drop" never fills.
- Supply steps (ticket 04): a step runs one full batch of its Utility row; the planner reserves nothing for later stages; supplies are checked one stage at a time. The 47 loop briefs name these limits.
- Layout (tickets 03, 08, 09): four pages that use `vertical_scroll` scroll before they need to; the Bank Claims block sits below the page edge at the default size; the Bank grid builds its cells twice on first open; under the macOS-like test style some labels clip (Combat "Current Slayer task only", Magic choosers, the Summoning and Smithing materials lines, "Daemonheim starter expedition"); Summoning and Thieving locked rows wrap their long "— Locked: …" text over several lines.
- Combat panel (ticket 10): the prayer grid shows the general ticks while a pinned preset fights with its own prayers; in Fusion dark, "Book" and "Prayer time" look enabled while "Use prayers" is off.
- From the first native look: Achievements rows draw each line in its own outlined box; the Utilities search box cuts the start of a long search.

## Retro candidates

- Manual native runs and the Sol loop's native lane share no queue or lock for the GUI; the manual runner had to poll `pgrep`.
- The native guard accepts only default save keys, so a real save needs 14 keys removed before it can seed a check.
- The Pass 18 runner's prompt named a default seed that overrode the packet's; one check ran on the wrong save.
- The implementer brief, copied from Pass 17, listed `tests/ui_flows/` as having room and did not ask for the census check; both cost a rebase.
- The shared test mirror handed its lock to the next waiter while an orphaned run (driver gone) still ran, and both waiting lanes exited with "sync blocked".
- Two Sol implementer runs failed on "Selected model is at capacity" minutes after the weekly Codex reset.
- The shared offscreen dark palettes leave `AlternateBase` white, so dark captures paint alternate rows white.
- `job.py` could not run `git commit` ("Operation not permitted").
- `AGENTS.md` names the commit hook by its Mac Studio path, which does not exist on the MacBook.
