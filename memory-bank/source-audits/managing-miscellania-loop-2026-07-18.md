# Managing Miscellania Review-Native Contract

Date: `2026-07-18`

Cutoff: RuneScape immediately before EOC, `2012-11-20`.

Status: **owner-design loop closed; the mechanic-complete horizontal slice is
implemented as of 2026-07-21. Remaining resource families, hidden bonus
selectors, and additional approval chores are catalog depth.**

## Pinned period evidence

`Managing Miscellania`, oldid `6500793`
(`2012-10-30T06:29:55Z`), establishes:

- completing `Throne of Miscellania` unlocks kingdom management;
- `Royal Trouble` adds Etceterian labour, raises the available subjects from
  ten to fifteen, raises the coffer cap from `5,000,000` to `7,500,000` coins,
  and raises the maximum source-day salary from `50,000` to `75,000` coins;
- productivity depends on approval, funded salary, and the chosen resource
  distribution;
- approval and salary update on the source daily boundary;
- approval falls by `2.5%` per source day, or `1%` after `Royal Trouble`;
- salary withdraws `10%` of the coffer balance, capped at the applicable
  `50,000` or `75,000`;
- the player may allocate subjects among the source resource families, with at
  most ten assigned to one family;
- the game records coffer withdrawals and approval rather than
  resource-by-resource production, so the distribution selected immediately
  before collection applies retroactively to the whole unclaimed period; and
- collection sends the calculated items directly to the Bank.

Source:

- <https://runescape.wiki/w/Managing_Miscellania?oldid=6500793>

The exact output tables, bonus-item rolls, approval-task recognition rolls,
storage ceiling, Fremennik-task effects, flatpack coffer values, and independent
period-lineage corroboration remain source work rather than owner questions.

## Answered-card production boundary

AnkiScape preserves the authentic collection-time allocation quirk.

Every answered-card day:

1. apply the source-shaped approval decay;
2. withdraw the source-shaped salary from the coffer;
3. convert that salary and the current approval into one funded,
   approval-weighted production-credit delta; and
4. add the delta to the unclaimed credit pool.

The background tick does **not** choose, roll, or store coal, herbs, flax, fish,
logs, seeds, nests, gems, caskets, clues, or other bonus items. When the player
clicks **Collect**, the current subject allocation converts the complete
unclaimed credit pool through the source output and bonus tables, atomically
deposits the result into the Bank, and clears only the claimed credit.

Changing the worker allocation before collection therefore changes the entire
unclaimed payout, exactly as the source allowed. This is an authentic mechanic,
not an AnkiScape exploit safeguard or a prospective workforce simulation.

The source daily boundary uses AnkiScape's global answered-card calendar and
never the wall clock. Review undo restores the approval, coffer, production
credit, and RNG deltas from the answered-card day tick. The bounded
direct-command undo path separately owns coffer transfers, allocation changes,
and collection payouts.

## Bespoke Activity surface

Managing Miscellania receives one dedicated Activity management panel rather
than generic target rows. It must present the connected state together:

- approval;
- coffer balance and deposit/withdraw controls;
- ten or fifteen available subjects according to quest state;
- source resource-family allocations with the ten-subject per-family cap;
- accumulated unclaimed production credit;
- a source-shaped reward preview for the current allocation; and
- one atomic **Collect** action.

The panel may reuse shared wallet, item-preview, button, and accessibility
components, but it must not scatter coffer, approval, distribution, and
collection across unrelated tabs. Allocation changes and coffer transfers are
free direct commands; they do not consume reviews.

## Approval maintenance

Approval restoration is a real foreground Miscellania action, not a free
background benefit and not an automatic tax on unrelated reviews.

The Activity exposes one **Help the subjects** review target and one saved
**Approval work** dropdown containing only the player's currently eligible
source chores. The default is the fastest source-backed eligible chore; the
same dropdown and behavior apply in both Casual and Advanced.

One successful review performs one selected source chore, awards its
source-shaped small skill XP, and applies its sourced approval opportunity.
`Again` performs no chore and grants no approval or foreground XP, although the
ordinary answered-card world clock still advances. At `100%` approval the
source prevents further chores, so the target becomes unavailable until
approval falls rather than silently awarding XP without approval work.

