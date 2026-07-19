# Reviewer Context Actions Contract

Date: `2026-07-18`

Status: **owner-settled first slice; implementation deferred; later candidate
harvest explicitly open.**

## Product boundary

AnkiScape may surface rare, gameplay-created decisions immediately above the
review XP/LP HUD. This is a contextual action surface, not a second menu and not
a reason to add permanent settings.

It extends, but does not replace, the existing
`review-hud-world-alerts-contract-2026-07-16.md`:

- `ReviewWorldAlertStrip` owns urgent or expiring state icons such as the
  Gravestone, dropped familiar cargo, and pet capability transitions.
- `ReviewContextActionStrip` owns one compact labeled decision with clickable
  actions.
- both are interactive siblings of the mouse-transparent `ReviewHUD` and are
  positioned by the same reviewer-overlay layout coordinator already required
  by the world-alert contract.

The action strip remains independent of Casual or Advanced mode unless a future
interaction has genuinely different behavior. It does not force a mode split.

## Qualification rule

A contextual action belongs in this strip only when all of these are true:

1. gameplay has just created or exposed a real persisted decision or immediate
   recovery action;
2. it resolves atomically through one of at most three concise options;
3. it is rare relative to ordinary review cadence rather than a per-review
   configuration choice;
4. the owning system can declare a conservative default or explicitly declare
   that ignoring means no action; and
5. direct and ignored resolution can both participate correctly in save and
   undo semantics.

Ordinary target configuration, shops, reward catalogs, inventory management,
quest branches, destructive actions, high-value confirmations, free-form input,
and choices with more than three useful options stay on their canonical pages.
The strip may offer one `Open …` action for a complex pending event, but it must
not reproduce that page as a miniature menu.

## Presentation and queueing

- Show at most one labeled context row at a time.
- Show no more than three action chips.
- Additional pending contexts remain queued behind one compact count/icon; they
  do not create stacked toolbars or modal dialogs.
- The strip itself is the notification. Do not also emit a duplicate toast or
  popup for the same decision.
- An ignored action does not block answering cards.
- When no contextual action exists, the row disappears and reserves no space.
- Existing world-alert icons remain distinct from decision chips. A status does
  not acquire buttons merely because it shares the overlay cluster.

## Ignored and remembered-choice semantics

“Ignored” means the player answers the **next card** after the context row was
first presented without clicking one of its actions. No wall-clock duration is
consulted.

Each context family declares:

- a stable family ID;
- its currently valid options;
- an authored conservative default;
- whether a prior explicit selection is safe to remember; and
- the pure/direct action used to resolve it.

On that next answered card:

1. use the last **explicitly clicked** option for that family when the family is
   rememberable and the option is still valid;
2. otherwise use the authored conservative default; and
3. resolve it inside the same atomic review transaction.

Review undo therefore reverses the ignored resolution and restores the pending
context. An automatic resolution never overwrites the remembered preference;
only a later explicit click does. Closing Anki or leaving the reviewer does not
resolve the context because no card was answered.

If a family cannot safely default, ignoring is a no-op and the event collapses
to its status icon or remains on its owning page. The generic framework must
never guess a default.

## First implementation slice: The Pit

Completing a successful Pit challenge creates a persisted reward context:

**Pit reward — `Take XP` / `Gamble`**

- The first conservative default is `Take XP`.
- An explicit `Take XP` or `Gamble` click becomes that family's remembered
  option.
- If the next card is answered without a click, use the remembered valid option
  or `Take XP` when none exists.
- A click remains a separately undoable direct command. An ignored choice is
  part of the next review's undo snapshot, including RNG state when the
  remembered choice is `Gamble`.
- The context strip becomes the canonical player-facing reward surface. The
  always-present Agility-panel `Claim Pit XP` and `Gamble Pit XP` command buttons
  must not remain as duplicate clutter once the strip is live.

This first slice does not add an **Automatically gamble Pit XP** checkbox.

## Second settled family: Aksel bronze orders (2026-07-18)

While Artisan's Workshop is the active target, Aksel's random bronze
ceremonial-sword orders (oldid `6547352`: 2–4 offers per source hour, less
frequent during a stay, cut diamond at 90%+ performance) surface as:

**Bronze order — `Accept bronze order` / `Ignore`**

- The conservative default is expiry: ignoring means no action and the offer
  disappears. There is no stored order backlog — the source offer is transient,
  and its decaying frequency exists so orders cannot be banked.
- The family is rememberable. An explicit `Accept` or `Ignore` click resolves
  later ignored offers, so habitual accepters get auto-accept without a
  settings checkbox.
- Accepting replaces the next successful Workshop action with the bronze-sword
  attempt inside the ordinary review transaction; XP, Respect, performance, and
  the diamond award ride the same undo snapshot.
- Owning decision record:
  `gap-grill-decisions-2026-07-10.md#smithing-artisans-workshop-burial-armour-and-ceremonial-swords`.

## Candidate harvest for later passes

These existing or designed families should be evaluated against the
qualification rule, not automatically included:

- Familiarisation's ingredient-box versus triple-charms reward;
- a pending Talent Scout offer when automatic acceptance is disabled;
- a full urn ready for direct teleport;
- manual familiar renewal or recovery when the relevant automation is disabled;
- future Slayer task/challenge offers; and
- other rare two- or three-option Activity rewards.

The existing world-alert contract already owns Gravestone details, familiar
cargo reclaim, and pet capability-transition warnings. Complex chosen-skill
rewards such as lamps or Penguin-point redemption should open their shared
reward-choice surface rather than rendering every skill in the reviewer.

## Implementation and verification handoff

Backend:

- add a pure, registry-driven context-row projection rather than inferring
  feature state in Qt;
- persist remembered explicit choices by stable family ID;
- validate remembered options against the live option set; and
- keep direct-command and next-review automatic resolution atomic and
  undo-safe.

Frontend:

- add one interactive sibling action strip to the shared reviewer-overlay
  cluster;
- coordinate it with ReviewHUD, Farming, ReviewWorldAlertStrip, and ExpPopup;
  and
- remove duplicate always-visible Pit reward commands when the new surface is
  canonical.

Verification:

- pure tests for qualification data, safe-default fallback, valid/invalid
  remembered choices, and no-op families;
- integration tests for click resolution, next-answer resolution, save/reload,
  RNG restoration, review undo, and direct-command undo;
- offscreen Qt tests for one-row/three-action limits, queue collapse, hidden
  empty state, HUD-disabled positioning, keyboard access, and dark-mode text;
  and
- manual Anki QA covering explicit Take, explicit Gamble, remembered ignored
  resolution, and undo of each path.

## First-slice implementation status — 2026-07-19

The generic projection, storage, shared reviewer strip, and complete Pit reward
family are live. The strip is an interactive sibling above the review HUD,
collapses later decisions behind a queue badge, hides when empty, and remains
available when the main HUD is disabled. `Take XP` is the visually safe option;
the automatic option is separately cued; Gamble's equal odds are disclosed in
its tooltip and accessible text names each action.

Explicit clicks are direct-command undo entries with RNG restoration. Ignoring
the row resolves it inside the next answered card's ordinary snapshot,
including Again, and review undo restores the pending context. Only explicit
clicks update the family preference. The permanent Agility-panel claim and
gamble buttons have been removed.

Aksel bronze orders remain the next contract-owned family; this closure does
not claim that Smithing slice.
