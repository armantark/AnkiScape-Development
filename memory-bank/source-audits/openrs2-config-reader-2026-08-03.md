# OpenRS2 enum, struct, and param reader

Date: 2026-08-03. Scope: shared source tooling only. This record establishes
how AnkiScape reads client configuration from the seven local period caches; it
does not promote any recovered number into a gameplay mechanic.

## Decoder authority

Local Darkan checkout:
`/Users/ArmanTarkhanian1/Documents/2012scape with bots`, commit
`900e5307fb876ebc1ed8faab6c481734f6748207`.

- The rev-727 deobfuscated client constructs the param loader from config index
  2, the enum loader from enum index 17, and the struct loader from config index
  2 (`IndexLoaders.java:248-252,272`).
- Its config-type table assigns params to config archive 11 and structs to
  archive 26; enum files use an eight-bit file split (`SharedConfigsType.java:11,14,29`).
- Enum opcodes 1-4 own key/value types and defaults. Opcodes 5-8 own sparse or
  array-backed string/integer entries (`EnumDefinitions.java:45-84`).
- Struct opcode 249 owns typed 24-bit param keys with string or integer values
  (`CacheableNode_Sub4.java:7-27`).
- Param opcodes are exactly 1 type, 2 integer default, 4 auto-disable false, and
  5 string default (`ParamDefinitions.java:47-65`).

The shipped tool reuses Darkan core 2.0.5 for enums and structs. Its local param
decoder implements only those four disclosed opcodes and fails on any other
opcode. This is safer than silently accepting revision drift.

## Tool contract

`tools/query_openrs2_cache_configs.sh` accepts an immutable OpenRS2 disk zip or
an extracted cache directory:

```
tools/query_openrs2_cache_configs.sh <cache> <enum|struct|param> count
tools/query_openrs2_cache_configs.sh <cache> <enum|struct|param> dump <id> [id ...]
tools/query_openrs2_cache_configs.sh <cache> <enum|struct|param> find <needle>
```

Output is deterministic. Entry maps are sorted by numeric key. An absent ID is
labelled rather than decoded as an empty definition.

## Period-cache proof

Definition counts from the seven extracted caches:

| build | date | enums | structs | params |
| --- | --- | ---: | ---: | ---: |
| 652 | 2011-06-08 | 3,853 | 1,793 | 1,414 |
| 727 | 2012-07-24 | 6,048 | 11,389 | 2,583 |
| 728 | 2012-08-01 | 6,060 | 11,416 | 2,583 |
| 729 | 2012-08-11 | 6,093 | 11,429 | 2,583 |
| 736 | 2012-10-09 | 6,634 | 13,879 | 2,775 |
| 741 | 2012-11-04 | 6,672 | 14,509 | 2,788 |
| 742 | 2012-11-07 | 6,680 | 14,527 | 2,792 |

The integration test pins three immutable rev-727 samples:

- enum 3483: integer keys, `J` values, default 1645, 1,096 entries, first pair
  `0 → 1592`;
- struct 0: four pairs, `130 → 1804`, `131 → 1807`, `134 → 1805`, and
  `135 → 1806`;
- param 0: integer type, default 0, auto-disable true.

Rev 742 independently preserves the same sample values while growing enum 3483
to 1,112 entries.

## Evidence ceiling and next slice

Enums, structs, and params can settle client identities, labels, component
relationships, defaults, and client-side gates. They cannot by themselves
settle XP, random rolls, drop rates, server timers, or reward equations. Those
remain `source_blocked` without ordinary period/server corroboration.

Interface-definition decoding is the next shared tooling slice. After it lands,
the parity ledger can be re-walked for rows blocked specifically on client-side
configuration. Server-side rows stay untouched.