The exact eligible chores, skill requirements, recognition rolls, approval
increments, and XP remain source-data harvest. The implementation must not
flatten different chores into invented equal XP merely because they share the
same target.

## Explicit coffer funding

Managing Miscellania never withdraws coins automatically from the Bank. Coffer
funding remains an explicit, undoable direct command on the bespoke panel.

The panel provides:

- **Fund 1 day**;
- **Fund 7 days**;
- **Fund 30 days**;
- **Deposit maximum**; and
- exact deposit and withdrawal controls.

The duration buttons calculate the required target balance from the live quest
state and source salary formula; they are conveniences over the authentic
coffer rather than invented recurring payments. If the coffer cannot fund the
maximum salary, the source-shaped lower withdrawal produces proportionally
lower credit. An empty coffer produces no credit. No checkbox, Casual/Advanced
split, recurring Bank transfer, or silent fallback exists.

## Worker allocation UI

The panel preserves the authentic individual-subject allocation rather than
flattening it into `Profit`, `Supplies`, or `Balanced` presets. Each source
resource family receives one row with:

- decrement and increment controls;
- a **Max** control;
- visible worker pips; and
- the source ten-subject per-family cap.

Ten subjects are available after `Throne of Miscellania`; `Royal Trouble`
raises the shared pool to fifteen without raising the per-family cap.
Allocation persists until the player changes it, and every change immediately
recomputes the reward preview against the complete unclaimed production-credit
pool.

Allocation changes are free, undoable direct commands. The same exact surface
appears in Casual and Advanced. AnkiScape does not provide a speculative
max-profit optimizer before its economy can support a meaningful answer.

## Owner-design closure and remaining source work

Managing Miscellania has no remaining owner-facing product fork. Implementation
still requires the exact output tables, bonus-item rolls, approval-chore
requirements and outcomes, storage ceiling, Fremennik-task effects, flatpack
coffer values, and independent period-lineage corroboration named above. Any
missing row remains source work rather than permission to invent a second
management model.

## Horizontal implementation harvest — 2026-07-21

The same immutable revision, oldid `6500793` at
`2012-10-30T06:29:55Z`, closes the smallest exact collection catalog needed to
exercise all distinct kingdom mechanics:

- ten Mining subjects produce `546 Coal` plus `3 gems` per fully funded,
  100%-approval source day;
- ten Woodcutting subjects produce `892 Maple logs`, with one bird nest per
  complete `100` logs;
- ten Hardwood subjects produce either `301 Teak logs`, `204 Mahogany logs`,
  or the mixed `121 Teak logs + 121 Mahogany logs`; and
- chopping maple trees at level `45 Woodcutting` gives `100 XP` and one
  approval point per recognized log.

Source: <https://runescape.wiki/w/Managing_Miscellania?oldid=6500793>.

The horizontal catalog deliberately uses those three families and the Maple
approval chore. They prove fixed output, derived bonus output, player-selected
sub-output, eligible foreground approval work, the individual-subject cap,
and retroactive collection-time allocation without waiting for every herb,
seed, fish, flax, or bonus table.

The period row names only `3 gems`, not the hidden gem selector. The live
horizontal row therefore uses `3 Uncut sapphire` as a disclosed lowest-value
representative, not as a historical claim about the selector. Bird nests use
the existing `Bird's nest (seeds)` representative identity while preserving
the exact `floor(Maple logs / 100)` count. Those two identity choices remain
data-depth abstractions; the quantities and the surrounding collection
mechanics are source-shaped.

The review translation is the already owner-settled global calendar:
`240 answered cards = one source day`. A migrated save anchors the new kingdom
state to its current review day, so installing the slice never creates
retroactive salary or production. The 2011-11-25 period interface art revision
is normalized under `activityicons/managing_miscellania.png`; its immutable
source identity is recorded in `assets_provenance.json`.

Remaining source depth:

- exact herb, flax, fishing, and Farming output tables;
- the hidden gem, seed, ring, casket, clue, and nest-type selectors;
- additional approval chores and any recognition rolls;
- the source storage ceiling, Fremennik-task modifiers, and flatpack coffer
  values; and
- independent period-lineage corroboration beyond the pinned cutoff wiki
  revision.

None of those rows changes the implemented entry, coffer, salary, approval,
worker-allocation, collection, persistence, undo, cadence, or UI mechanics.
