# Design 2 → cadence-canonical reconciliation handoff

Date: 2026-07-17

Canonical destination thread: **Design** (`019f5d83-d80c-7240-b6a4-bf89bd349af9`)

Retiring source thread: **Design 2 overnight**
(`019f6ef2-2d5f-7002-8d89-906fc375222a`)

## Authority and reconciliation rule

The owner selected the other Design thread as canonical because its live cadence
kernel work is upstream of later review-count abstractions.

On any timing, rate, action-unit, duration, or review-cost conflict:

1. the settled live cadence contract and verified implementation win;
2. preserve the product intent recorded below;
3. recalculate the numeric mapping rather than silently retaining a pre-kernel
   review count; and
4. ask the owner only when two recalibrated models would produce materially
   different play.

Both threads share the canonical checkout. Do **not** cherry-pick, merge a
worktree, or reapply these files. Reconcile the already-visible dirty changes in
place and preserve concurrent cadence implementation files.

## Durable decisions from Design 2

### Achievements, diaries, capes, and completion

Authoritative design:
`memory-bank/achievement-diary-item-grants-design.md`.

Important settled outcomes include:

- eight cutoff equipment families, twelve curated tasks per tier, and the
  separate Burthorpe/Taverley and Miscellaneous sets;
- visible cross-tier progress, sequential atomic claims, authentic taskmaster
  presentation, and no per-task regional rewards;
- Taskmaster as completion state/Cabinet seal/Comp requirement rather than an
  invented achievement cape;
- source-shaped Skill, Quest, Dungeoneering 120, Max, Completionist, trimmed
  Completionist, milestone, and Veteran capes;
- first-99 untrimmed art preserved display-only through the Cabinet;
- Music Log under Collections;
- Treasure Trails explicitly parked for its own later deep grill; and
- exact effort and review-count values require cadence reconciliation before
  implementation.

Related files:

- `memory-bank/ankiscape-completion-starter-grill-2026-07-17.md`
- `memory-bank/future-work-kanban.md`
- `memory-bank/status-updates/achievement-system-concept-lab-2026-07-17.html`

### Road to Restoration comparator

Authoritative audit:
`memory-bank/source-audits/road-to-restoration-design-lessons-2026-07-17.md`.

Modern Road work is design-quality evidence only, never 2012 parity evidence.
The adopt/adapt/reject matrix covers:

- removal of monetisation-derived coercion;
- free mechanics information, Help, and search;
- narrow audits of concrete progression outliers rather than a global novice
  buff;
- DailyScape forgiveness;
- Aura/Loyalty repair;
- reduced aggregate setup ritual;
- GE transparency;
- shared search, visual coherence, and asset provenance;
- parked multiplayer/social work; and
- rejection of post-cutoff level-120 and mechanical imports.

### Aura and Loyalty

Settled product intent:

- preserve the cutoff Aura catalog and ordinary Aura equipment slot;
- Aura selection and automatic activation are mode-independent equipment
  behavior; Advanced does not own equipment slots;
- the equipped Aura automatically activates when available on the next eligible
  action;
- start with 107,500 Loyalty Points, exactly one cutoff-era year;
- earn 100,000 points per 7,200 world-calendar reviews, targeting the
  1,301,000-point representative practical portfolio after twelve simulated
  months;
- Loyalty never expires and never gates Completionist;
- content balance never assumes a high-tier Aura;
- Aura effect windows begin and deplete only on eligible actions, while
  cooldowns remain answered-card/review driven.

Cadence reconciliation required:

- re-express every Aura duration and cooldown through the live kernel's declared
  calendar, short-duration, or foreground-action class;
- do not assume the pre-kernel “one eligible action = one old review” mapping;
- keep the 7,200-review Loyalty payout only if the cadence kernel retains the
  settled 240-review world day independently of its 1,000-review balancing
  hour.

### Recurring activity forgiveness

Owner accepted this target design:

