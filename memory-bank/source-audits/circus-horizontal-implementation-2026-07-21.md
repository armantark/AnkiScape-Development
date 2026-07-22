# Big Top Bonanza horizontal implementation — 2026-07-21

Status: **mechanic-complete horizontal slice implemented; exhaustive costume variants and hidden period curves remain data depth.**

## Authority and cutoff evidence

The owning design remains
`memory-bank/source-audits/circus-performance-loop-2026-07-17.md`. The period
gameplay table is pinned to literal RuneScape Wiki wikitext from
`Balthazar Beauregard's Big Top Bonanza`, oldid `6554790`, timestamp
`2012-11-14T06:58:34Z`:

- <https://runescape.wiki/w/Balthazar_Beauregard%27s_Big_Top_Bonanza?oldid=6554790>

The revision proves the safe weekly activity, six skill performances, quest
gates, ten-attempt and six-attempt limits, suggested-level bands, zero XP on
failure, once-per-level-band XP, complete trick/XP tables, and costume score
bands. OpenRS2 revision 742 supplies the cutoff item identities and interaction
options for Circus ticket `13663`, Giant's hand `13666`, Clown hat `13667`,
Ringmaster hat `13672`, Acrobat hood `13680`, and Firemaker's tabard `23003`.
The immutable local cache is:

`~/Library/Caches/codex/2012scape-openrs2/extracted/742-2012-11-07/cache`

The transcribed runtime tables in `circus_data.py` contain:

- 20 Magic tricks across levels 10–99;
- 20 Ranged target variants across levels 10–99;
- 20 Agility tightrope/juggling variants across levels 10–99;
- six Fire-breathing tricks at levels 74, 78, 82, 87, 91, and 95;
- six Flaming poi tricks at the same levels; and
- five Thieving magic tricks at levels 50–90, repeated only after every unique
  trick when filling the source ten-attempt performance.

## Explicit source blocks and bounded translations

Oldid `6554790` proves non-zero under-level success and non-certain over-level
success, but does not expose the success curve. `circus_logic.py` therefore
isolates the horizontal calibration at
`clamp(0.50 + (skill_level - suggested_level) / 200, 0.10, 0.95)`. It is a
declared bounded abstraction, not a claimed historical formula.

The oldid internally conflicts on a successful above-level attempt: one passage
describes a value 40 levels below the attempted trick, while the detailed
strategy section says half the player's current level. The implementation uses
the detailed section conservatively and maps to the highest transcribed band at
or below half the current level. This remains replaceable if stronger period
evidence resolves the conflict.

The exact audience-score algorithm is also source-blocked. The isolated score
translation uses `50 + suggested_level`, anchored to the article's observed
roughly 150-point level-99 trick, then applies small disclosed strategy,
variety, and owned-costume modifiers. Exact period reward thresholds remain
literal: Audience `1–500`, Acrobat or Firemaker `501–1000`, Clown `1001–1200`,
and Ringmaster `1201+`.

## Horizontal mechanic boundary

The implementation keeps one representative period-identified item from each
reward band: Giant's hand, Acrobat hood, Firemaker's tabard, Clown hat, and
Ringmaster hat. This is sufficient to exercise award, inventory, equipment,
loss, free reclaim, persistence, and undo. Colour, gender, and remaining set
pieces are deferred catalog depth, not missing mechanics.

All five representatives have normalized period sprites. Their provenance
timestamps in `assets_provenance.json` range from 2010-01-07 through
2012-01-11. The standard alpha-bounds audit reports no remaining transparent
padding. Giant's hand uses the rev-667 weapon slot and type 7; the two hats use
the head slot. Firemaker's tabard uses its period body-slot identity with zeroed
bonuses because the older rev-667 equipment block predates item `23003`.

The UI lives only on the paginated Activities surface. It exposes performance,
strategy, and Casual/Advanced setup without adding another scroll region.
Advanced opens a fixed source-bounded routine editor. The score strip swaps the
mutually exclusive Acrobat and Firemaker `501–1000` reward according to the
selected performance, and the performance picker marks quest locks and weekly
completion.

## Atomicity, persistence, and cadence

One successful review resolves one complete performance, grants its single
skill's XP, scores the audience, awards at most one new representative costume,
and closes only that performance for the answered-card week. Direct policy,
routine, abandon, and reclaim commands use the normal direct-action undo stack.
Review resolution, XP, reward, weekly gate, and the answered-card world-clock
advance share one review undo snapshot.

The weekly index is `answered_cards // 1680`; wall-clock time is never read.
Cadence coverage classifies the action as an atomic activity group and forbids
foreground multiplication from beginning another performance on the same
answer. Save config version 72 migrates the retired Agility-only week and
audience counters, then removes their legacy fields.

## Independent UI review

Fable was deliberately held in reserve under the owner's quota instruction.
Kimi's live quota gate failed closed at four percent weekly remaining. Opus had
quota available, but the Claude CLI required a new login, so no external model
review ran and no such signoff is claimed. Codex inspected the four normalized
dark-mode renders directly. That audit found one material legibility gap: the
available-state card did not say that its remaining count was weekly. The status
now reads `N left this answered-card week`; locked rows still name their quest
gate and completed rows say `done this week`. The mutually exclusive
`501–1000` reward bands, fixed-count editor copy, named score strip, icon
tooltips, result line, setup-mode labels, and accessible names were verified in
the rendered and offscreen-Qt surfaces.

## Verification scope

Focused coverage proves the six tables and gates, atomic success and failure,
once-per-level XP, Entertain variety, above-level translation, weekly rollover,
single-performance abandon, reclaim, legacy migration, runtime dispatch,
direct-action undo, review/world-clock undo, equipment generation, paginated UI,
reward-row switching, locked-row annotations, and normalized assets. Final
full-suite, native Anki, reachability, documentation, and closure results are
recorded in the matching status artifact and core Memory Bank files.
