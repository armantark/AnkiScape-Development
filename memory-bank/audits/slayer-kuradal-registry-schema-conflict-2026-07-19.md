# Slayer Kuradal registry-schema conflict — 2026-07-19

Status: **implementation stopped on settled-contract/code conflict**.

## Conflict

The settled Kuradal contract cannot be represented faithfully by the current
Slayer registry schema:

1. `SlayerFamily` owns one global quest gate and one global
   `readiness_features` tuple. Kuradal's Aquanite 50-point assignment unlock
   and Ice-strykewyrm Tale-of-the-Muspah plus cape-or-2,000-point alternative
   are master-specific row gates, not global family gates.
2. The shared `dark_beasts` family currently requires
   `temple_of_light_context`, while the Kuradal contract explicitly uses a
   Kuradal's-Dungeon variant that must not import the unrelated
   Temple-of-Light route.
3. `SlayerMaster` can express only one quest ID alongside Combat and Slayer
   levels. Kuradal's Ancient Cavern access is owned by the Barbarian Training
   activity, which does not exist as a quest flag and must not be fabricated as
   one.
4. Readiness currently accepts feature satisfaction across any family
   candidate. It cannot prove that one certifying target simultaneously
   satisfies a master-specific context and every distinctive family mechanic.

Encoding the 36 rows now would therefore create a supposedly complete hidden
registry whose eligibility and future readiness metadata are already known to
contradict the owner-settled contract.

## Evidence

- Governing pool and gate contract:
  `source-audits/slayer-kuradal-pool-2026-07-17.md`.
- Closed TzHaar and Living-rock membership:
  `source-audits/slayer-kuradal-family-boundaries-2026-07-19.md`.
- Current schema:
  `slayer_data.py` (`SlayerFamily`, `SlayerMasterFamilyRow`, and
  `SlayerMaster`).
- Current readiness composition:
  `slayer_readiness.py:slayer_family_readiness_blockers_pure`.
- Barbarian Training ownership:
  `gap-grill-decisions-2026-07-10.md` under
  `fm-barbarian-bow-lighting`.

## Required repair boundary

This is not an open creative-design question. A later implementation slice
must add a contract-preserving representation for:

- master-specific family-row eligibility;
- non-quest activity access on master rows;
- context-specific qualifying variants; and
- readiness that certifies one valid end-to-end route rather than composing
  unrelated feature fragments.

Only after that representation is implemented may Kuradal's 36-row,
322-point hidden pool be registered. No Kuradal data, runtime master, or
readiness assertion was added in this stopped slice.
