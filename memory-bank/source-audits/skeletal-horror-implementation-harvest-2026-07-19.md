# Skeletal Horror Implementation Harvest

Date: `2026-07-19`

Cutoff: RuneScape immediately before EOC, `2012-11-20`.

Status: **phase identity, LP thresholds, attack-style changes, rewards, cadence,
and limb interactions are source-closed. The family shipped on 2026-07-26 under
registered placeholders for the phase accuracy/defence stats and a stand-in for
post-quest wish-list state; see "Integration disposition" below.**

This is the implementation follow-up to
`skeletal-horror-loop-2026-07-18.md`. It does not change that owner-settled
review-native design.

## Closed period values

`Skeletal horror`, oldid `6278479` (`2012-09-21T20:50:07Z`), supplies:

- one continuous `3,500`-LP encounter;
- combat levels `320 → 260 → 180 → 100`;
- maximum hits `334 → 214 → 154 → 74`;
- attack speed `4`;
- Melee and Magic initially, with Magic lost after both arms are removed;
- right arm, left arm, then tail as the weakening order;
- first rewards of `10,000` Slayer XP and `7,000` Prayer XP;
- repeat rewards of `1,250` Slayer XP and `1,000` Prayer XP;
- a `1/20` elite-clue chance;
- a recurring weekly allowance after the Odd Old Man rebuilds the creature;
  and
- the Rag and Bone Man and Fur 'n Seek wish lists as the access gate.

Literal source:

- <https://runescape.wiki/w/Skeletal_horror?oldid=6278479>

The latest pre-cutoff talk revision, oldid `5579987`
(`2012-05-08T05:41:03Z`), independently records the first form as `350`
historical hitpoints (`3,500` life points):

- <https://runescape.wiki/w/Talk:Skeletal_horror?oldid=5579987>

Two dated Tip.It captures recover the server-visible phase thresholds that the
wiki article's Monster Examine montage only approximates:

- the level-260 second form has `275` historical hitpoints and loses its left
  arm after another `75`;
- the level-180 third form has `200` historical hitpoints and loses its tail
  after another `75`.

Combined with the independently pinned `350` starting hitpoints and the
sequential limb order, the exact continuous thresholds are therefore:

| Transition | Remaining LP | Damage since previous phase |
|---|---:|---:|
| right arm; `320 → 260` | `2,750` | `750` |
| left arm; `260 → 180` | `2,000` | `750` |
| tail; `180 → 100` | `1,250` | `750` |
| death | `0` | `1,250` |

Dated captures:

- `2010-02-10T03:09:08Z`,
  <https://web.archive.org/web/20100210030908/http://www.tip.it/runescape/?rs2monster_id=1318>
- `2010-02-10T03:09:13Z`,
  <https://web.archive.org/web/20100210030913/http://www.tip.it/runescape/?rs2monster_id=1319>

This is dated Wayback material admitted by the permanent source standard; it
does not rely on the modern post-EOC Tip.It rows.

## Cache identity and interactions

Both rev 727 (`2012-07-24`) and rev 742 (`2012-11-07`) contain the same client
identities:

| ID | Name | Client option |
|---:|---|---|
| `9176` | Skeletal horror | Attack |
| `9177` | Skeletal horror | Attack |
| `9178` | Skeletal horror | Attack |
| `9179` | Skeletal horror | Attack |
| `9180` | Skeletal horror | Attack |
| `9181` | Right hand | Pick-up |
| `9182` | Left hand | Pick-up |
| `9183` | Tail | Pick-up |
| `15217` | Arm | Bury |
| `15218` | Arm | Bury |
| `15219` | Tail | Bury |

The five boss identities and three ground-limb identities are NPC definitions;
the three buryable limb identities are item definitions. These caches prove
identity and client interaction only, not combat stats or transition logic.

Cache roots:

- `/Users/ArmanTarkhanian1/Library/Caches/codex/2012scape-openrs2/extracted/727-2012-07-24/cache`
- `/Users/ArmanTarkhanian1/Library/Caches/codex/2012scape-openrs2/extracted/742-2012-11-07/cache`

## Concrete implementation blockers

### Phase accuracy and defence remain source-blocked

AnkiScape's live Combat kernel needs the enemy's Attack or Magic level for its
accuracy roll and Defence level for the player's accuracy roll. The sources
above close LP, maximum hit, attack speed, styles, and phase transitions, but
do not state those levels.

Darkan commit `bc97c449aa92f6c8b69fb77ec9aea655b9d231a9` contains four Skeletal
Horror combat-definition files under
`data/npcs/combatdefs/uncategorized/skeletal_horror/`, but every filename is
explicitly marked `(nostats) (noanims)`. The rows also copy `3,500` LP,
maximum hit `334`, and Melee across every form, contradicting the pinned phase
maximum hits and the sourced initial Magic attack. They are leads, not
shippable phase tables.

`developer-information/npcListBonuses.txt` supplies one shared defence-bonus
array for all five identities, but no Attack, Magic, Strength, or Defence
levels. Combat level and maximum hit do not uniquely determine those missing
stats. The blocked values are not hidden probabilities, so the provisional
roll exception does not apply.

### Wish-list access is a quest-program dependency

The generated quest catalog currently represents completion of
`rag_and_bone_man` and `fur_n_seek`; it does not persist the two post-quest
wish-list completions that the period source specifically requires. Gating the
boss on ordinary quest completion would silently weaken the source gate.

The Darkan quest-parity thread owns that quest-state restoration. This is not
an owner design question and this pass does not edit quest stages, invent a
replacement flag, or duplicate quest work.

## Integration disposition

Superseded on 2026-07-26. The re-issued breadth goal admits a **registered
placeholder** where this audit had recorded a hard blocker, so the family
shipped rather than waiting:

- the four phase stat blocks remain placeholders in
  `memory-bank/placeholder-values.md`, marked at the value in
  `data/skeletal_horror_data.py`;
- the shared bonus array and two-style selector weight were recovered from
  Darkan's rev-727 dump and combat script and retired on 2026-07-27;
- the wish-list dependency is stood in by two explicit commands, recorded as an
  open design decision in `memory-bank/design-thread-queue.md` section 3.1.

Nothing in the *sourced* set — thresholds, maximum hits, styles, rewards,
cadence — is a placeholder. The original reasoning below still holds for why
those may not be guessed.

The implementation path this audit predicted was followed exactly:

1. register the four phase rows as encounter-only Combat identities;
2. persist the continuous enemy LP and current phase through live six-tick
   reviews;
3. perform the owner-settled automatic pick-up and burial transaction at
   `2,750`, `2,000`, and `1,250` LP;
4. award the first/repeat Slayer and Prayer XP, clue roll, and simulated-week
   lockout atomically on victory; and
5. use ordinary live-Combat death, abandonment, grave, and undo paths.

## Workflow note

Read-only Codex Workflow run
`e8e57a3d-3516-4f2d-a148-97f1c6249896` was cancelled without output after a
different provider startup held the serialized machine-wide pre-session
handshake. Both requested leaves remained before `thread.started` with zero
stdout, zero stderr, zero tokens, and no session ID. The root independently
reproduced every finding above; no reviewer result is represented as evidence.
