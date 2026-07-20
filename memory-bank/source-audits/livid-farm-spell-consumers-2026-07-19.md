# Livid Farm spell consumers — 2026-07-19

## Scope and cutoff

This audit closes the ordinary-Magic registration boundary for the first ten
Livid Farm spell unlocks at the permanent `2012-11-20T00:00:00Z` cutoff. The
owning activity and automatic cumulative unlock ladder remain defined by
`memory-bank/source-audits/livid-farm-loop-2026-07-18.md`.

## Period evidence

The literal pre-cutoff RuneScape Wiki revisions establish:

| Spell | Revision | Period facts used |
|---|---|---|
| South Falador Teleport | `South Falador Teleport`, oldid `6587582`, `2012-11-19T14:13:50Z` | Level 72, 70 XP, 2 Astral + 1 Law + 2 Air, south Falador gate destination, Livid unlock. |
| Repair Rune Pouch | `Repair Rune Pouch`, oldid `6587602`, `2012-11-19T14:14:31Z` | Level 75, 75 XP, 2 Astral + 1 Law + 1 Cosmic, medium/large/giant only, repairs and strengthens even before visible degradation, 500% durability, giant pouch example of 60 rather than 12 uses. |
| North Ardougne Teleport | `North Ardougne Teleport`, oldid `6587632`, `2012-11-19T14:15:42Z` | Level 76, 76 XP, 2 Astral + 1 Law + 5 Water, destination north of East Ardougne bank. |
| Remote Farm | `Remote Farm`, oldid `6587680`, `2012-11-19T14:17:29Z` | Level 78, 79 XP, 2 Astral + 2 Earth + 3 Nature, views every farmable patch and cures any and all diseased patches in one cast. |
| Make Leather | `Make Leather`, oldid `6587732`, `2012-11-19T14:19:21Z` | Level 83, 87 XP, 2 Astral + 2 Fire + 2 Body, tans five hides of any kind per cast, excludes Yak-hide conversion. |
| Disruption Shield | `Disruption Shield`, oldid `6587745`, `2012-11-19T14:19:50Z` | Level 90, 97 XP, 3 Astral + 3 Blood + 10 Body, nullifies the next player-sourced attack only and has a one-minute cooldown. |
| Vengeance Group | `Vengeance Group`, oldid `6587416`, `2012-11-19T14:07:05Z` | Level 95, 120 XP, 4 Astral + 3 Death + 11 Earth, applies Vengeance to up to 50 players in a 7-by-7 area and shares the 30-second Vengeance cooldown. |
| Teleport to Trollheim | `Trollheim Farm Teleport`, oldid `6587747`, `2012-11-19T14:20:34Z` | Level 92, 101 XP, 3 Astral + 3 Law + 10 Water, teleports next to the Trollheim herb patch, requires My Arm's Big Adventure. |
| Group Teleport to Trollheim | `Tele-group Trollheim Farm`, oldid `6587750`, `2012-11-19T14:22:50Z` | Level 93, 102 XP, 3 Astral + 3 Law + 20 Water, teleports the caster and nearby players to the herb patch, requires My Arm's Big Adventure for caster and recipients. |

`Livid Farm`, oldid `6569596` (`2012-11-17T21:40:18Z`), independently pins
the cumulative ladder, spell order, levels, and spell purposes. Its
`227,120` North Ardougne threshold wins over the individual spell revision's
`227,170` typo because the newer owner-approved activity contract already
resolved the conflict and the live ladder uses `227,120`.

The last pre-EOC Spiritualise Food page history does not survive under its
current title. Its level, XP, rune, name, and Livid-unlock row is supplied by:

- Darkan commit `82e793597923b68f04e8b80e383b2f78a1302959`,
  `src/main/java/com/rs/game/content/skills/magic/lunar/LunarDefs.kt:33-55`;
- Darkan's rev-727-derived `developer-information/enums.txt:53680-53715` for
  spell names, levels, Livid unlock hints, and client sprite identities; and
- `developer-information/enums.txt:63660-63710` for the matching rune-cost
  structs.

The Livid Farm oldid independently corroborates the spell's period existence,
order, unlock threshold, level, and purpose. The Darkan enum supplies:

