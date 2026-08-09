# Mage Training Arena reward-catalog closure

Date: `2026-08-08`

Cutoff: RuneScape immediately before EOC, `2012-11-20`.

Status: **the complete 25-row cutoff reward shop is live. Every row has its
exact four-wallet price and a canonical item or unlock. The Infinity set and
Mages' book have exact period identities, modeled Magic bonuses, shared equip
requirements, and normalized source sprites. No placeholder or design gap was
added.**

## Period shop table

RuneScape Wiki `Mage Training Arena` oldid `6491109`, timestamp
`2012-10-28T20:51:43Z`, supplies the literal reward table in Telekinetic /
Alchemist / Enchantment / Graveyard order:

<https://runescape.wiki/w/Mage_Training_Arena?oldid=6491109>

| Reward | Cost |
| --- | ---: |
| Infinity gloves | `175 / 225 / 1,500 / 175` |
| Infinity hat | `350 / 400 / 3,000 / 350` |
| Infinity top | `400 / 450 / 4,000 / 400` |
| Infinity bottoms | `450 / 500 / 5,000 / 450` |
| Infinity boots | `120 / 120 / 1,200 / 120` |
| Battlestaff | `1 / 2 / 20 / 2` |
| Beginner wand | `30 / 30 / 300 / 30` |
| Apprentice wand | `60 / 60 / 600 / 60`, plus Beginner wand |
| Teacher wand | `150 / 200 / 1,500 / 150`, plus Apprentice wand |
| Master wand | `240 / 240 / 2,400 / 240`, plus Teacher wand |
| Mages' book | `500 / 550 / 6,000 / 500` |
| Bones to Peaches | `200 / 300 / 2,000 / 200` |
| Mist, Dust, Mud, Smoke, Steam, or Lava rune | `1 / 1 / 15 / 1` each |
| Cosmic rune | `0 / 0 / 5 / 0` |
| Chaos rune | `0 / 1 / 5 / 1` |
| Nature rune | `0 / 1 / 0 / 1` |
| Death rune | `2 / 1 / 20 / 1` |
| Law rune | `2 / 0 / 0 / 0` |
| Soul rune | `2 / 2 / 25 / 2` |
| Blood rune | `2 / 2 / 25 / 2` |

The source table writes “Mage's book”. Rev-742 item `6889` is named
`Mages' book`; the implementation uses the canonical cache identity while the
price remains the literal oldid row. Bones to Peaches remains an atomic spell
unlock rather than a fabricated inventory item.

## Period identities and equipment

The deterministic rev-742 item query
`tools/query_openrs2_cache.sh --id <ids>` against the extracted
`742-2012-11-07` cache pins:

- Mages' book `6889`;
- Infinity top `6916`, hat `6918`, boots `6920`, gloves `6922`, and bottoms
  `6924`;
- Death `560`, Nature `561`, Chaos `562`, Law `563`, Blood `565`, and Soul
  `566` runes; and
- Steam `4694`, Mist `4695`, Dust `4696`, Smoke `4697`, Mud `4698`, and Lava
  `4699` runes.

The authentic game-main item definitions at
`/Users/ArmanTarkhanian1/Downloads/game-main/data/cfg/items.yml` pin the modeled
equipment fields:

| Item | Slot | Magic attack / defence | Requirement |
| --- | --- | ---: | --- |
| Mages' book | Shield | `15 / 15` | Magic 60 |
| Infinity gloves | Hands | `5 / 5` | Defence 50, Magic 25 |
| Infinity hat | Head | `6 / 6` | Defence 50, Magic 25 |
| Infinity top | Body | `22 / 22` | Defence 50, Magic 25 |
| Infinity bottoms | Legs | `17 / 17` | Defence 50, Magic 25 |
| Infinity boots | Feet | `5 / 5` | Defence 50, Magic 25 |

The source definitions also contain a Summoning bonus. AnkiScape's shared
equipment model has no Summoning-bonus field, so this catalog slice does not
invent a one-off parallel stat.

Registering these six exchangeable items also activates their live Grand
Exchange rows. The existing cutoff harvester recovered an exact four-hour buy
limit of `10` for every item and these nearest-pre-cutoff prices:

| Item | Guide price | Exchange oldid |
| --- | ---: | ---: |
| Infinity boots | `677,237` | `6549641` |
| Infinity bottoms | `4,248,199` | `6519647` |
| Infinity gloves | `1,753,011` | `6562407` |
| Infinity hat | `2,551,706` | `6570751` |
| Infinity top | `3,234,233` | `6562411` |
| Mages' book | `3,115,395` | `6562622` |

All six Exchange revisions are dated between `2012-11-02` and `2012-11-18`.
They replace the cache-value price fallback and keep buy offers available
without weakening the GE catalog's fail-closed limit boundary.

## Assets and UI

Six source sprites were fetched through the existing asset pipeline and are
recorded in `assets_provenance.json`. Their immutable source timestamps range
from `2011-08-10` to `2012-04-25`, all before the cutoff. Native sprites remain
at their source aspect ratios; both Goal and Reward selectors render them in a
fixed `24 × 24` icon box.

The existing two-selector design is unchanged. It now exposes all 25 source
rows with text as the primary identifier and icons as a secondary
disambiguator. This is especially useful for the four wand upgrades and the
similarly named rune rows. Bones to Peaches uses its existing spell icon rather
than appearing as a false section heading. Kimi K3 found no blocking taste
defect and recommended the icon treatment. Opus identified the missing spell
icon; the final UI includes its smallest correction.

## Behavioral closure

Every row has an atomic full-wallet purchase proof that consumes the exact four
balances, consumes the predecessor wand when required, yields the item or
unlock, increments the durable purchase count, and integrates with the shared
item/equipment registries. One bounded end-to-end Battlestaff proof earns its
price through all four room loops. Repeating the thousands of room reviews for
all 25 data rows would duplicate the same mechanic and is deliberately absent.

The complete catalog changes no room cadence, hazard, death, cap, route, undo,
or persistence contract. Hidden room rolls and throughput placeholders remain
owned by the earlier Arena audits.

## Verification

The accepted catalog passes:

- 133 focused MTA, GE, registry, equipment, undo, reachability, and tooling
  tests;
- 3 focused real offscreen Qt selector and asset-normalization tests;
- full plain discovery: 3,889 tests, 479 expected environment skips;
- full real offscreen Qt discovery: 3,889 tests, 3 intentional skips;
- documentation: 523 Markdown and 431 HTML files;
- test quality: 3,855 tests across 177 files, zero hard issues; and
- reachability: 1,499 actions, 2,240 reachable items, 168 orphan inputs, and
  188 unresolved actions.

Python compilation, JSON parsing, diff hygiene, asset normalization, and the
worktree guard also pass. The real 1200×760 dark-palette render shows the full
shop row and the 25-row popup without truncation. Kimi K3 returned no blocker
after recommending icons. Opus found that the sole iconless Bones to Peaches
row looked like a section heading; the existing period spell icon closed that
defect, and the final Qt regression pins it.

Read-only Sol-high simplification runs
`d8d86421-3316-4a95-821c-034416da54e3` and
`f9634099-4ef5-476f-91cd-b8a9a90d2393` failed safely at their tool-output
guards before producing findings. Root's narrow diff review found no
behavior-equivalent deletion. No model edited or committed code.
