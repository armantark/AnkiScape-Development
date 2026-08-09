# Great Orb Project talisman staves

Date: `2026-08-09`

Cutoff: RuneScape immediately before EOC, `2012-11-20`.

## Period evidence

RuneScape Wiki `Runecrafting staff` oldid `6430449`, timestamp
`2012-10-16T20:39:23Z`, identifies the unequippable, non-stackable base staff,
its 10,000-token Wizard Elriss price, and its use with a talisman to make the
matching altar staff:

<https://runescape.wiki/w/Runecrafting_staff?oldid=6430449>

The immutable Darkan copy is:

`/Users/ArmanTarkhanian1/Documents/2012scape with bots/memory-bank/audit/sources/runecrafting-staff-oldid-6430449.json`

Its SHA-256 is
`4f89f6a45734cc40d1a3b7a684b89372325d7cd14fe03efb782a4c680e29b41d`.

The following final dated item-page revisions pin the twelve ordinary names
at the cutoff. Their mechanic is corroborated by the older Air revision below;
their post-update combat infoboxes are not used as pre-EOC stat evidence.

| Staff | Oldid | Timestamp |
| --- | ---: | --- |
| Air | 6593647 | `2012-11-20T11:27:27Z` |
| Blood | 6593681 | `2012-11-20T11:29:33Z` |
| Body | 6593684 | `2012-11-20T11:29:43Z` |
| Chaos | 6593720 | `2012-11-20T11:31:56Z` |
| Cosmic | 6593734 | `2012-11-20T11:32:53Z` |
| Death | 6593753 | `2012-11-20T11:33:51Z` |
| Earth | 6593786 | `2012-11-20T11:35:09Z` |
| Fire | 6593814 | `2012-11-20T11:35:59Z` |
| Law | 6594001 | `2012-11-20T11:40:43Z` |
| Mind | 6594035 | `2012-11-20T11:42:21Z` |
| Nature | 6594075 | `2012-11-20T11:44:32Z` |
| Omni | 6594094 | `2012-11-20T11:45:41Z` |
| Water | 6594888 | `2012-11-20T13:11:34Z` |

Air talisman staff oldid `6080692`, timestamp `2012-08-12T14:37:59Z`,
establishes the ordinary construction and access behavior: one Air talisman
combines with one base staff, the result equips in the weapon slot, and the
wielded staff enters the matching altar while freeing one inventory slot.
It also records the Abyss-eye distraction claim:

<https://runescape.wiki/w/Air_talisman_staff?oldid=6080692>

The immutable copy SHA-256 is
`f83d0f072273f6b05d147ab330ea2e7574042b8fa41710725ee6ba4ef0fbae6a`.

Omni-talisman staff oldid `6080707`, timestamp `2012-08-12T14:49:51Z`,
establishes the special conversion and altar exceptions. Wizard Korvak binds
one Omni-talisman to one base staff for free; the talisman cannot be removed.
The wielded Omni staff enters every modeled ordinary altar except Law. The Law
talisman staff has zero combat bonuses and remains valid on Entrana:

<https://runescape.wiki/w/Omni-talisman_staff?oldid=6080707>

The immutable copy SHA-256 is
`22939865f75a58ff2aee975a7eb209d62a57227e8cdee96323cce8970e208264`.

The authentic rev-742 item table pins base item `13629`, ordinary staff items
`13630` through `13641` in altar order, and Omni item `13642`. It records every
staff as non-tradeable. The ordinary outputs equip one-handed in the weapon
slot. All non-Law rows have `-1` slash attack, `+7` crush attack, `+5` Magic
attack, `+2/+3/+1` stab/slash/crush defence, and `+33` Strength. Air, Mind,
Fire, and Body have `+15` Magic defence; the other non-Law ordinary rows and
Omni have `+16`. Law has zero bonuses. Ordinary and Law rows use attack speed
5; rev-742 pins Omni at attack speed 4 and therefore supersedes the older
wiki's speed-5 infobox for the live value:

`/Users/ArmanTarkhanian1/Downloads/game-main/data/cfg/items.yml:157182-157614`

No period source inspected for this slice awards Runecrafting XP for binding a
talisman to a staff. The live action therefore gives zero XP. This is not a
placeholder: no recovered period record establishes a hidden value that needs
replacement.

## Live translation

Wizard Elriss sells the base staff one at a time for exactly 10,000 Great Orb
Project tokens through the existing atomic purchase and direct-undo route.
The Runecrafting target selector adds one irreversible binding row for each of
the twelve modeled talisman altars. Each review consumes one carried base staff
and one carried matching talisman, produces the exact non-tradeable weapon, and
inherits the corresponding altar's existing quest gate. The equipped output
provides the same 28-slot essence capacity already used by tiaras and the
Wicked hood.

Wizard Korvak's free Omni conversion remains an instantaneous shop action. It
atomically consumes the Omni-talisman and base staff, produces the Omni staff,
and uses the existing direct-action undo. The output grants access to every
modeled talisman altar except Law. Law's dedicated staff grants Law access and
uses its exact zero-bonus equipment row.

Save repair treats an Omni-tiara or Omni staff in inventory or equipment as
proof that Elriss's one-time 13,605-XP claim already occurred. This closes the
older equipment-only state hole without changing the save schema.

Binding recipes now declare their real carried-pack requirements. This also
repairs the older tiara-binding rows, which previously bypassed the processing
overlay and consumed directly from the bank. No wall clock, new save state, or
schema migration is involved.

Fourteen normalized sprites are stored in `runecraftingitems/`, keyed through
the shared item registry and provenance manifest. The existing Runecrafting
tree and Great Orb reward selector render them through the established icon
sizes; no new widget or interaction pattern was introduced.

## Boundaries

- The Abyss is not a live AnkiScape substrate. The sourced eye-distraction
  behavior is recorded here but is not implemented as an inert bonus.
- Staff binding is irreversible in gameplay. Review undo and direct-action
  undo remain application-history rollback, not an in-world unbinding action.
- The existing quest-unlock table owns Cosmic, Death, and Blood access. This
  slice does not edit or duplicate Darkan-owned quest content.
- Great Orb Project teleport tablets remain a separate depth slice.
- No placeholder or owner design decision was added.

## Verification contract

Focused pure, registry, equipment, runtime, hook, asset, and real offscreen-Qt
tests cover exact prices and IDs, carried binding, material consumption,
irreversibility, quest-gate inheritance, ordinary and Omni altar access, the
Law exception, exact representative stats, direct undo, target grouping,
tooltips, and fixed-size icons. The focused pure/integration packet passes 413
tests, and the complete real Qt widget module passes 394.

Full plain and real offscreen-Qt discovery each pass 3,903 tests, with 479
expected plain skips and three intentional Qt skips. Documentation audits 527
Markdown and 431 HTML files; test quality reports zero hard issues across 3,869
tests in 177 files. Compilation, tracked JSON, diff whitespace, deterministic
asset fetching, global UI-asset normalization, and worktree safety pass.
Reachability improves to 1,511 actions and 2,270 items while the known 168
orphan inputs and 188 blocked actions remain unchanged.
