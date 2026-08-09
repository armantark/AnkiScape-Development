# Great Orb Project standard Runecrafter robes

Date: `2026-08-09`

Cutoff: RuneScape immediately before EOC, `2012-11-20`.

## Period evidence

RuneScape Wiki `Runecrafter robes` oldid `6327369`, timestamp
`2012-09-30T21:15:05Z`, pins three colours (green, blue, and yellow), four
pieces per colour (hat, robe, skirt, and gloves), and a price of 1,000
Runecrafting Guild tokens for every piece. It states that there is no direct
wear requirement; level 50 Runecrafting is only the existing indirect gate to
enter the guild and play Great Orb Project:

<https://runescape.wiki/w/Runecrafter_robes?oldid=6327369>

The same revision records the exact combat bonuses for every colour:

| Piece | Magic attack | Stab defence | Slash defence | Crush defence | Magic defence | Ranged defence |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Hat | +3 | +3 | +3 | +3 | +3 | +3 |
| Robe | +5 | +5 | +5 | +5 | +5 | +5 |
| Skirt | +4 | +4 | +4 | +4 | +4 | +4 |
| Gloves | +2 | +2 | +2 | +2 | +2 | +2 |

The cutoff revision says that worn pieces give a slight XP boost only when
crafting essence during Great Orb Project. Cutoff talk oldid `5565562`,
timestamp `2012-05-04`, confirms that each piece contributes, and rejects
folklore that the effect varies with distance or Runecrafting level. Neither
revision gives a numeric rate. The live `0.25%` per-piece value is therefore a
registered bounded placeholder, capped structurally at four occupied slots and
1% total. A period server crafting routine or measured XP table would replace
it without changing the mechanic.

The immutable Darkan source artifact is:

`/Users/ArmanTarkhanian1/Documents/2012scape with bots/memory-bank/audit/sources/great-orb-project-oldids.json`

The artifact SHA-256 is
`2eb976379eb698f1a57ece1cc463a1e01a5726c81214e4da159a418bacb49c2b`;
its stored robes wikitext SHA-256 is
`fedd32d916c94bc4cb2708dce129f89372d149b2567de7cfa3c170f9f0cca260`.

OpenRS2 revision 742 pins the exact non-stackable, non-exchangeable item
identities and equipment slots:

| Colour | Hat | Robe | Skirt | Gloves |
| --- | ---: | ---: | ---: | ---: |
| Green | 13620 | 13619 | 13622 | 13623 |
| Blue | 13625 | 13624 | 13627 | 13628 |
| Yellow | 13615 | 13614 | 13617 | 13618 |

The canonical hat identity uses the goggles-on item. Moving the goggles is a
cosmetic inventory toggle and is outside this equipment/mechanic slice.

## Live translation

Wizard Elriss sells all 12 pieces one at a time for exactly 1,000 tokens
through the existing atomic purchase and direct-undo path. The items use the
shared inventory, Bank, equipment, discard, and recovery registries. Mixed
colours work because the XP effect is per occupied standard-robe slot, not a
same-colour set check.

The standard bonus applies only inside Great Orb Project essence crafting. It
does not pass through the ordinary altar Runecrafting bonus helper. When a
player mixes standard and Master pieces, both effects are calculated from the
same base XP and added, so the result does not compound one outfit bonus
through the other. Great Orb Project retains the unrounded awarded total in
its result, status, persistent match tracker, runtime XP award, telemetry, and
undo state.

Nine robe, skirt, and glove sprites use immutable pre-cutoff RuneScape Wiki
file revisions recorded in `assets_provenance.json`. The current renamed green,
blue, and yellow goggles-on hat files retain no pre-cutoff revision under those
titles. Their exact items and mechanics remain pinned by the cutoff page and
rev-742; current sprites are used only as labeled visual fallbacks and supply
no identity or mechanic evidence. Native canvases range from 28×22 to 31×28,
and the existing shop renders every item in the shared fixed 24-pixel slot.

## Review and boundaries

Root inspected the real 1200×760 dark offscreen-Qt render. The 30-entry selector
keeps the existing compact shop layout and fixed icon size; no new widget or
interaction pattern was introduced. Kimi K3 could not run because its fresh
quota preflight reported `fiveHour.usedPercent=100.0`; Opus could not run
because its quota preflight freshness was `unavailable` with refresh error
`Claude's usage endpoint is rate limited. The widget will retry in five
minutes.` Neither guard was bypassed.

Read-only Codex Workflows run `39cf4d5c-611c-4b9a-bb6a-f46653c1c7b2`
exceeded its bounded tool-output allowance (`70432` bytes observed against
`70000`) after two source reads and returned no findings. Root independently
reproduced the source assertions and reviewed the complete diff.

The required diff-only simplification run
`2bc0904b-34fc-43db-bf38-a67700d8a5a9` also failed closed before findings. It
left the five-file boundary to inventory Memory Bank files, then exhausted at
`63810` processed tokens against `50000` and `61353` tool-output bytes against
`45000`. Root inspected only its bounded partial status, did not repeat its
reads, and completed the five-file simplification review locally; no valid
deletion or behavioral defect remained.

- Talisman staves and Great Orb Project teleport tablets remain separate
  mechanic/data depth.
- Hat goggles position remains cosmetic-only depth.
- No wall clock, migration, new content, or owner design decision was added.

## Verification

Focused pure, registry, equipment, runtime, purchase, asset, and real Qt tests
cover all 12 exact rows, prices, equipment data, mixed-colour arithmetic,
Great-Orb-only scope, fractional XP continuity, and fixed selector icons. Full
plain and real offscreen-Qt discovery each pass 3,897 tests, with 479 expected
plain skips and three intentional Qt skips. Documentation audits 526 Markdown
and 431 HTML files; test quality reports zero hard issues across 3,863 tests in
177 files. Compilation, 26 tracked JSON files, diff whitespace, deterministic
asset fetching, all 284 Activities-item crops, and worktree safety pass.
Reachability improves to 2,256 items while holding at 1,499 actions, 168 known
orphan inputs, and 188 known blocked actions.
