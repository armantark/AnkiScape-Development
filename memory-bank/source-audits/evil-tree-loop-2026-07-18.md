# Evil Tree Review-Native Source Pin

Date: `2026-07-18`

Cutoff: RuneScape immediately before EOC, `2012-11-20`.

Status: **period source pinned; phase-compression model under owner grill.**

## Pinned period evidence

`Evil Tree`, oldid `6569638` (`2012-11-17T22:22:59Z`), establishes:

- the activity may be completed twice per source day;
- merely inspecting a tree does not consume an interaction, but nurturing or
  otherwise interacting with it does;
- the tree has five sapling growth stages followed by the fully grown tree;
- nurturing advances sapling growth and awards Farming XP;
- the grown-tree loop consists of chopping roots for Woodcutting XP and
  kindling, lighting up to eight sections for Firemaking XP and tree damage,
  and chopping the tree itself for Woodcutting XP and tree damage;
- contribution raises the player's reward percentage, while the shared tree
  health is reduced by chopping and fire;
- the fallen tree pays noted logs, coins, and item-table rolls, with reward
  magnitude affected by contribution;
- finishing grants a temporary ordinary-tree Woodcutting benefit whose maximum
  source duration varies from 6 to 30 minutes by tree tier; and
- the event has seven tree tiers with distinct Farming, Woodcutting, and
  Firemaking requirements and XP tables.

Source:

- <https://runescape.wiki/w/Evil_Tree?oldid=6569638>

The exact reward-distribution formula, participation curve, post-event bonus
conversion to AnkiScape review opportunities, recurring eligibility, and event
availability model remain implementation-source work. They must not use the
wall clock or simulate worlds, clans, scouts, or individual other players.

## First owner fork: phase compression

The source contains six growth stages, four recurring root positions, eight
fire positions, shared health, and a contribution percentage. Reproducing
those objects literally would add state without adding a meaningful review
decision.

The recommended AnkiScape boundary is one explicit finite activity session with
three consequential phases:

1. **Nurture** — compress the five sapling stages into one Farming review beat;
2. **Prepare** — chop roots to obtain and spend kindling, preserving the
   Woodcutting-to-Firemaking dependency; and
3. **Fell** — combined chopping and burning progress defeats the grown tree and
   determines the player's reward share.

The HUD exposes the current phase and one bounded progress meter; each answered
review performs one source-shaped phase action and emits one result line. No
hidden tree population, root-position, fire-position, or multiplayer
simulation runs behind that line.

The owner must decide whether to preserve this three-phase skill chain or
flatten the entire event into one generic `Tend Evil Tree` progress action.
