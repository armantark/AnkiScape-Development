# Skilling brawling-gloves source closure

Date: `2026-08-09`

Cutoff: RuneScape immediately before EOC, `2012-11-20`.

Backlog item: `skilling-brawling-gloves-runtime`.

## Result

The period record closes the six item identities and the XP multipliers. It
also closes five action-count limits well enough for the settled action model.

Mining has no exact period action count. The period page gives a 30-minute use
window and an estimate of 350 to 800 ores. AnkiScape must never use wall-clock
time for gameplay. A later implementation must register one review-action
count as a labeled abstraction.

The glove drop rate also remains `source_blocked`. Period pages prove drops
from Revenants and the Chaos Elemental, but they give no rate. AnkiScape does
not have either encounter. The shared runtime must wait for an obtainable
source route through the boss or Revenant work.

No owner design question remains. The block is source and implementation work.

## Period page set

| Page | Oldid | UTC timestamp | What it proves |
| --- | ---: | --- | --- |
| [Brawling gloves](https://runescape.wiki/w/Brawling_gloves?oldid=6472676) | `6472676` | `2012-10-25T20:40:58Z` | Members-only Revenant drops; 1.5 times XP outside the Wilderness; 4 times XP in the Wilderness; use-limited disintegration; 13 glove types; same-type gloves do not bank-stack. |
| [Brawling gloves (Woodcutting)](https://runescape.wiki/w/Brawling_gloves_%28Woodcutting%29?oldid=6055139) | `6055139` | `2012-08-07T13:22:23Z` | 1.5 times outside; 4 times inside; 732 logs; Revenant and Chaos Elemental acquisition. |
| [Brawling gloves (Firemaking)](https://runescape.wiki/w/Brawling_gloves_%28Firemaking%29?oldid=6055133) | `6055133` | `2012-08-07T13:18:25Z` | 1.5 times outside; the skill-specific 5-times Wilderness exception; 1,200 logs; Revenant and Chaos Elemental acquisition. |
| [Brawling gloves (Mining)](https://runescape.wiki/w/Brawling_gloves_%28Mining%29?oldid=6055149) | `6055149` | `2012-08-07T13:24:57Z` | 1.5 times outside; 4 times inside; 30 minutes or about 350 to 800 ores; Revenant and Chaos Elemental acquisition. |
| [Brawling gloves (Smithing)](https://runescape.wiki/w/Brawling_gloves_%28Smithing%29?oldid=5912021) | `5912021` | `2012-07-09T12:54:27Z` | 1.5 times outside; 4 times inside; about 434 normal actions; XP-scaled wear with Sacred clay; Revenant and Chaos Elemental acquisition. |
| [Brawling gloves (Fishing)](https://runescape.wiki/w/Brawling_gloves_%28Fishing%29?oldid=6469129) | `6469129` | `2012-10-25T04:45:11Z` | 1.5 times outside; the skill-specific 5-times Wilderness exception; about 400 catches; explicit PKer risk; Revenant and Chaos Elemental acquisition. |
| [Brawling gloves (Cooking)](https://runescape.wiki/w/Brawling_gloves_%28Cooking%29?oldid=6560241) | `6560241` | `2012-11-16T00:18:08Z` | 1.5 times outside; 4 times inside; 1,109 successful cooks; Revenant and Chaos Elemental acquisition. |

The cutoff [general talk page](https://runescape.wiki/w/Talk:Brawling_gloves?oldid=5554007)
at oldid `5554007` (`2012-05-02T22:44:01Z`) preserves an official Game Guide
claim that the Wilderness effect totals 4 times normal XP. It also records that
gloves use action-based wear instead of elapsed time. Talk evidence is a
secondary check, not the source of the numeric rows above.

## Cache identity proof

The rev-727 and rev-742 caches contain the same six item definitions.

| Skill | Item ID | Period item name | Stackable | Exchangeable | Options |
| --- | ---: | --- | --- | --- | --- |
| Woodcutting | `13850` | `Brawling gloves (wc)` | No | No | `Wear`, `Destroy` |
| Firemaking | `13851` | `Brawling gloves (fm)` | No | No | `Wear`, `Destroy` |
| Mining | `13852` | `Brawling gloves (mining)` | No | No | `Wear`, `Destroy` |
| Smithing | `13855` | `Brawling gloves (smithing)` | No | No | `Wear`, `Destroy` |
| Fishing | `13856` | `Brawling gloves (fishing)` | No | No | `Wear`, `Destroy` |
| Cooking | `13857` | `Brawling gloves (cooking)` | No | No | `Wear`, `Destroy` |

Commands:

```bash
tools/query_openrs2_cache.sh '/Users/ArmanTarkhanian1/Library/Caches/codex/2012scape-openrs2/extracted/727-2012-07-24/cache' --id 13850 13851 13852 13855 13856 13857
tools/query_openrs2_cache.sh '/Users/ArmanTarkhanian1/Library/Caches/codex/2012scape-openrs2/extracted/742-2012-11-07/cache' --id 13850 13851 13852 13855 13856 13857
```

The two cache rows match for names, model `42579`, recolours, zero bonuses,
stackability, exchangeability, and options. The cache does not prove XP,
charges, or acquisition rates.

## Reconstruction comparison

The local `game-main` tree is not a Git worktree, so it has no commit identity.
Its candidate implementation is at:

- `game/plugins/src/main/kotlin/gg/rsmod/plugins/content/items/armor/BrawlingGloves.kt:6-21`
- `game/plugins/src/main/kotlin/gg/rsmod/plugins/api/ext/PlayerExt.kt:1877-1913`

It uses one charge per XP action and disintegrates at zero. It also applies a
level-scaled first-use formula. Its maximum counts conflict with the cutoff
pages for five of the six in-scope skills. Do not ship those values as period
facts.

Darkan world-server commit
`bf9c0f0894e05a592826c6e3e622d1b9538c4e88` uses a different reconstruction:

- `src/main/java/com/rs/game/model/entity/player/Skills.java:1002-1030`
- `src/main/java/com/rs/game/model/entity/player/Skills.java:1082-1133`
- `src/main/java/com/rs/game/content/world/areas/wilderness/forinthry/Revenant.kt:118-160`

Darkan gives ordinary skilling gloves a flat 464 charges. It adds 0.5 outside
the Wilderness and 2.0 inside to the base multiplier. This totals 1.5 and 3.0,
which conflicts with every cutoff Wilderness row. Its Revenant table proves an
implementation route, but not a period drop rate.

## Implementation-ready constants

The settled AnkiScape design consumes one charge for each XP action. It does
not reproduce Sacred-clay double wear because that equipment interaction is
outside this six-skill substrate.

| Skill | Outside multiplier | Wilderness multiplier | Action limit | Status |
| --- | ---: | ---: | ---: | --- |
| Woodcutting | `1.5` | `4.0` | `732` | Period closed. |
| Firemaking | `1.5` | `5.0` | `1200` | Period closed. |
| Mining | `1.5` | `4.0` | not set | Register a review-action abstraction. Do not use wall time. |
| Smithing | `1.5` | `4.0` | `434` | Period approximation becomes the deterministic action limit. |
| Fishing | `1.5` | `5.0` | `400` | Period approximation becomes the deterministic action limit. |
| Cooking | `1.5` | `4.0` | `1109` | Period closed. |

## Blocks and omissions

- `source_blocked`: the Mining action count.
- `source_blocked`: the Revenant and Chaos Elemental glove drop rates.
- Dependency block: AnkiScape has no Revenant or Chaos Elemental encounter.
- The period pages describe PKers and dangerous Wilderness routes. They do not
  state an attack probability. The existing AnkiScape Wilderness risk kernel
  must own the labeled cadence abstraction.
- The period pages do not prove exact death protection or recovery behavior.
- This audit does not add Combat, Prayer, Agility, Hunter, or Thieving gloves.
- This audit does not add any product code, user interface, or asset.

## Delegation record

Codex Workflows run `d66c60fd-e7de-4966-a12c-56e969689fad` used two read-only
Sol-high leaves. Both leaves exceeded their evidence budgets after three tool
calls. Root used only their file leads and reproduced every accepted claim.
