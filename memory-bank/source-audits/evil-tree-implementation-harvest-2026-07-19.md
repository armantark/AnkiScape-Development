# Evil Tree Implementation Harvest

Date: `2026-07-19`

Cutoff: RuneScape immediately before EOC, `2012-11-20`.

Status: **implemented and verified from period tables plus the disclosed
bounded abstractions below.**

Owning design:

- `memory-bank/source-audits/evil-tree-loop-2026-07-18.md`

This note harvests implementation values only. It does not reopen the settled
three-phase review loop, discovery cadence, partial entry, or post-event
Woodcutting behavior.

## Period-qualified primary source

`Evil Tree`, oldid `6569638`, timestamp `2012-11-17T22:22:59Z`:

- <https://runescape.wiki/w/Evil_Tree?oldid=6569638>

The revision pins all seven tier gates and action XP values:

| Tier | Woodcutting | Farming | Firemaking | Nurture XP | Root XP | Tree XP | Fire XP |
|---|---:|---:|---:|---:|---:|---:|---:|
| Normal | 1 | 1 | 1 | 20 | 3 | 15.1 | 200 |
| Oak | 15 | 7 | 15 | 45 | 6.4 | 32.4 | 300 |
| Willow | 30 | 15 | 30 | 66 | 9.1 | 45.7 | 450 |
| Maple | 45 | 22 | 45 | 121.5 | 11.1 | 55.8 | 675 |
| Yew | 60 | 30 | 60 | 172.5 | 12.8 | 64.4 | 1,012.5 |
| Magic | 75 | 37 | 75 | 311 | 14.1 | 70.9 | 1,517.5 |
| Elder | 85 | 42 | 85 | 687.5 | 15.5 | 77.8 | 2,000.5 |

The same revision labels the following as the highest *reported* rewards, not
fixed payouts:

| Tier | Maximum logs | Maximum coins | Maximum blessing |
|---|---:|---:|---:|
| Normal | 12 Logs | 185 | 6 minutes |
| Oak | 24 Oak logs | 326 | 10 minutes |
| Willow | 226 Willow logs | 1,127 | 14 minutes |
| Maple | 131 Maple logs | 1,280 | 18 minutes |
| Yew | 17 Yew logs | 2,334 | 22 minutes |
| Magic | 10 Magic logs | 4,737 | 26 minutes |
| Elder | 375 Teak / 102 Mahogany / 59 Yew / 18 Magic logs | 8,694 | 30 minutes |

Additional period mechanics in the revision:

- the sapling has five nurture stages before the fully grown phase;
- root chops yield kindling, up to eight fires may be lit, and both chopping
  and fire reduce shared health while increasing personal reward contribution;
- the tree starts at 100% health and the player at 0% reward;
- the ordinary reward shape is noted logs, coins, and either a tree seed or
  bird's nest, with clue scrolls and key halves as possible additional rolls;
- the same contribution percentage does not always produce the same logs or
  coins;
- lightning caps a surviving grown tree at 50% after ten minutes, at 25% after
  twenty minutes, and kills it after thirty minutes;
- the blessing applies only to normal, oak, willow, maple, yew, and magic
  trees; reduces solo depletion, increases bird-nest chance, and banks eligible
  logs when the inventory is full; and
- logging out pauses the blessing.

The RuneScape Wiki API exposes no main `Talk:Evil tree` page in the current
history export. Prefix enumeration on `2026-07-19` returned only
`Talk:Evil tree (normal)`, `Talk:Evil tree development`, and
`Talk:Evil tree kindling`. Therefore no period talk revision was available to
pin a reward formula or tier distribution.

## Emulator convergence and conflicts

Darkan:

- `/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/src/main/java/com/rs/game/content/dnds/eviltree/EvilTrees.kt`

Useful structural convergence:

- lines `33-42`: five nurture stages and three grown/dead progress stages;
- lines `78-89`: a two-hour spawn schedule and an unfiltered random choice
  across the seven tiers;
- lines `211-228`: eight fire positions and eight root directions;
- lines `451-497`: 25 nurture progress actions per stage and 250 chops per
  grown stage; and
- lines `404-448`: contribution-proportional rewards and a Woodcutting buff.

The Darkan values are not period-authoritative where they conflict with the
period page:

- lines `50-57` contain several different XP values, including Normal tree
  `15.0` rather than `15.1`, Yew tree `87.5` rather than `64.4`, and Elder
  nurture `730.0` rather than `687.5`;
- lines `417-440` double the period page's reported maximum logs and coins and
  flatten all blessing ceilings to thirty minutes; and
- the implementation's daily `evilTreeChippings` exchange is not the
  contribution model described by the period revision.

AnkiScape therefore uses Darkan only as structural convergence. The period
Wiki table owns gates, XP, ceilings, and tier-based blessing duration.

## Source-blocked values

The following remain `source_blocked` after the period page, available talk
namespace, Darkan implementation, and local 2011Scape tree plugin were checked:

