# Prayer, Altar, Urn, Passive, and Herblore Closure Audit

Date: 2026-07-13  
Cutoff: RuneScape immediately before EOC, `2012-11-20T00:00:00Z`  
Scope: Prayer combat/training polish, owned gilded altar, training urns, Bonecrusher, Ectoplasmator, direct urn teleport/undo, and Prayer-potion/bonemeal identity integration.

## Evidence layers

### Historical wiki revisions

Revision timestamps were re-queried through the RuneScape Wiki MediaWiki API on 2026-07-13.

| Page | Revision | UTC timestamp | Claim used |
| --- | ---: | --- | --- |
| Prayer | 6539264 | 2012-11-06T19:15:34Z | lit gilded altar reaches 3.5x |
| Ectofuntus | 6544994 | 2012-11-09T13:32:24Z | 4x Prayer XP and five ecto-tokens per worship |
| Ancient Curses | 6535713 | 2012-11-05T05:11:14Z | curse roster and drain cadence |
| Chivalry | 6268775 | 2012-09-19T20:20:45Z | Prayer 60, Defence 65, Knight Waves gate |
| Piety | 6268774 | 2012-09-19T20:20:44Z | Prayer 70, Defence 70, Knight Waves gate |
| Urns | 6386501 | 2012-10-11T17:09:13Z | six supported skill families, tier levels, XP capacities, and teleport rewards |
| Bonecrusher | 6589107 | 2012-11-19T23:56:51Z | item 18337 and automatic bone-bury behavior |
| Ectoplasmator | 6566210 | 2012-11-17T14:35:50Z | item 25354 and exact covered spectral XP rows |

The code also pins dated ash, Rapid Restore/Renewal, and Redemption revisions in `prayer_data.py`; their UTC dates were reconciled against the API during this pass.

### Period-lineage implementation and cache identity

- `game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/mechanics/prayer/prayer.kt`
- `game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/mechanics/prayer/Prayers.kt`
- `game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/skills/prayer/burying/BoneData.kt`
- `game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/skills/prayer/scattering/AshData.kt`
- `game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/skills/crafting/pottery/PotteryData.kt`
- `game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/skills/crafting/pottery/AddRuneAction.kt`
- `game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/skills/herblore/mixing/PotionData.kt`
- `game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/api/cfg/Items.kt`
- `game-main/data/cfg/items.yml`
- Darkan Prayer/Sap/Leech/Curse manager rows pinned at `7e7d67b481f1b94599de38a98c470419ab7c96b3` in `prayer_data.py`.
- Construction altar/burner evidence is frozen in `construction-skill-contract-2026-07-11.md`, including Chapel `2012-10-14T18:39:20Z` and Mahogany burner `2011-12-06T22:57:30Z` pins.

## Closed values and behavior

### Combat Prayer

- The master switch masks effects without erasing configured selections or uptime.
- Standard-prayer conflicts and curse-family conflicts normalize deterministically.
- Target overrides apply independently of preset pinning.
- Chivalry requires Defence 65 and Knight Waves; Piety requires Defence 70 and Knight Waves; Rigour and Augury require Defence 70.
- Locked Curses fall back to Standard without dropping unrelated preset state.

### Owned gilded altar

- Gilded altar base: 250%.
- One lit burner: 300%.
- Two lit burners: 350%.
- Lighting consumes one clean marrentill per installed burner once at the start of a new stint.
- The stint freezes its burner count/multiplier. Changing the composite Prayer selection ends stale hosted-search and owned-stint state; reopening the same selection does not charge herbs again.

### Training urns

- Twenty-six tiers ship across Mining, Cooking, Fishing, Woodcutting, Smithing, and Prayer.
- Each tier has exact unfired, non-runed, runed, active, and full source IDs; every physical state is non-stackable.
- Charge eligibility follows the pinned resource family/level exclusions, preserves overflow into another carried runed urn, and caps each skill at ten nonempty urns.
- Activation is physical and target-local: bank-only or other-target urns do not charge.
- Advanced saved layouts represent logical urn slots and materialize the current runed/active/full state after both skilling and Combat bank runs.
- Direct full-urn teleport requires the full urn in the current target's carried pack, awards the pinned teleport XP, records telemetry, persists immediately, and uses a separate bounded LIFO Anki undo stack.

### Bonecrusher and Ectoplasmator