- Spiritualise Food: level 80, 81 XP, 2 Astral + 3 Cosmic + 5 Body.

## Implementation boundary

Source-ready consumers:

- South Falador and North Ardougne record an explicit direct destination
  transition through the ordinary Magic action result.
- Remote Farm reads the existing Farming patch state and cures every live
  diseased crop atomically in one cast. It remains castable when no patch is
  diseased because viewing patch state is itself the sourced spell function.
- Make Leather follows the existing per-output Magic target pattern and tans
  at most five of the explicitly selected supported hide type. Cowhide may
  become soft or hard leather; Snake hide becomes Snakeskin; and green, blue,
  red, or black dragonhide becomes the matching leather. The ordinary and
  swamp snake hides share AnkiScape's existing `Snake hide` identity. Royal
  dragonhide remains absent because neither its raw nor leather item substrate
  exists in the registry; Yak hides remain excluded by the period source.
- Teleport to Trollheim requires My Arm's Big Adventure, records the Troll
  Stronghold herb-patch destination, and focuses the existing
  `trollheim_herb` Farming patch.

Registered but consumer-blocked:

- Repair Rune Pouch waits on the existing unresolved base pouch-degradation
  counter conflict documented in
  `memory-bank/source-audits/runecrafting-recon-2026-07-14.md`. Applying a
  five-times multiplier to the known-conflicting emulator counter would not
  reproduce the period 60-use giant-pouch result.
- Spiritualise Food waits on period-qualified eligible-food, familiar heal,
  stat-boost, and reuse semantics. Darkan's current handler uses a wall-clock
  cooldown and therefore cannot be copied into AnkiScape.
- Disruption Shield has no monster consumer by source and waits for PvP.
- Vengeance Group and Group Teleport to Trollheim require other players.

These five rows remain ordinary sourced Magic content. Their disabled reason
names the real missing consumer or dependency; they are not put back into an
undifferentiated “future Livid spell set” bucket.

## Tests mapped to evidence

- `tests/test_magic.py` pins the ten spell unlocks, their ordinary-Magic rows,
  levels, XP, rune costs, cumulative Livid unlock gates, and every supported
  Make Leather output.
- The same suite proves the two direct destinations, Trollheim Farming focus,
  all-patch Remote Farm cure, exact five-hide Make Leather transaction, and
  atomic refusal of the five unavailable consumers.
- `tests/test_farming.py` covers the all-diseased-patch Remote Farm helper
  independently of Magic rune spending.
- Existing runtime and metadata suites prove registry-driven selection,
  disabled-row reasons, one-review mutation, undo, XP award, and save behavior.

## Closure verification

- Focused pure/runtime: 102 tests passed.
- Real shown-dialog offscreen Qt: the Livid Magic surface test passed at
  720-by-540 with the longest Make Leather group expanded, a non-null output
  icon, input tooltip text, and no horizontal scrollbar.
- Full non-Qt: 1,810 methods passed with 230 expected environment skips.
- Full real offscreen Qt: 1,810 methods passed with one intentional skip.
- Test-quality audit: 1,810 tests across 78 files, zero hard issues.
- Documentation, compile, diff, and worktree audits passed.
- Reachability remains explicit at 283 orphan inputs and 300 blocked actions.
- Kimi K3 returned `SHIP`. Fable's `REVISE` findings were all accepted:
  shown-dialog geometry, output-icon wiring, source-faithful Trollheim names,
  and selected-hide tooltip copy.
- A restarted macOS Anki process loaded one AnkiScape dialog with
  `Training: Magic`, the normalized Magic icon, `Teleports — Lunar (12)`, and
  `Lunar skilling (21)`. macOS accessibility could not expand the custom tree
  row after the Mac locked; exact expanded-row rendering therefore remains
  proven by the shown-dialog Qt test rather than overstated as live-compositor
  evidence. The user's prior `Cooking` selection was restored and verified.
- Results:
  `memory-bank/status-updates/livid-farm-magic-consumers-results-2026-07-19.html`;
  mobile copy: `https://hbqtpi53phuh.postplan.dev`.
