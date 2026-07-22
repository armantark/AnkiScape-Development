# Varrock Museum horizontal readiness

Date: `2026-07-22`

Cutoff: RuneScape immediately before EOC, `2012-11-20`.

Status: **period values, the horizontal review translation, and shared
runtime/UI integration are closed.**

## Pinned period evidence

The literal wikitext was fetched through the RuneScape Wiki API and inspected,
not inferred from a current rendered page.

- `Varrock Museum`, oldid `6550044`,
  `2012-11-12T19:18:01Z`:
  <https://runescape.wiki/w/Varrock_Museum?oldid=6550044>
- `Kudos`, oldid `6514304`, `2012-11-01T00:26:08Z`:
  <https://runescape.wiki/w/Kudos?oldid=6514304>
- `Natural history quiz`, oldid `6459188`,
  `2012-10-23T14:10:49Z`:
  <https://runescape.wiki/w/Natural_history_quiz?oldid=6459188>

These revisions establish:

- `183` total source Kudos: `28` from the natural-history quiz, `50` from
  specimen exhibits, `95` from quest stories, and `10` from the first
  Dahmaroc statue;
- fourteen quiz displays, three correct answers per display, `2` Kudos per
  completed display, and the one-time Orlando reward of `1,000` Hunter plus
  `1,000` Slayer XP;
- specimen-cleaning gates of completed `The Dig Site`, worn Leather gloves
  and Leather boots, and Trowel, Rock pick, and Specimen brush in the activity's
  manually configured carried pack;
- five exhibit finds worth `10` Kudos each: Pottery, Old symbol, Ancient
  symbol, Ancient coin, and Old coin;
- Clean necklace teaching the ability to enchant Ruby necklaces into Digsite
  pendants;
- the complete quest-story ledger, including Dagon'hai history for What Lies
  Below and the real Prophecy tablet for the full Glorious Memories award;
- one-time threshold rewards at `51`, `101`, and `151` Kudos: `1,000` Mining;
  `2,500` Crafting and Mining; then `4,000` Crafting, Hunter, Prayer, Slayer,
  and Smithing XP.

OpenRS2 rev-742 independently establishes the client identities and options:

| Item | ID |
|---|---:|
| Specimen brush | `670` |
| Rock pick | `675` |
| Trowel | `676` |
| Uncleaned find | `11175` |
| Pottery | `11178` |
| Old coin | `11179` |
| Ancient coin | `11180` |
| Ancient symbol | `11181` |
| Old symbol | `11182` |
| Digsite pendant (1–5) | `11190–11194` |
| Clean necklace | `11195` |

## Darkan boundary

The Darkan restoration task supplied a read-only handoff rather than a new
harvest. Its current `MuseumKudos.kt` owns a narrow persistent total and an
award-once helper. Runtime evidence independently proves the existing
Meeting History and Defender of Varrock `+5` claims. `VarrockMuseum.java`
remains an interface-ID stub, and Darkan has no quiz, specimen-cleaning,
display-case, threshold-reward, or complete Minas ledger implementation.

The unaudited `specimen_tray.json` drop table is not tied to Varrock Museum and
is not used as evidence or implementation data.

## Horizontal translation

The settled contract in
`memory-bank/source-audits/recon-coverage-closure-2026-07-18.md` owns this
family: persistent Kudos, one-time quiz and quest landmarks, repeatable
specimen cleaning until its Kudos pool is exhausted, and direct threshold
claims.

No approved period-lineage implementation supplies a specimen probability.
The hidden-roll calibration gate is therefore not met. The horizontal runtime
does not fabricate one: a cleaning review represents cleaning enough samples
to obtain the next missing exhibit. After all five exhibits, one final
cleaning review represents finding and handing in the Clean necklace. This is
a disclosed AnkiScape review translation, not a historical drop sequence or
rate.

## Explicit omissions

- Ghostly Robes is worth the remaining `10` quest-story Kudos, but AnkiScape
  has no miniquest completion state. The live quest ledger therefore exposes
  `85` of the sourced `95` until that dependency exists.
- Shattered Heart is separately contracted but not implemented. Its first
  statue contributes the remaining `10` to the source maximum only when that
  owner ships.
- The source describes additional antique lamps and the storage-crate ordinary
  reward table, but the period evidence inspected here does not close the
  complete lamp-to-milestone mapping or a server-side cleaning distribution.
  Those are data depth and remain `source_blocked`.
- Fossil Island access is explicitly unreleased at the cutoff and is excluded.

The executable horizontal maximum is therefore `163` Kudos: quiz `28`,
specimens `50`, and currently representable quest stories `85`. This still
reaches and exercises every threshold reward.

The two physical story items must be placed in the Museum carried pack before
Minas can record their stories. Merely owning either item in the flat bank does
not satisfy the source's "bringing" requirement.

## Verification map

`tests/test_varrock_museum.py` covers source totals, state repair, all fourteen
quiz beats, Orlando's one-time XP, exact cleaning gates, the rate-free cleaning
translation, all five exhibits, pendant unlock, quest-item gates, one-time
Minas claims, all three threshold packages, cadence disclosure, and normalized
period assets. Focused runtime, migration, Magic-gate, direct-undo, registry,
and real offscreen Qt interaction checks also cover the shared seams.
Current-HEAD ordinary discovery passes all `2,419` methods with `306` declared
environment skips. Full real offscreen Qt discovery passes its `2,417`-method
snapshot with one skip; the concurrent two-test Familiarisation addition
separately passes its complete `28`-test module under ordinary Python and real
offscreen Qt. Documentation, test-quality, provenance, asset-normalization,
compilation, diff, and worktree-guard checks pass. Native Anki and external
Kimi/Fable taste claims are deliberately absent while the Mac is locked and the
owner quota hold remains active.

Self-contained closure report: <https://fe2ohwaibdw3.postplan.dev>.