- Both are non-tradeable, non-stackable target-carried passives.
- Bonecrusher intercepts eligible Combat and Hunter bone outputs before ordinary auto-Prayer handling.
- Ectoplasmator awards only the exact source-closed spectral rows currently represented by stable Combat targets; generic or unproven spectral aliases remain excluded.
- No acquisition route is invented. The items can be present through test/developer/save state until their authentic owning activities ship.
- Their checked-in icons use explicit RS3 wiki fetching and provenance. OSRS-first fallback output found during takeover was replaced because it lacked independent period-art proof.

### Bonemeal identity and Prayer potions

The earlier gap-ledger conclusion that item 6810 should collapse into ordinary `Bonemeal` is superseded.

- `Items.kt` names ID 4255 `BONEMEAL` and ID 6810 `WYVERN_BONEMEAL`.
- `items.yml` proves both source display names are `Bonemeal`.
- `PotionData.kt` binds Super prayer to `Items.WYVERN_BONEMEAL` at level 94 for 270 Herblore XP.
- AnkiScape therefore preserves two storage identities: `Bonemeal` (4255) and disambiguated `Wyvern bonemeal` (6810). This is a storage-key disambiguation, not an invented RuneScape display name.
- Prayer and Super prayer doses restore the internal Prayer-point pool with the pinned formulas/caps; automatic drinking prefers Super prayer.

## AnkiScape abstractions

- One successful review remains one sourced action by default; Ectofuntus preparation retains the owner-set pacing batches documented in the Prayer contract.
- Target-carried packs model physical inventory without a persistent world location.
- Hosted gilded-altar search and owned altar stint are compact review-state abstractions, not literal house travel.
- Direct teleport is a non-review Bank action, so its undo is intentionally separate from Answer Card undo.

## Source-blocked or deferred

- Bonecrusher and Ectoplasmator acquisition routes remain deferred to their authentic owning activities/reward systems.
- Shades of Mort'ton cremation and GE acquisition remain on their owning program cards.
- No Ancient bonemeal, modern any-herb burner rule, or OSRS Chaos Temple offering altar is added.
- The owner's real Anki profile was not mutated during certification; the results artifact carries the release-candidate manual checklist.

## Conflict resolutions

1. **Bonemeal name collision:** preserve source IDs and use `Wyvern bonemeal` only as the stable disambiguated storage key for 6810.
2. **Passive icon fallback:** replace OSRS-first results with explicit RS3 provenance because exact period-art identity was not independently closed.
3. **Saved urn layout versus physical state:** materialize each logical slot to the actual active/full/runed bank item instead of replaying stale `(r)` text.
4. **UI refresh:** direct teleport rerenders the visible implemented skill panel so awarded XP/levels and locks are immediately truthful.
5. **High-tier Defence gates:** encode Chivalry 65 and Rigour/Augury/Piety 70 in the shared data row so malformed saves and non-Qt paths cannot bypass them.

## Test map

- `tests/test_prayer.py`: books, gates, conflicts, composite selection, altar multipliers/stints, Ectofuntus, potions, and source assets.
- `tests/test_prayer_passives.py`: target-carried passive precedence, counters, exact spectral mapping, and no invented acquisition.
- `tests/test_urns.py`: 26-tier authority, five-state IDs, charging/overflow/caps, target-local presence, repacks, teleport, migration, and provenance.
- `tests/test_runtime_actions.py`: Prayer/Herblore processing and carried-overlay behavior.
- `tests/test_combat_logic.py`: Prayer effects, passives, Prayer urns, bank runs, and preservation of combat behavior.
- `tests/test_integration_smoke.py`: review undo, direct custom LIFO undo, save callbacks, atomic selection, XP, and UI bridge integration.
- `tests/test_main_menu_widget.py`: real offscreen Qt selection, gates/tooltips, owned altar presentation, carried pack, direct teleport, visible level refresh, Bank actions, and unchanged Construction/Farming surfaces.
- `tests/test_storage_pure.py`, `tests/test_construction.py`, and `tests/test_farming.py`: schema-v33 migration and preservation boundaries.

Final certification: 626 focused tests passed; the independent backend audit passed 663 tests; `python3 run_tests.py` passed 1,198 tests with 187 environment skips and 3 expected failures; real offscreen Qt discovery passed 1,198 tests with 3 expected failures. The artifact URL and commit are recorded in `status-updates/archive/2026-07/prayer-herblore-construction-polish-results-2026-07-13.html`.
