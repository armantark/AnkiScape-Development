# OpenRS2 interface-definition reader

Date: 2026-08-03. Scope: shared source tooling only. This record establishes
how AnkiScape reads client interface definitions from the seven local period
caches. It does not treat client presentation or script operands as proof of a
server mechanic.

## Decoder authority

Local Darkan checkout:
`/Users/ArmanTarkhanian1/Documents/2012scape with bots`, commit
`f7fd72bbf7b11b1177e407db091f9af327dece19`.

- The rev-727 client loads interfaces from index 3
  (`darkan-client/src/main/java/com/rs/jagex/IndexLoaders.java:156-169`).
- Each interface is one archive; its component number is the file number. The
  loader assigns the stable packed identity `component + (interface << 16)`
  before decoding the file
  (`darkan-client/src/main/java/com/rs/jagex/SkyboxIndexLoader.java:8-35`).
- The component format begins with a version byte and component type. The
  decoder then reads content type, bounds/aspect modes, parent, hidden and
  click-through flags, followed by type-owned sprite, model, text, figure, or
  line fields
  (`darkan-client/src/main/java/com/rs/jagex/IComponentDefinitions.java:989-1096`).
- The same file carries client action labels, cursor metadata, event flags,
  typed parameters, script hooks, and watched variables
  (`IComponentDefinitions.java:1097-1209`).

The shipped reader wraps the already-installed Darkan core 2.0.5 interface
loader rather than copying the 220-line binary decoder. The exact jar used in
verification has SHA-256
`bfaf99f7bb04a55418a9aeb07a01f2724034692637b435a87df4f3f4b029e3fe`.

## Tool contract

`tools/query_openrs2_interfaces.sh` accepts an immutable OpenRS2 disk zip or an
extracted cache directory:

```
tools/query_openrs2_interfaces.sh <cache> count
tools/query_openrs2_interfaces.sh <cache> dump <interface-id> [component-id ...]
tools/query_openrs2_interfaces.sh <cache> find <needle>
```

`dump` without component IDs prints the whole interface. `find` searches only
client-authored names, visible text, use labels, operation labels, and option
labels. Output includes stable `interface:component` identities, layout and
visibility metadata, text/font, sprite/model references, actions, and the
principal script hooks. It is deterministic for the same cache and query.
Correction, 2026-08-13: the checked-in reader still skips fifteen archives in
revisions 736, 741, and 742. Darkan core 2.0.5 throws an exception labelled
`if1` whenever a component's first byte is not `0xFF`; the affected components
begin with version byte `0x03`, so the label does not establish a legacy or
unsupported format. `OpenRs2InterfaceQuery.find` catches the exception, prints a
skip warning, and exits zero after searching only the remainder. Absence from
its output is therefore incomplete negative evidence.

A one-off reflective experiment bypassed that guard and invoked the library's
package-private decoder directly. It decoded all 1,376 affected components into
coherent period interfaces, including Squeal of Fortune and Avatar
Customisation surfaces. The experiment found none related to Achievement Diary
interface 917, Conquest, or Daily Challenges interface 1343. Reproducing that
complete search requires a guard fix or a byte-level parser; neither exists in
the repository today. The archive IDs are `548`, `628`, `629`, `633`, `634`,
`635`, `691`, `976`, `1253`, `1311`, `1316`, `1358`, `1360`, `1361`, and
`1368`. Interface ID 976 also demonstrated a namespace-collision hazard: an
interface archive number is not an item, NPC, object, enum, or struct identity
merely because the integer matches.

## Period-cache proof

Index-3 counts from the seven extracted caches:

| build | date | interfaces | components | first ID | last ID |
| --- | --- | ---: | ---: | ---: | ---: |
| 652 | 2011-06-08 | 1,096 | 46,654 | 0 | 1,110 |
| 727 | 2012-07-24 | 1,321 | 65,239 | 0 | 1,320 |
| 728 | 2012-08-01 | 1,323 | 65,345 | 0 | 1,322 |
| 729 | 2012-08-11 | 1,331 | 65,717 | 0 | 1,331 |
| 736 | 2012-10-09 | 1,362 | 67,912 | 0 | 1,361 |
| 741 | 2012-11-04 | 1,362 | 67,864 | 0 | 1,369 |
| 742 | 2012-11-07 | 1,363 | 67,952 | 0 | 1,369 |

At least interface 0 component 0 decodes through the same loader in every
snapshot. Exact rev-727 integration fixtures additionally pin:

- interface 105 component 15: the `Grand Exchange` text heading, font 496,
  and on-load script 585;
- interface 889 component 15: a container whose client operation is
  `Travel to the Grand Exchange`.

## Evidence ceiling and next slice

An interface definition can establish shipped component identities, visible
text, layout, hidden defaults, sprites/models, action labels, and the existence
and operands of client script hooks. It cannot establish server validation,
quest-state truth, XP, random rolls, drop rates, timers, or reward equations.
Those remain `source_blocked` without ordinary period or server corroboration.

The next depth slice is a client-side-only re-walk of existing
`source_blocked` rows using the config, interface, and CS2 readers. Rows that
depend on hidden server behavior stay untouched.
