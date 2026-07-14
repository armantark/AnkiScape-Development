# Role

You are implementing the **Thieving** skill in AnkiScape, an Anki add-on that
turns flashcard reviews into RuneScape pre-EOC skilling actions.

Repo: `/Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork`
Branch: create `codex/thieving-skill` off `main`. Do not work on `main`.

# Goal

Thieving ships as a playable skill: pickpocketing, stalls, wall safes, and
blackjacking, with every number sourced and the stall line paced by the cadence
kernel rather than by one-action-per-review.

# The contract is already written — read it first, and do not relitigate it

`memory-bank/thieving-skill-contract-2026-07-13.md` is the output of three rounds
of owner grilling. Every design question is settled there: which emulator wins,
the roll shape, why the stall catch chance is zero, why the wall safe is the one
exception, why the level inversion ships as-is, and which content rows park.

Read it before you open anything else. If you find yourself about to invent a
balance constant, re-read it — the answer is in there, and the answer is usually
"the source already tells you, and it is not a free parameter."

# Success criteria

Thieving is done when all of the following hold:

1. The skill is registered in `skill_registry.py` and behaves like the other
   twelve — target selection, XP, levels, the skill hub, the main menu.
2. **Pickpocketing** ships 2011Scape's table wholesale, with the interpolation
   roll (`chance = (minChance + (maxChance-minChance)*(level-1)/98) / 255`), the
   multi-pickpocket rule, and stun/damage on failure. Note that
   `agilityLevelOvershoot` is Agility minus the *Thieving target's* level, and
   Agility is still a stub capped at 66 by quest XP, so multi-pickpocket will
   fire rarely at the top end and never for the Hero. That is expected and
   accepted — see the contract. **Ship the sourced thresholds unchanged**; do not
   compensate for the missing Agility skill by tuning them.
3. **Stalls** are paced by the cadence kernel. Each stall's profile is exactly:
   ```python
   rate_limited_profile_pure(f"thieving:{stall_id}", 6000, respawn_ticks)
   ```
   because a tick is 0.6s, so `actions_per_hour = 6000 / respawnTicks` is an
   exact rational. The vegetable, baker, and wall-safe stalls exceed `R = 1000`
   and must declare `overflow_policy=CAP_ONE_ACTION` — the kernel raises if they
   don't (`cadence_kernel.py:169`). **The stall catch chance is zero.** There is
   no roll to write.
4. **The wall safe** ships 2011Scape's `lowChance = 8, highChance = 160`
   endpoints — the only stall-family row that can fail, and the only one whose
   unconditional success would overshoot its sourced XP/hour.
5. **A failed attempt costs the review**, applies the sourced damage to the
   shared combat lifepoint pool, and stuns, so the next review only clears the
   stun. A Thieving food loadout rides the existing `combat_supply_loadout`
   substrate. One casual toggle — "Fight back when caught", default off —
   governs both stall guards and blackjack thugs.
6. The stall XP/hour comes out within rounding of the pinned period rates in
   `tools/sourced_xp_rates.py:90-96`. **This is the acceptance test for the whole
   stall line.** Write it as a real test, not a spot check: the gem, spice, and
   silver stalls should land on 3,240 / 3,600 / 6,480 xp per balancing-hour.
7. Full suite green. Baseline on `main` right now is **1,219 tests, 187 skips, 3
   expected failures** (`python3 -m unittest discover -s tests -q`). Anything else
   is a regression you caused.
8. Every shipped number carries a `file:line` citation into 2011Scape or a pinned
   wiki `oldid`, recorded in
   `memory-bank/source-audits/thieving-tables-2026-07-13.md`, which you also
   write. A value without a citation is not done.

# Sources, and which one wins

- **2011Scape** = `~/Downloads/game-main`, Thieving at
  `game/plugins/src/main/kotlin/gg/rsmod/plugins/content/skills/thieving/`.
  **Trusted. Ships.**
- **Darkan** = `~/Documents/2012scape with bots/darkan-world-server`.
  **Established inventor.** Record as a divergence column, never as the shipped
  value — not even where 2011Scape is silent.

**Do not take a number from the prose dossier**
(`memory-bank/source-audits/thieving-source-dossier-2026-07-13.md`). Open the
implementation file. The dossier records source *shorthand*, and misreading it as
probabilities is the specific mistake this contract exists to prevent — see the
notation section of the contract before you record a single chance value.

# Constraints

- **NEVER invent a value.** No source states it → mark `source_blocked` and park
  the row. Absence of evidence is a finding; recording it correctly is worth more
  than filling the cell.
- **Preserve source base XP exactly.** Any rate correction rides the cadence
  profile, never the XP number.
- The cadence kernel is integer/rational (`Fraction`) throughout and **no float
  is ever persisted**. A refractory period is a deterministic residual schedule,
  not a coin flip. Match that.
- Storage changes are **additive** and versioned (`storage_pure.py`,
  `CURRENT_CONFIG_VERSION`). An existing save must still load.
- Do not touch the cadence kernel's Phase 1 semantics, the shadow observer, or
  any other skill's balance. Thieving is the only behavior that changes.
- **Do not edit the tests to make them pass.** `tools/sourced_xp_rates.py` is a
  measuring instrument — it is evidence, not a knob. If a stall misses its
  sourced rate, the bug is in your cadence wiring.

# Autonomy

Make the in-scope changes and run validation without asking. Commit as you go —
this is a solo project and the owner wants frequent checkpoints on the branch.
Do not push, do not open a PR, do not merge to `main`.

# Output

A short preamble, then work. Update only at phase changes; do not narrate routine
reads. Final report: what shipped, what parked as `source_blocked`, the stall
XP/hour table you actually measured against the sourced one, and the suite count.

# Stop rules

- No source states a value → `source_blocked`, park the row, continue. Do not ask.
- 2011Scape and Darkan conflict → 2011Scape ships, Darkan noted. Do not ask.
- Only Darkan has the row → `source_blocked` + lead. Do not ask.
- A stall misses its sourced XP/hour → fix your cadence wiring, not the test.
- Something genuinely contradicts the contract → **stop and report.** Do not
  guess, and do not quietly pick a side. The contract cost three rounds of
  grilling; a real contradiction in it is worth surfacing, not routing around.
