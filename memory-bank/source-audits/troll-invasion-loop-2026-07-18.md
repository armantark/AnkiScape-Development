# Troll Invasion Review-Native Source Pin

Date: `2026-07-18`

Cutoff: RuneScape immediately before EOC, `2012-11-20`.

Status: **period combat, repair, reward, and reset surfaces pinned; review-native
action model owner-closed.**

## Pinned period evidence

`Troll Invasion`, oldid `6588736` (`2012-11-19T21:28:55Z`), establishes:

- the activity is single-player and safe;
- the player chooses either Combat or gatehouse Repair;
- Combat begins with a standard 20-wave version;
- attempting the standard version once unlocks a harder 7-wave version;
- both Combat versions pay the same full reward-book XP on completion;
- partial Combat completion pays proportionally to waves reached;
- the supply table restores combat state up to five times per wave, but may be
  permanently destroyed for the run by a Dynamite troll;
- the Combat route culminates in Cliff and includes source-defined priority
  threats and multi-enemy waves;
- Repair maintains oil drums, ballista ammunition, walls, and barricades;
- Repair grants small Construction, Crafting, and Firemaking XP, while morale
  powers and troll attacks change the pressure state;
- Repair completes after ten source minutes or 1,500 trolls defeated;
- one completion per source month grants a reward book;
- the reward book applies all XP at once to one chosen skill; and
- reward XP is
  `8 × completion_fraction × (L² - 2L + 100)`.

Source:

- <https://runescape.wiki/w/Troll_Invasion?oldid=6588736>

Exact enemy Combat tables, wave-level aggregate outcomes, supply restoration
after its period nerf, ordinary troll drops, Repair failure rates, and monthly
boundary lineage remain implementation-source work.

## Settled platform boundaries

Both source routes ship. The Activity start surface exposes `Combat` and
`Repair`, plus `Standard (20 waves)` or the source-unlocked `Hard (7 waves)`
inside Combat. This is one activity-specific selector, not a Casual/Advanced
split.

The safe-activity rule means defeat loses used consumables but never creates a
grave or drops equipment. Leaving or disconnecting cashes out the source-shaped
partial completion fraction rather than preserving a resumable session.
Viewing another page does not leave; switching review targets or explicitly
leaving uses the shared confirmation and partial cash-out.

The reward book enters the shared chosen-skill reward surface because its
skill list is too large for the contextual action strip. Monthly eligibility
uses a fixed 30-day answered-card month—7,200 reviews—as the labeled no-wall-
clock normalization unless a project-wide simulated calendar later supplies a
different month boundary. Runs remain playable after the monthly book has been
claimed for their ordinary Combat or Repair XP, exactly as the source allowed.

## Settled review-native action model

### Combat

A source wave is a progress boundary, not an Anki action unit. One successful
review advances the selected Combat route by the live kernel's ordinary
`6 × M` immediate game ticks. It is therefore invalid to clear a whole wave
merely because one card was answered.

Each source wave is represented by one visible aggregate **wave front** with
persistent LP and pressure state derived from that wave's period roster. The
ordinary Combat engine attacks that front for six ticks at multiplier 1. It
does not instantiate or tick every troll behind the result line. Clearing the
front advances exactly one of the source's twenty Standard or seven Hard wave
markers. A kill, defeat, flee, destroyed-supply boundary, or completed wave ends
the review without spending unused ticks on the next wave.

This keeps the activity inside the cadence kernel rather than creating an
activity-specific combat burst. It also preserves the source's exact
wave-based partial-reward fraction, Standard-to-Hard unlock, supply-table
failure, priority-threat texture, and Cliff finale without depending on the
parked general multi-enemy model. The supply table follows the active Combat
automation preset at safe boundaries. A sourced Dynamite consequence may
destroy it for the rest of the run, and the result line must say so.

Implementation still has to source and pin the aggregate-front construction
from each exact wave roster. The abstraction is the aggregation itself, not
permission to invent unsupported enemy totals, XP, or damage.

### Repair

One successful review performs one complete maintenance action. This is a
cadence `passthrough` action, not Combat ticks and not a hidden ten-minute
simulation. At multiplier `M`, the review performs up to `M` complete
maintenance actions and stops at the activity boundary.

The player does not babysit four repair buttons. The route automatically picks
the most urgent valid job among oil drums, ballista ammunition, walls, and
barricades: first prevent an imminent gatehouse failure, then repair the
lowest-condition component. Its one-line result names the job, the authentic
Construction, Crafting, or Firemaking XP, the ten-troll credit, and any morale
power or troll-pressure consequence.

The complete runtime state is four bounded component conditions, morale,
trolls defeated, and eligible repair reviews spent. It never simulates
individual defenders or trolls. One aggregate, source-shaped pressure
consequence resolves after each maintenance action. Morale powers use a
deterministic automatic priority: prevent failure first, otherwise spend only
when capped or when the power improves the current action. The UI may explain
the selected power in the result line, but exposes no per-review morale
controls.

The source endpoints map without wall time:

- reaching 1,500 defeated trolls completes the route, normally after 150
  productive maintenance actions because each contributes ten; or
- the ten-minute endpoint becomes a ceiling of 167 eligible successful reviews
  at the canonical 1,000-reviews-per-balancing-hour cadence.

Interrupted or non-productive maintenance can therefore make the 167-review
ceiling relevant. Leaving earlier cashes out the same source-shaped completion
fraction used by the activity's reward contract.
