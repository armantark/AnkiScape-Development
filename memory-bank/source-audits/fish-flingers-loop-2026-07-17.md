# Fish Flingers Review Loop

Date: `2026-07-17`

Cutoff: RuneScape immediately before EOC, `2012-11-20`.

## Pinned period evidence

`Fish Flingers` oldid `6529096` (`2012-11-03`) establishes a recurring
multiplayer D&D with no level, quest, or item requirement; temporary bait,
hook, and weight controls; six species across four locations; rating feedback
used to deduce optimal tackle; communal depletion; cooperative big fish;
Fishing-level-scaled XP; two daily tickets capped at ten held; medals, tokens,
and a reward shop:

<https://runescape.wiki/w/Fish_Flingers?oldid=6529096>

The earlier provenance summary is
`memory-bank/source-audits/gap-grill-13-fishing-provenance-2026-07-10.md`.

## Entry gate

One stored entry ticket is consumed atomically when an event begins. There is
no level, quest, or item gate. The source's two-per-day ticket grant and
ten-ticket storage cap must use AnkiScape's answered-card calendar rather than
the wall clock; extra tickets retain only their source acquisition routes.
Undoing event entry restores the ticket. This gate is also indexed in
`activity-entry-gate-ledger-2026-07-18.md`.

## Settled AnkiScape abstraction

The source's tackle deduction survives as a visible automatic efficiency ramp,
not as controls the player must babysit:

- neither Casual nor Advanced exposes bait, hook, or weight selection;
- the first three successful reviews all produce catches;
- those reviews successively discover bait, hook, and weight, visibly raising
  catch efficiency until the third review reaches full efficiency;
- one event lasts six successful reviews, leaving three catches at full
  efficiency after the discovery ramp;
- the sixth review atomically closes the event and awards XP, medals, and
  tokens;
- the exact intermediate efficiency percentages are labeled AnkiScape balance
  values rather than source claims;
- stock depletion automatically rotates species or location;
- a fixed communal depletion pressure replaces simulated competitors; and
- any cooperative big-fish opportunity is captured automatically inside the
  triggering review using the public-event baseline.

Persist only the bounded state that affects a later result: event progress,
discovery step, current stock/rotation, score, and earned reward counters. Do
not persist competitors, tackle candidates, search history, or background
workers. All changes are answered-card-driven and undoable.

The six-review length is an AnkiScape pacing abstraction, not a conversion of
the source duration into wall-clock or answered-card minutes. It provides one
compact sweep matching the source's six-species structure.

## Horizontal implementation harvest (`2026-07-21`)

The literal archived wikitext from oldid `6529096` pins the following reward
mechanics used by the first mechanic-complete slice:

- tokens are `floor(fish caught / 4)`, plus one per big fish (maximum three),
  one per two assists (maximum three), and one per two perfect tackles (maximum
  three), with a 2,000-token cap;
- Junior Angler, Master Angler, Whopper, and Team Player medals require three
  perfect tackles, six perfect tackles, three big fish, and six assists;
- each fishing-outfit piece costs 140 tokens and gives 1% extra Fishing XP,
  while the complete set gives a further 1%; and
- the five cumulative-medal tackle-box upgrades cost respectively
  `110/20`, `230/50`, `470/110`, `900/230`, and `1860/500` tokens/medals.

OpenRS2 cache revision `742` (`2012-11-07`) pins item definitions `15666` to
`15670` for the five tackle boxes and wearable definitions `24427` to `24430`
for the fishing outfit. The item definitions and pre-cutoff RuneScape Wiki
images are recorded by `tools/fetch_fish_flingers_assets.py` and
`assets_provenance.json`.

The automatic tackle ramp counts only catches made at full efficiency as
perfect-tackle credits. Because the settled six-review compression discovers
the final component on catch three, one event can earn four such credits; it
does not fabricate a six-perfect Master Angler medal during the two partial
efficiency catches.

The implemented event XP curve remains a disclosed balance translation:
oldid `6529096` says XP scales with score and Fishing level and approaches
20,000 at high level, but explicitly marks its displayed XP table obsolete
after the `2012-07-24` update. Recovering the exact post-update equation, raw
fish exchange rewards, and the original hidden catch/weight distributions is
remaining data-depth work, not a missing mechanic.

