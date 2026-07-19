# Activity cadence reconciliation

Date: `2026-07-18`

Status: **recent activity-design portfolio audited against the live cadence
kernel; two concrete Combat conflicts corrected; grouped activity units
classified.**

Authority:

- `memory-bank/cadence-kernel-contract-2026-07-13.md`
- `memory-bank/codex-briefs/design-2-to-cadence-canonical-handoff-2026-07-17.md`
- the focused July 17–18 source audits named below.

## Answer to the owner concern

The recent activity designs did not universally ignore cadence. The live
contract deliberately lets Utility/Activities own finite action groups and
world-clock sessions. That is what makes a whole Circus performance, Pyramid
Plunder room, or Skullball route a legal review unit without pretending that
each contained animation is an ordinary repeatable skilling action.

The review was nevertheless too implicit. Several focused audits said “one
review” without naming their cadence class, and two compressed actual Combat
work while also granting Combat XP or combat-shaped loot. Those two cases were
real conflicts:

1. Phoenix Lair grouped five guardian fights, their Combat XP, and their loot
   into one traversal review.
2. Fist of Guthix described complete tactical exchanges without attaching
   them to the six-tick Combat reducer, even though the source grants
   damage-based Combat XP.

Both are corrected by persistent aggregate encounters that advance through the
ordinary `6 × M` Combat slice. This does not reopen the owner's spatial and
control simplifications.

## Canonical activity cadence classes

Every implemented activity route must declare one of these through the
existing Utility/Activities exemption metadata or the ordinary live handler:

| Class | Review behavior at multiplier 1 | Multiplier and terminal rule |
|---|---|---|
| `world_clock` | Every answered card advances only the established 240-card day and its derived event timers. | Never multiplied a second time. |
| `combat_ticks` | One successful review advances six immediate Combat ticks with persistent encounter state. | Advance `6 × M` ticks, stopping at kill, death, flee, wave, round, or other activity boundary. |
| `source_action` | One successful review performs one real source action or attempt. | Perform up to `M` complete actions, stopping at the activity boundary. |
| `activity_group` | One successful review resolves one explicitly bounded, finite activity beat whose contents and reward are declared. | Resolve up to `M` beats, but never start a second locked performance, run, encounter, or reward cycle after a terminal boundary. |
| `direct_command` | An atomic UI transaction with no foreground action or XP. | Never multiplied and consumes no review. |
| `source_blocked_activity` | Retain the approved finite grouping while its missing rate or hidden roll remains visibly unresolved. | Same terminal rules as its owning grouped activity; never pretend the unresolved number is sourced. |

An Activity exemption is not permission to bypass cadence silently. Its row
must name the action unit, any grouped source operations, direct XP and reward
contents, `Again` behavior, multiplier behavior, terminal boundary, and undo
boundary.

## Portfolio result

| Activity | Classification | Verdict |
|---|---|---|
| Tears of Guthix | `source_blocked_activity` | The automatic collection beat survives. Exact beat count and reward magnitude remain blocked; no legacy review count may be treated as parity. |
| Circus | `activity_group` | Whole 6- or 10-trick performance remains a deliberate weekly grouping. It pays the exact bounded routine once and cannot be interpreted as ten repeatable skilling steps. |
| Fish Flingers | `source_action` inside a finite activity | One review is one catch opportunity. The six-catch event length is a labeled pacing abstraction; completion rewards must be calibrated to that finite score model rather than to source minutes. |
| Flash Powder Factory | `activity_group` | One A+B+catalyst+mix production circuit is the declared beat. The eight/nine-slot session remains an activity abstraction and may not replay hidden subactions or claim source minutes. |
| Gnome Ball | `source_blocked_activity` | The three match beats remain, but their grouped goal XP and any throw XP are one declared fixed activity result. Missing tackle, score, and throw rolls remain blocked. |
| Pyramid Plunder | `activity_group` | One room is the bounded beat. Its selected-priority object bundle and XP resolve once; there is no hidden urn loop and no second Thieving cadence gate. |
| Werewolf Skullball | `activity_group` | The ten-goal route remains one atomic finite run with one sourced completion reward. It is not an ordinary Agility-course passthrough row. |
| Evil Tree | `activity_group` plus `world_clock` | Discovery and the blessing use the world clock. Nurture, prepare, and fell are explicit finite phase groups; their exact aggregate XP must come from the activity tables and never masquerade as ordinary repeatable skill actions. |
| The Pit | `source_blocked_activity` | One bounded challenge step remains the approved unit. The six-step budget is still a labeled abstraction pending source-time reconciliation. |
| Sorceress's Garden | `source_action` | One review is one complete garden attempt and harvest. `Again` owns the caught outcome. No additional success or cadence gate is allowed. |
| Penguin Hide and Seek | `source_action` plus `world_clock` | One review spies one listed penguin. Weekly roster creation uses the world calendar; chosen-skill redemption is a direct reward command. |
| Managing Miscellania | `world_clock`, `source_action`, and `direct_command` | Salary/approval/credit use the day clock; one review performs one real approval chore; allocation, funding, and collection remain direct commands. |
| Shattered Heart | host-action attachment | Strange-rock eligibility rolls only when the already-admitted owning skill action occurs. It never receives a second cadence opportunity. |
| Gnome Restaurant | `source_action` and `world_clock` | Cooking inputs use ordinary Cooking cadence. Delivery is one no-skill-XP activity action; `Again` affects the bounded punctuality state while the world clock advances. |
| Barrows | `activity_group` plus `combat_ticks` | Room transitions are bounded graph beats; any active brother or tunnel encounter advances only through six-tick Combat slices. |
| Skeletal Horror | `combat_ticks` plus `world_clock` | Four boss phases persist through six-tick reviews; weekly eligibility uses 1,680 answered cards. |
| Troll Invasion | `combat_ticks` or `source_action` | Combat advances six ticks against the persistent wave front. Repair performs one maintenance action per kernel step. |
| Phoenix Lair | `combat_ticks` plus `activity_group` | Corrected below: one aggregate guardian front and the Phoenix both use live Combat. Pyre preparation remains one finite no-early-reward grouping. |
| Fist of Guthix | `combat_ticks` plus `world_clock` | Corrected below: every active round advances six Combat ticks. Stance changes charge and exposure inside those ticks; it does not replace Combat cadence. |
| Vinesweeper | `source_blocked_activity` | One successful review resolves one bounded source-shaped operation. No grid, field, farmer, rabbit, or timer state exists; exact outcome weights remain blocked pending the implementation source pass. |
| Big Chinchompa | `activity_group` plus `world_clock` | One activity kernel step resolves one complete fifteen-moth catch-and-feed jar circuit. Multiplier stops at event expiry or communal fullness; crowd pressure advances once per review boundary, never once per moth. |
| Livid Farm | `activity_group` plus exact `rate_limited` residual | One kernel emission resolves one complete five-round source cycle. The pinned twelve-cycle/hour rate becomes exactly six cycles per five successful reviews; the UI reports whether a review emitted one or two cycles. |

## Implementation gate

Before any focused activity ships:

1. add its declared action unit to cadence coverage;
2. prove `Again`, multiplier, terminal, and undo behavior;
3. ensure a grouped activity reward is paid once rather than per hidden
   subaction;
4. route every real Combat encounter through `combat_ticks`; and
5. leave source-blocked rates and rolls visibly blocked instead of deriving
   them from a convenient review count.

This audit preserves the owner-approved simplifications. Only the two real
Combat conflicts require changed session progression.
