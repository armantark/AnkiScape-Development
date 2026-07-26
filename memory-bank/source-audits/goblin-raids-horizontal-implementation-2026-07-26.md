# Goblin Raids Horizontal Implementation Source Audit

Date: `2026-07-26`

Schema version claimed: **87**.

## Scope decision

This family implements the settled owner answer in
`recon-coverage-closure-2026-07-18.md` item 6: "Evil Tree discovery surface on
the answered-card world clock composes with a live multi-enemy engaged-target
raid encounter (goblin roster + Hollowtoof) ending in the sourced spoils."

It also ships the Goblin Village boss loop from the same pinned article. That
loop is not named in the owner answer, but it is the only route to the Goblin
cower shield, whose effect is the most exactly-sourced reward in the family — 25%
bonus Attack, Defence and Constitution experience up to 1,000, stated in the
release update itself. Leaving it out would have shipped a family with no
bonus-experience mechanic and an unobtainable period item.

## Sources in required order

### 1. Darkan

**Nothing.** The tree at commit `c95aca409f397cab12c13b6d5269b73f6cd8abe9` has no
goblin-raid content: a case-insensitive search for `goblinraid`, `goblin_raid`
and `hollowtoof` across `src/main` returns no files. The activity released
`2012-10-17`, three weeks before the cutoff, so this is expected rather than a
gap in the search.

### 2. Registered emulator-cited stat blocks

The roster needed no placeholder stats, because AnkiScape already carries the
right ones. The period Goblin Raider is stated to be combat level 2 with 50
lifepoints, and the registered `goblin_level_2_armed` row — cited to game-main's
`goblin_level_2.plugin.kts`, `GOBLIN_4262` — is exactly that. Hollowtoof and the
three village bosses are combat level 5, and `goblin_level_5` carries the
matching offensive stats and bonus block.

`goblin_raids_enemies_pure` therefore builds each roster row from its base and
overrides only the fields a period page states: the display name, the stated
lifepoints, the stated attack style and the examine text. Attack, Strength,
Defence, Magic, Ranged, the bonus block and the drop tables all stay as the
emulator-cited row has them, which is why the placeholder register holds no
roster stat for this family.

### 3. Pinned historical wiki

- `Goblin Raids` oldid `6545250`, `2012-11-09T20:21:45Z`
- `Update:What's Mine is Yours` oldid `6434891`, `2012-10-17T15:08:44Z`
- `Hollowtoof` oldid `6522288`, `2012-11-03T04:29:15Z`
- `Goblin Raider` oldid `6464537`, `2012-10-24T16:33:38Z`
- `Commander Yodri` oldid `6548002`, `2012-11-11T11:02:18Z`
- `Brokeface` oldid `6444343`; `Stinkears` oldid `6447564`; `Lumpnose` oldid
  `6550383`
- `Raider axe` oldid `6464509`; `Raider chainbody` oldid `6464451`;
  `Raider shield` oldid `6464501`
- `Goblin cower shield` oldid `6444335`, `2012-10-19T21:29:09Z`

Sourced facts implemented:

- A server-wide notice gives the latest incursion's location **every thirty
  minutes**. The house review clock runs 240 answered cards to the game day, the
  scale Evil Tree and Shooting Star already use, so the announcement is one every
  **five answered cards**. That conversion is arithmetic on a stated period
  figure, not a placeholder.
- Raids happen at **farms, wood-gathering sites and mines**, and the extra reward
  follows the site: **seeds, logs, ores** respectively.
- Goblin Raiders **accumulate raided material as they shout** and drop everything
  they took when they die. The article's own example is "two logs and one oak
  log" after three shouts.
- **Hollowtoof cannot be attacked** until every ordinary raider is dead, at which
  point he shouts "Now it's my turn!".
- Hollowtoof drops **one Raider set piece per kill, in the order chainbody, axe,
  shield**, and drops the chainbody again once the set is complete — which the
  article itself flags as possibly unintended. Both behaviours ship.
- A sufficiently high-level player may **talk to Hollowtoof before the raiders
  die and receive the whole set**.
- **Commander Yodri** arrives once the raid's goblins are dead and gives an item
  "for every goblin slain" plus a location-appropriate extra.
- **Every fifteen goblins killed inside the village gates summons one of three
  bosses**, and goblins outside the gates do not count. Brokeface is melee,
  Stinkears magic, Lumpnose ranged; all three are level 5 with 120 lifepoints,
  and Lumpnose's maximum hit of 20 is stated.
