# Enchanted key treasure hunt

Date: 2026-07-26

Status: **closed for breadth level one.** No value is source-blocked and no
placeholder was needed.

## Scope and cutoff

The post-Making-History treasure hunt as it stood before 2012-11-20: the eleven
buried treasures, the key's temperature readings, the god mjolnirs, the lost-key
replacement, and the key melting after the last find. The Meeting History
time-travel use of the same key is out of scope and belongs to the quest thread.

## Sources

| what | source | pinned |
| --- | --- | --- |
| hunt structure, site list, per-site loot, temperature table, melt rule, replacement | `Enchanted key` | oldid `6554980`, 2012-11-14T08:47:10Z |
| key granted by Erin, quest rewards | `Making History` | oldid `6493057`, 2012-10-29T15:58:17Z |
| notes item, confirmed out of scope | `Enchanted key notes` | oldid `6177669`, 2012-09-01T23:25:40Z |
| treasure coordinates | `darkan-world-server` `src/main/java/com/rs/game/content/quests/making_history/MakingHistory.kt` | local checkout |
| item identity | `Enchanted key`, item 13591 | Darkan `MeetingHistoryState.kt`; game-main `data/cfg/items.yml` |

## Values proven

- Eleven sites. "There are a total of 11 treasure sites to be found."
- Order. "The first treasure site will always be Fremennik Province. After that,
  all other locations are at a random order for each player."
- Per-site loot. All eleven rows were checked against Darkan's table one at a
  time and every row agrees. Two source defects are recorded rather than
  followed: the Grand Exchange row's wikitext displays "15 Law runes" but links
  the words to the Air runes page, and the article's own aggregate reward summary
  contradicts its rows on Earth runes, Fire runes and Steel arrows. The rows win.
- The distance metric. "measured in the number of steps (including diagonal
  steps) it would take to reach the treasure, ignoring any obstacles (this is
  the Chebyshev distance)".
- The eight temperature bands and their thresholds, from the article's own
  table, together with the "Warmer/Colder/Same temperature than last time"
  suffixes. Darkan's thresholds match exactly.
- Digging range. "there is a 9 by 9 square region in which they may dig", which
  is the 4-step band the "steaming" message covers.
- The melt. "Once all the treasure has been found, the key will melt."
- Replacement. "another key can be obtained from Erin for 500 coins, if the
  second quest has not been started."
- The mjolnirs. "In three of the sites, there will the God mjolnirs", at Wayne's
  Chains, Al-Kharid and the Exam Centre, and "This is the only way to obtain
  these unique weapons, other than trading with another player and buying in the
  Grand Exchange."

## AnkiScape abstractions

- **The walking.** The period hunt is positional and AnkiScape has no map, so the
  search is flattened the way Penguin Hide and Seek flattens spotting: the player
  chooses one of the eleven known sites and one answered card is one trip out to
  it. Every reading is still the period ladder over the real coordinates, so a
  wrong guess costs a review and tells the player how far off it was.
- **Consequence, recorded rather than hidden.** Because a search either lands on
  the treasure or on another site, and no two sites are closer than 61 steps, the
  "burning hot", "very hot" and "freezing" bands cannot fire. The whole period
  table still ships, and
  `tests/test_enchanted_key.py::test_the_flattened_geometry_reaches_these_bands_and_no_others`
  pins exactly which bands are live so nobody has to rediscover it.
- **The coordinates** are Darkan's reconstruction, not a pinned period
  coordinate. The wiki corroborates every site's identity and loot but gives
  locations only in prose. They are used solely to space the sites apart for the
  distance readings, so a later correction changes readings and never rewards.

## Unresolved

The Grand Exchange buy limit for the three mjolnirs. They are tradeable, but the
pinned buy-limit table (oldid `6457777`) has no row for them, so they sell like
every other unresolved identity and stay unbuyable. This is the existing
convention for thirty-nine other catalog rows, and
`tests/test_grand_exchange_data.py` names them.

## Tests to evidence

| claim | test |
| --- | --- |
| quest, key and spade all gate the hunt | `test_the_quest_the_key_and_the_spade_are_all_real_gates` |
| the temperature table is the article's | `test_the_temperature_ladder_is_the_period_table` |
| Fremennik Province is always first | `test_the_first_treasure_is_always_fremennik_province` |
| the rest of the order varies per save | `test_the_rest_of_the_order_varies_between_saves` |
| warmer/colder relation | `test_the_reading_reports_warmer_and_colder_against_the_last_search` |
| every site pays once, the mjolnirs arrive, the key melts | `test_the_whole_hunt_pays_every_site_once_and_then_melts_the_key` |
| a melted key is final | `test_a_melted_key_is_not_replaced_and_the_hunt_does_not_restart` |
| Erin's 500-coin replacement, and its Meeting History cutoff | `test_erin_replaces_a_destroyed_key_for_five_hundred_coins`, `test_erin_stops_replacing_the_key_once_meeting_history_starts` |
| a lost key mid-hunt keeps the order and progress | `test_losing_the_key_mid_hunt_is_recoverable_and_keeps_the_progress` |
| the panel renders view flags it does not own | `test_the_view_owns_every_button_decision_the_panel_renders`, `test_enchanted_key_card_renders_the_view_flags_and_selects_a_site` |
| undo at the mutation boundary | `test_enchanted_key_site_choice_restores_through_the_seam` |
