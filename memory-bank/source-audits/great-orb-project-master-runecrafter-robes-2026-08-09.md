# Great Orb Project Master Runecrafter robes

Date: `2026-08-09`

Cutoff: RuneScape immediately before EOC, `2012-11-20`.

## Period evidence

RuneScape Wiki `Master runecrafter robes` oldid `6514332`, timestamp
`2012-11-01T00:45:56Z`, pins the four-piece reward family. Each piece costs
15,000 Runecrafting Guild tokens. The per-piece Runecrafting XP bonuses are
0.8% hat, 1.6% body, 1.2% skirt, and 0.4% boots. Wearing all four adds another
1%, for 5% total. The bonus applies to all Runecrafting activities, stacks with
the Great Orb Project's double XP, and is capped at 700 bonus XP per action:

<https://runescape.wiki/w/Master_runecrafter_robes?oldid=6514332>

The exact cutoff child revisions are hat oldid `6311005`, body page `Master
runecrafter robe` oldid `6529558`, skirt oldid `6311007`, and boots oldid
`6311008`. They state no wear requirement beyond the Great Orb Project's
indirect level-50 admission gate.

The immutable Darkan source artifact is:

`/Users/ArmanTarkhanian1/Documents/2012scape with bots/memory-bank/audit/sources/great-orb-project-oldids.json`

The artifact SHA-256 is
`2eb976379eb698f1a57ece1cc463a1e01a5726c81214e4da159a418bacb49c2b`;
its stored Master-robes wikitext SHA-256 is
`3004ec95da9a94d0ed342b88acb6fcd7c198a58acfd0f64be6f29dddac01dc74`.

OpenRS2 revision 742 pins the exact item identities and slots:

| Item | ID | Slot | Magic attack | Each defence |
| --- | ---: | --- | ---: | ---: |
| Master runecrafter body | 21516 | Body | +5 | +5 |
| Master runecrafter hat | 21517 | Head | +3 | +3 |
| Master runecrafter skirt | 21518 | Legs | +4 | +4 |
| Master runecrafter boots | 21519 | Feet | +2 | +2 |

All four cache rows are non-stackable, non-exchangeable, and wearable. The
combat values apply equally to Stab, Slash, Crush, Magic, and Ranged defence.
The local authentic game-main table was consulted only as corroboration because
its trade flags and boots equipment row disagree with the dated cache; its
observed SHA-256 was
`4bc95333b282216b6d1a50dd60b4510aa0bbc837d5bc39b0d1b8e44d7390e4f0`.

## Live translation

Wizard Elriss sells each piece one at a time for exactly 15,000 tokens through
the existing atomic purchase and direct-undo path. The four items use the
shared inventory, Bank, equipment, discard, and recovery registries. Their
piece bonuses and full-set bonus apply to ordinary altar Runecrafting and to
Great Orb Project crafting. The 700 limit caps only the added XP:

`awarded XP = base XP + min(base XP × worn rate, 700)`

Great Orb Project applies the bonus inside its pure result, so the result
payload, match status, persistent match tracker, runtime XP award, telemetry,
and undo all observe the same number.

The four sprites are exact RuneScape Wiki file revisions dated
`2011-08-23`. Their source dimensions are 23×21, 36×32, 26×25, and 22×21; the
existing asset pipeline normalizes transparent padding and the UI renders them
in the shared fixed 24-pixel item slot. Each immutable revision and SHA-1 is
recorded in `assets_provenance.json`.

## Review findings

Kimi K3 found three concrete presentation/integration defects, all reproduced
and fixed: Elemental talisman now precedes the robe family; token amounts use
thousands separators; and Great Orb Project status no longer reports base XP
while runtime awards boosted XP. Root inspected the real 1200×760 dark render.
The supported Opus review failed closed: the final preflight reported
`Claude rejected the OAuth token. Run one Claude Code command to refresh it.`
and `Claude call canceled because a fresh quota snapshot was unavailable.` No
unsupported bypass was used.

Read-only Sol-high simplification run
`17f8d113-af59-44e0-a170-9acd022b70ec` exhausted its bounded processed-token
budget (`121271` observed against `90000`) before findings. Root preserved the
partial artifact, completed the bounded diff review locally, and removed one
needless temporary variable. No behavioral defect remained.

## Boundaries

- Standard Runecrafter robes, talisman staves, and teleport tablets remain
  separate data/mechanic depth.
- No hidden roll, registered placeholder, wall clock, migration, or owner
  design decision was introduced.

## Verification

Focused pure, runtime, equipment, registry, undo, and UI tests exercise all
four exact shop rows, equipment data, piece/full-set/cap arithmetic, ordinary
Runecrafting, Great Orb Project status and runtime XP, source assets, and direct
undo. Full plain and real offscreen-Qt discovery each pass 3,895 tests, with 479
expected plain skips and three intentional Qt skips. The remaining closure
audit passes 525 Markdown and 431 HTML files; test quality reports zero hard
issues across 3,861 tests in 177 files. Compilation, 26 tracked JSON files,
diff whitespace, all 272 Activities-item sprite crops, deterministic asset
fetches, and worktree safety pass. Reachability improves to 2,244 reachable
items while holding at 1,499 actions, 168 known orphan inputs, and 188 known
unresolved actions.