- Each boss has a chance to drop the **Goblin cower shield**, which grants **25%
  bonus Attack, Defence and Constitution experience up to 1,000 bonus experience
  in total**, after which it is purely cosmetic.
- The **Raider axe requires 8 Attack**. No Defence requirement is stated for the
  chainbody or shield.

Facts read and deliberately not implemented:

- The article records a membership conflict: the release update labels the
  activity members-only while the period NPC infoboxes say `members = No`.
  AnkiScape does not model membership, so nothing was carried either way.
- Death is nowhere described as safe or dangerous. Raids and the village are
  ordinary open-world content, so the family uses the ordinary death pipeline the
  combat burst already applies rather than adding a rule no source states.
- The Falador easy task "Like a Boss" is real period content but belongs to the
  task system rather than this family.
- The client's "- all rank pts"-style wipe has no analogue here; no counter in
  this family is ever reset by a death, because nothing says one was.

## The one cross-cutting change

The cower shield's bonus needed a place to attach. Rather than add a second
experience seam, it rides the one that already exists: `_award_skill_exp` in
`__init__.py`, which the Stealing Creation reward tools already use. The shield's
budget is checked by a cheap hot-path gate before anything is copied, exactly as
`stealing_creation_tool_can_apply_pure` does, so an ordinary review pays nothing
for a shield the player does not have.

## Placeholders registered

Eight, all in `memory-bank/placeholder-values.md`:
`goblin_raids.raid_active_reviews`, `goblin_raids.raider_count`,
`goblin_raids.raided_material_tables`, `goblin_raids.yodri_reward_table`,
`goblin_raids.intimidation_combat_level`,
`goblin_raids.cower_shield_drop_chance`, `goblin_raids.stinkears_max_hit`,
`goblin_raids.raider_set_bonuses`.

Two are worth calling out because they are conflict resolutions rather than plain
gaps. `intimidation_combat_level` exists because the same pinned article gives
two different approximations, "around level 95" and "approx. level 90", for the
same threshold; the lower one is used so the shortcut is not harder than either
statement. `stinkears_max_hit` exists because the engine derives a caster's
maximum hit from melee strength, which is wrong, and Stinkears' page states no
maximum while its same-level, same-lifepoints sibling Lumpnose states 20.

## Asset provenance

`tools/fetch_goblin_raids_assets.py` installs six images, all with pre-cutoff
upload timestamps recorded in `assets_provenance.json`:

| file | source | upload |
| --- | --- | --- |
| `activityicons/goblin_raids.png` | `File:Goblin raid.png` | `2012-11-14T05:37:21Z` |
| `combatenemies/goblin_raids_raider.png` | `File:Goblin Raider.png` | `2012-10-17T18:33:52Z` |
| `combatenemies/goblin_raids_hollowtoof.png` | `File:Hollowtoof.png` | `2012-10-17T17:27:45Z` |
| `combatenemies/goblin_raids_brokeface.png` | `File:Brokeface.png` | `2012-10-17T16:24:34Z` |
| `combatenemies/goblin_raids_stinkears.png` | `File:Stinkears.png` | `2012-10-17T16:25:31Z` |
| `combatenemies/goblin_raids_lumpnose.png` | `File:Lumpnose.png` | `2012-10-17T16:25:05Z` |

The filenames follow `_asset_slug(target_id)` rather than the wiki title, because
that is how `COMBAT_ENEMY_IMAGES` resolves enemy art. Five files were fetched
under their wiki names first, attached to nothing, and were refetched under the
slug; the stale provenance rows were removed with them.

The unnamed village goblin has no wiki image of its own, so `constants.py` falls
its art back to the registered goblin row it inherits its stats from. That is a
four-line addition to the image loop, and `test_goblin_raids` asserts every
roster row resolves to art.

## Test coverage

`tests/test_goblin_raids.py`, 42 tests in nine classes: data and registration,
the world clock, entry, the raid stages, the intimidation shortcut, the village
boss loop, the cower shield bonus, failure paths, the view, persistence, the
command router, and runtime integration. Plus one case in
`tests/test_direct_action_undo_seam.py`.

Nothing under test is mocked. `GoblinRaidStagesTest` clears a whole raid through
the real combat kernel and then claims Yodri's spoils; its last test plays three
consecutive raids to prove the Raider set arrives chainbody, axe, shield and then
wraps. `GoblinVillageBossTest` fights village goblins until a boss is genuinely
summoned and until the cower shield genuinely drops, and a second test keeps
playing until all three named bosses have appeared, so none of them is a row no
player can reach.
