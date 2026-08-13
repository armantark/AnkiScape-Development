# Farming skill-guide rebuild specification — 2026-08-12

Cutoff: 2012-11-20. Scope: source specification for the missing Farming Stats-tab guide. No product projection ships in this slice.

## Period client spine

The rev-727 and rev-742 clients agree on Farming guide key 21, player-skill ID 19, entry enum 5463, and category enum 5438. Enum 5438 is ordered:

1. Everything
2. Milestones
3. Produce
4. Trees
5. Special
6. Other
7. Dungeoneering

`Everything` is an aggregate filter, not a duplicate family. Rev-727 CS2 script 5683 initializes interface 1218 to `Milestones`; scripts 5690 and 5691 load enum 5463 and filter entries by struct param 2220. Enum 5463 contains 110 structs. The guide must therefore be built from those structs as the authoritative enumeration, then resolve each struct against whichever AnkiScape registry implements it.

Representative positive controls:

- struct 3439: `Potato`, level 1, category 2.
- struct 3453: `Oak tree`, level 15, icon item 1521 (Oak logs), category 3.
- struct 3473: `Make and place a scarecrow`, level 23, category 5.
- struct 3501: `Evil turnip`, level 42, category 4.
- struct 3514: `Access to the Livid Farm`, level 60, category 1.
- struct 3548: `Skill mastery`, level 99, category 1.

Sources:

- `/Users/ArmanTarkhanian1/Library/Caches/codex/2012scape-openrs2/extracted/727-2012-07-24/cache`
- `/Users/ArmanTarkhanian1/Library/Caches/codex/2012scape-openrs2/extracted/742-2012-11-07/cache`
- `tools/query_openrs2_cache_configs.sh`
- `tools/query_openrs2_interfaces.sh`
- `tools/OpenRs2Cs2Disassembler.java`

Darkan's `src/main/java/com/rs/game/model/entity/player/Skills.java` identifies interface 1218 as the skill guide but does not supply Farming categories. `git log -- <path>` supplied no usable category provenance; all `src/main/java/com/rs/web/*AuditProbe.kt` files were excluded. Game-main's `SkillGuide.kt` independently maps Farming to key 21 and skill 19 but carries no category table. RuneScape Wiki oldid 6565110 at 2012-11-17T05:59:19Z describes crop families but not the interface filter order. No source disagrees with the cache structure.

## Required period fields

The normalized Farming-guide row must preserve cache facts rather than replace them with internal Farming data:

- struct ID and stable guide-row identity;
- guide label from param 2210;
- level from param 2212;
- icon item reference from param 2213, resolved to the existing item registry and sprite;
- Farming guide key from param 2215;
- category from param 2220;
- quest and cross-skill requirements carried by the struct/config dependencies;
- resolution status against the implementing AnkiScape registry.

The Stats guide must distinguish `level reached` from `unlocked`. Level alone cannot decide opacity or availability. For example, Jade vine at Farming 53 remains quest-gated by Back to My Roots. That quest is currently unreachable because 185 of 196 quest stage actions lack an emitter, so dropping the gate would direct the player toward content that cannot be found.

## Registry resolution

The 110 period structs include crops and non-crop unlocks. Resolution must search the appropriate existing registries, not only `FARMING_CROPS`:

- crops and patches in `data/farming_data.py`;
- Livid Farm entry/unlocks in `data/livid_farm_data.py` and `logic/livid_farm_logic.py`;
- Evil Tree nurture unlocks in the Evil Tree registry;
- milestone, effigy, scroll, weapon, and other rows in their owning registries;
- Dungeoneering rows remain a separate family and must not be invented from Farming crop data.

AnkiScape currently has 76 `FARMING_CROPS` rows, of which 62 are runnable. These numbers describe modeled crop state, not guide membership. The period guide has 110 structs. The difference is mixed: some rows are unmodeled depth, while others already exist in non-crop registries and were merely missed by a crop-only projection.

White tree is an established absence from the period guide. An exhaustive search of all 110 enum-5463 structs found no Farming row for it; the only global `White tree` struct hit was unrelated achievement struct 1512 and carried neither skill param 2215=21 nor category param 2220. The same search found Potato, Jade Vine, and scarecrow positive controls.

## Why the crop-table projection was withdrawn

The attempted implementation inverted the source relationship six ways:

1. Categories were inferred from internal crop tuple families instead of param 2220.
2. Membership was filtered by `CropDefinition.runnable`, although the guide is informational and period-backed rows remain guide entries before their gameplay implementation is complete.
3. Labels came from internal display names instead of param 2210, producing `Scarecrow` instead of `Make and place a scarecrow` and `Oak` instead of `Oak tree`.
4. The row set came from `FARMING_CROPS`, omitting implemented non-crop entries such as Livid Farm and Evil Tree nurture unlocks.
5. Icons came from harvest outputs or roots instead of param 2213, even though the referenced log assets already exist.
6. Quest and cross-skill gates were discarded, making level appear equivalent to unlocked.

Focused tests passed while encoding these omissions and substitutions. They defended the inverted model rather than detecting it, so they must be replaced with tests derived from the 110-struct source enumeration.

## Safe projection design

Do not add generic per-row section metadata to the existing flat guide path merely for Farming. Legacy target registries should keep the proven `Actions` projection. Farming needs an explicit source-enumerated projection path or a separately reviewed multi-registry guide model.

Section state belongs once per section, not on every row. Group by stable section identity and keep one order per section. If a row cannot resolve, isolate that row and preserve the rest of the display; a malformed or partially migrated row must never flatten every section or abort the Stats guide. Loud failure is appropriate in the source-generation/audit step, not in the player-facing display projection.

The period default was Milestones. If the rebuilt AnkiScape view omits an empty default filter or presents all populated families together, record that as a deliberate UI-parity departure. `_SKILL_TARGET_TABLES` currently serves both guide projection and current-target display resolution; a Farming entry would serve only the guide because Farming intentionally has no `current_target_key` or `default_target`.

## Verification contract for the rebuild

- Pin enum 5438 order and all 110 enum-5463 struct IDs.
- Pin labels, levels, icon item IDs, categories, and gate metadata from the cache.
- Positive-control cache searches and inspect multiplicity before accepting absence.
- Assert resolution coverage by owning registry and list unresolved structs explicitly.
- Test non-crop rows, including Livid Farm and Evil Tree nurture unlocks.
- Test authentic labels and icon references, not merely non-empty rows or asset existence.
- Test level-reached versus unlocked state with quest/cross-skill gates.
- Test that one unresolved/malformed row cannot flatten or crash the guide.
- Add a real offscreen Qt test through `/Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/.venv-qt/bin/python`; the worktree does not contain its own `.venv-qt`.
- Mutation-prove the production source-enumerated path.
- Keep reachability unchanged; this remains an informational surface.

Dungeoneering remains untouched. It has no live level-keyed target table and is a different, larger problem.
