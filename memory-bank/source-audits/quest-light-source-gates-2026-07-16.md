# Quest Light-Source Gate Audit — 2026-07-16

## Scope and evidence

This pass audits the ten quest-stage gates that used the parser artifacts
`Light source` or `Light sources`. The cutoff is 2012-11-20. Exact lit item
states are cross-checked against
`/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/mechanics/lightsource/LightSource.kt`;
its eleven raw/product pairs are the same states exposed by
`firemaking_data.py`. The period light-source classification comes from
`Light sources`, oldid 6581760, 2012-11-19T07:45:54Z. That page lists eleven
ordinary lit source types plus Seer's headbands 1–4 and the three expired
Gielinor Games torches, identifies gas-explosion risks, and says bullseye
lanterns are covered sources that do not go out on their own. The complete
18-item period classification is recorded in `PERIOD_LIT_LIGHT_SOURCE_ITEMS`.

The AnkiScape translation is an OR group of the eleven reachable exact lit
states. An equipped exact state satisfies a non-consumed alternative, which is
necessary for the lit Mining helmet and also corrects existing equipment-shaped
quest alternatives. Consumed alternatives remain inventory-only.

## Quest findings

| Quest and source | Source-backed gate | Implemented stage and alternatives |
|---|---|---|
| Temple of Ikov — oldid 6538747, 2012-11-06T06:17:13Z | “Make sure your light source is lit” before descending the temple stairs. | Stage 1; any of the eleven exact lit states. |
| Watchtower — oldid 6525573, 2012-11-03T08:25:45Z | The Skavid Caves section requires a Skavid map and light source; a lit candle is obtainable in the watchtower. | `source_blocked` stage placement. The generated journal is a placeholder and does not prove a numeric stage, so the phantom row is removed without inventing a start gate. |
| Tears of Guthix — oldid 6547184, 2012-11-10T21:41:57Z | The items list requires a second strong source and names a bullseye lantern or Seer's headband. The walkthrough requires a covered source and says a candle lantern breaks at the stepping stone even when unlit. It later requires the completed sapphire lantern to be lit. | Stage 1 accepts the reachable safe source, `Bullseye lantern (lit)`. Stage 2 retains the empty bullseye plus sapphire transformation gate; stage 3 requires `Sapphire lantern (lit)`. Seer's headbands remain recorded period alternatives but are not live rewards. |
| The Lost Tribe — oldid 6534350, 2012-11-04T20:05:19Z | The Dorgeshuun section says the source must be illuminated before squeezing through the tunnel. | Stage 2; any exact lit state. |
| Wanted! — oldid 6510622, 2012-10-31T12:24:35Z | Chasing Solus calls for a light source; the possible Giant Frog Legs clue explicitly recommends an oil or bullseye lantern in Lumbridge Swamp Caves. | Stage 5; any exact lit state. |
| Rag and Bone Man — oldid 6326142, 2012-09-30T18:23:16Z; quick guide oldid 6539629, 2012-11-06T22:32:33Z | The source is needed while collecting the Big Frog leg in Lumbridge Swamp Caves; the items list says any light source. | Stage 2, bone collection; any exact lit state. |
| Another Slice of H.A.M. — oldid 6548739, 2012-11-12T01:11:00Z | “Getting Past the Guards” requires the source before descending into Lumbridge Swamp Caves; the page excludes the bug lantern. | `source_blocked` stage placement. The generated journal does not align the prose section to a numeric stage, so no guessed stage-4 gate is emitted. Bug lantern remains excluded. |
| Land of the Goblins — oldid 6564799, 2012-11-17T03:36:27Z | “Home Portal” says to bring the source to the fairy ring south of Dorgesh-Kaan. | Stage 7; any exact lit state. The former stage-1 gate was a top-level-item parser placement error. |
| Defender of Varrock — oldid 6542570, 2012-11-08T04:56:59Z | The Camdozaal walkthrough says to enter the excavated hole with a source in inventory. | Stage 4, cave entry; any exact lit state. |
| The Chosen Commander — oldid 6556184, 2012-11-15T03:10:20Z | The search for Zanik says to bring a source to the cave south of Dorgesh-Kaan. Later, Zanik supplies an oil lamp if none is present. | Stage 3, the first actual cave requirement; any exact lit state. The later supplied-lamp event is not duplicated as a gate. |

## Intentional boundaries

- Seer's headbands and Gielinor Games torches are period light sources but are
  not live, obtainable AnkiScape items, so quest OR groups do not advertise
  unreachable states. Their exact names and item IDs remain source-tracked for
  the achievement-reward and legacy-event content passes that would make them
  real items rather than phantom alternatives: Seer's headband 1–4 are rev-742
  IDs 14631, 14662, 14663, and 19763; Bronze, Silver, and Gold torch are IDs
  24547, 24548, and 24549.
- Watchtower and Another Slice of H.A.M. retain explicit `source_blocked`
  placement findings. This pass removes their false parser gates; it does not
  claim an unsupported numeric stage.
- Darkness damage, sources going out, gas explosions, and the Chosen Commander
  oil-lamp handoff remain outside this gate-normalization pass. No wall-clock
  mechanic was added.
- The generated catalog and the Temple of Ikov override both use exact states;
  the phantom `Light source` item is no longer registered.

## Additional consumer seam

The Dorgesh-Kaan Agility Course also used `Light source` as though it were an
inventory identity. Its course lock now uses the same eleven-state reachable OR
group and accepts an exact equipped Mining helmet state. This changes only the
item gate; the course's settled review-native obstacle and payout model is
unchanged.