- historical probability distribution across the seven tiers;
- exact personal-contribution increments and reward-share curve;
- exact random distribution below the reported log and coin ceilings;
- exact tree-seed / bird-nest / clue / key roll probabilities;
- the blessing's exact bird-nest multiplier; and
- a complete player-visible active window spanning sapling growth and the
  grown-tree lightning sequence.

These are implementation values, not owner-facing design forks: the owning
contract explicitly permits labeled bounded abstractions that preserve the
settled activity shape.

## Shipped bounded abstractions

The implementation may use the following disclosed values until stronger
period evidence supersedes this note:

- **Tier draw:** uniform across the seven real tiers. This is the owning
  contract's labeled fallback and matches Darkan's unfiltered random choice.
- **Active opportunity:** five answered cards. At the settled conversion of
  roughly twenty cards per two source hours, one card represents about six
  source minutes; five cards preserve the sourced thirty-minute grown-tree
  ceiling while leaving enough room for the three compressed phases.
- **Three review actions:** Nurture awards one exact nurture-table action;
  Prepare awards one exact root-chop action and produces one Evil tree
  kindling; Fell consumes one kindling and awards one exact tree-chop plus one
  exact fire action.
- **Contribution display:** `33%`, `67%`, then `100%` after the three completed
  phases. It is a legibility meter for the compressed finite sequence, not a
  claim about the unrecovered source curve.
- **Coins and logs:** independently uniform from 50% through 100% of the period
  reported ceiling, then multiplied by completed contribution. The ceiling is
  source-pinned; the lower bound and distribution are labeled bounded
  abstractions.
- **Ordinary item slot:** an even tree-seed versus bird's-nest choice. Clue,
  key-half, and Squeal-of-Fortune rolls remain excluded until their exact
  activity table and any dependent system are source-ready.
- **Blessing conversion:** period minutes divided by six and rounded to the
  nearest answered-card opportunity, yielding `1, 2, 2, 3, 4, 4, 5` reviews
  from Normal through Elder.
- **Nest boost:** double the ordinary eligible-tree bird-nest probability.
  This is the smallest bounded multiplier consistent with the source's
  “significantly increased” description.

The abstractions must be named in the UI/tooltips and tests. They must never be
presented as recovered RuneScape formulas.

## Implementation boundary

The source gate is open for the owner-settled slice:

- review-clock spawn and expiry;
- dynamic Utility / Activities D&D surface;
- Nurture, Prepare, and Fell review actions;
- nurture-only participation;
- source-table XP and bounded rewards;
- post-event review-clock blessing;
- one non-chaining ordinary Woodcutting continuation roll;
- doubled nest opportunity while blessed; and
- eligible-log overflow banking while the carried pack is full.

No quest-parity work is included. Location labels are flavor-only and must be
drawn from unrestricted period locations rather than introducing quest-state
or travel simulation.

## Implementation closure

The shipped slice includes:

- a sanitized versioned save state on storage schema `49`;
- one world-clock spawn check per answered card, a five-review active window,
  the two-interaction review-day allowance, and atomic review undo;
- full and nurture-only entry gates with no invented travel or quest state;
- exact tier XP, one carried kindling transaction, bounded rewards, telemetry,
  level checks, and completion feedback;
- a compact Utility card, global review-HUD event/blessing notice, and a
  repeatable offscreen renderer;
- one non-chaining eligible Woodcutting continuation, doubled nest chance, and
  full-pack overflow banking without a fake Bank trip; and
- canonical tight-alpha kindling art with recorded provenance.

The first cross-layer verification pass found and fixed two concrete defects:
the blessing overflow gate had been inserted in the Agility pack helper, and
the world event advanced after the review snapshot so Anki undo could leave a
spawn behind. Focused pure/runtime/integration coverage now exercises both
boundaries. Fable's UI review found the light-theme chip contrast and
card/tree selection desynchronization; both were corrected, together with the
inactive-HUD wording and event/countdown hierarchy. Kimi K3 independently
confirmed those findings and caught the remaining wall-clock-like `today`
label; the final surface says `this review day` and uses neutral inactive
chrome.

Verification:

- `149` final focused pure/runtime/integration methods pass;
- `4` focused real offscreen Qt behavior methods pass;
- the complete non-Qt runner passes `1,853` methods with `239` expected
  environment skips;
- complete real offscreen Qt discovery passes `1,853` methods with one
  intentional skip;
- documentation, test-quality, compilation, diff, sprite normalization,
  registry/reachability, and guarded-worktree audits pass; and
- after a full Anki restart, the canonical add-on opened exactly one native
  AnkiScape dialog. Its dark-mode Utility surface showed the normalized
  kindling art, `Next review`, and `0/2 interactions used this review day`;
  the dialog then closed back to the deck screen without selecting an activity
  or mutating the save; and
- the read-only Workflows run
  `8585cfb9-f3f2-4ff0-afdd-2c6985b9d6e2` timed out both leaves. The root used
  no incomplete leaf result and independently reproduced every accepted
  source and integration claim.

No new owner-design question emerged. The probability/formula rows listed
under `Source-blocked values` remain honest abstractions rather than hidden
parity claims.
