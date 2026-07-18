# Managing Miscellania Review-Native Contract

Date: `2026-07-18`

Cutoff: RuneScape immediately before EOC, `2012-11-20`.

Status: **collection-time allocation, bespoke Activity surface, and
approval-maintenance review target owner-settled; coffer funding still under
grill.**

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

## Still open in the owner grill

The next product fork is whether coffer funding stays entirely explicit or may
draw automatically from the Bank.