- recurring activity eligibility banks one current entry plus one reserve,
  default cap two;
- only eligibility accumulates; the player still performs the activity;
- no XP, items, currency, stages, or completion resolve automatically;
- UI shows available entries but never overflow/lost-value warnings;
- banked entries never become progression requirements; and
- shop stock, growth, passive producers, and equipment charges retain their own
  owning systems.

This intentionally supersedes the previous no-stacking design, but it is not
implemented. It is recorded in:

- `memory-bank/simulation-time-boundary-2026-07-16.md`, Decision 2;
- `memory-bank/systemPatterns.md` as a pending target; and
- the Road audit.

Cadence reconciliation required: derive entry accrual from the canonical world
calendar and undo contract. Do not create a second timer.

### Help and free mechanics details

`memory-bank/help-system-contract-2026-07-16.md` now adds a shared optional
`Details` surface, available in both modes:

- show genuinely known effective success chance, expected output/damage range,
  XP, failure consequences, and readable modifier contributions;
- show current prices/stock but not future shop predictions;
- use qualitative wording rather than false precision; and
- hide equations, internal ticks, RNG state, source files, and developer
  classifications.

### Tears of Guthix starter activity

Owner accepted a short automatic multi-review session rather than a one-review
weekly lamp:

- Quest Points determine a capped collection-session length;
- each eligible successful action advances one automatic collection beat;
- one status line narrates stream result, tear delta, total, and remaining
  beats;
- green streams may subtract tears;
- leaving preserves the session; and
- completion rewards the eligible skill with the least XP.

Exact beat count and reward magnitude are deliberately unresolved.

Source correction:
`memory-bank/source-audits/tears-of-guthix-cutoff-reconciliation-2026-07-17.md`
records that oldid `6579712` is dated 19 November but explicitly contains stale
pre-6-November-refresh mechanics. The refreshed activity, weekly/XP-or-QP
eligibility, ornate bowl, and lowest-XP routing are safe; exact post-refresh
collection and XP magnitude remain source-blocked.

Cadence reconciliation required: the accepted product unit is a short session,
but “one collection beat” must attach to the live foreground-action/cadence
contract rather than assuming one legacy review.

## Files changed by the retiring branch

Tracked Memory Bank files:

- `memory-bank/achievement-diary-item-grants-design.md`
- `memory-bank/ankiscape-completion-starter-grill-2026-07-17.md`
- `memory-bank/future-work-kanban.md`
- `memory-bank/help-system-contract-2026-07-16.md`
- `memory-bank/simulation-time-boundary-2026-07-16.md`
- `memory-bank/source-audits/agility-complete-content-inventory-2026-07-15.md`
- `memory-bank/systemPatterns.md`

New files:

- `memory-bank/source-audits/road-to-restoration-design-lessons-2026-07-17.md`
- `memory-bank/source-audits/tears-of-guthix-cutoff-reconciliation-2026-07-17.md`
- `memory-bank/status-updates/achievement-system-concept-lab-2026-07-17.html`

The source thread made no code changes and no commit. The current code changes
in `__init__.py`, `cadence_kernel.py`, `logic_pure.py`, `runtime_actions.py`,
`cadence_coverage.py`, and `cadence_live.py` belong to the cadence-canonical
thread and must not be attributed to or overwritten by this handoff.

## Required destination-thread action

1. Finish or stabilize the cadence kernel first.
2. Reconcile the Memory Bank edits above against the final cadence taxonomy and
   mappings.
3. Keep all compatible product decisions.
4. Recalculate pre-kernel numeric review counts.
5. Present only genuine remaining owner conflicts.
6. Continue the completion/activity grill in the canonical Design thread.

Kimi K3 is the requested background design critic until the owner says Fable
quota has reset. Kimi's OpenRouter preflight works, but max-reasoning calls have
been slow; do not block interactive owner questions indefinitely waiting for a
silent consultation.