Implementation ownership:

- `fish_flingers_data.py` pins the activity, reward shop, equipment, and item
  identities;
- `fish_flingers_logic.py` owns ticket accrual, event progress, terminal
  rewards, outfit XP, leave semantics, and the shop;
- `runtime_actions.py`, `storage_pure.py`, and `__init__.py` connect answered
  reviews, persistence, atomic activity ownership, and direct-action undo; and
- `ui.py` exposes the paginated Activities detail card and compact manual
  reward shop without a nested scroll surface.

## UI and native-runtime closure (`2026-07-21`)

An Opus read-only taste pass found five bounded presentation defects, all
reproduced in the real card: the disabled Buy button hid its unmet gate, the
currency string displaced the usual activity state, the reward frame competed
with the primary action, the progress wording appeared off by one, and the
fresh-state copy implied a ticket-claim action that does not exist. The compact
card now exposes READY/ACTIVE state, keeps the shop frame neutral, preserves the
full reward label and the first unmet purchase requirement in tooltips, labels
progress as landed catches, and uses plain player-facing idle copy with event
history only after something has happened.

A fully restarted native Anki instance showed one AnkiScape menu, the separate
Utilities and Activities categories, Fish Flingers on the paginated
Distractions and Diversions page, and the updated dark-mode detail card. The
disabled purchase control exposed `Requires 140 Fishing tokens` through the
native accessibility tree. The check did not enter an event or mutate the real
player save.

## Bounded stock-mechanic closure (`2026-07-25`)

The six sourced species and four sourced locations are now a live deterministic
six-entry route with the sourced one/one/two/two location distribution. Session
state version 2 persists only bounded current route, species, location, stock,
and existing score/reward inputs. Old and malformed sessions repair into that
shape.

The stock maximum, species/location catch modifiers, stock bands, rotation
order, and fixed three-stock communal depletion are explicitly AnkiScape balance
values, not historical rate claims. Every review uses the current species,
location, and stock in its catch result, then removes both the player catch and
fixed communal pressure from stock so that pressure changes later stock-band
catches. Exhaustion rotates immediately without a worker. The pure view and
dark-mode-safe Qt card show species, location, stock amount/percent/label, route
index, and communal pressure. The
six-review tackle ramp, entry/leave behavior, terminal formulas,
shop, XP, runtime dispatch, and undo seam remain unchanged.

### Correction (`2026-07-25`)

An earlier version of the section above also described per-species and
per-location **weight modifiers**, a `total_weight` accumulated across a session,
and a total shown on the card. Those were removed the same day, and the
description with them.

Two reasons. Nothing read the value: it was computed, persisted, clamped and
printed, and no gate, reward, medal, XP formula or rotation consumed it, which is
the same inert-state defect the stock-rotation work existed to fix. And the name
collided with a sourced term meaning something else — "weight" in this audit is
one of the three tackle controls, bait, hook and weight, which the six-review
ramp already discovers. A future reader would have read the invented fish weight
as the sourced tackle weight.

The description was also added to this audit in the same change that added the
code, so it documented an invention rather than settling a design. When an
implementation and its audit are written together, the audit stops being evidence.

### Event length raised to eight reviews (`2026-07-25`)

The six-review length made the sourced medal table unreachable. Perfect tackles
are the reviews after the discovery ramp, so a six-review event yielded exactly
four of them every time: Junior Angler fired unconditionally, Master Angler's
six-tackle threshold never fired at all, and Team Player's six assists were
nearly unreachable.

The medal thresholds come from oldid `6529096`. The event length does not — this
audit already recorded it as "an AnkiScape pacing abstraction". The abstraction
therefore moved to fit the source rather than the other way round. At eight
reviews a flawless event produces exactly six perfect tackles, so every sourced
medal is reachable and no sourced value changed.

The discovery ramp is untouched: bait, hook and weight still land on the first
three reviews, and the two extra reviews run at full efficiency. Rewards scale
with fish caught, so the longer event pays proportionally more.
