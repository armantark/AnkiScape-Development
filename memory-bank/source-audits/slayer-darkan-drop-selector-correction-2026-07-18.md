# Darkan ordinary-drop selector correction

Date: 2026-07-18

Status: **confirmed implementation defect corrected across eleven live Slayer
targets; no owner design input required.**

## Executable source semantics

Darkan's
`src/main/java/com/rs/utils/drop/DropList.java:43-68`
sorts the supplied `DropTable` rows, assigns every nonzero rate an adjacent
interval in one cumulative range, and appends the remaining no-drop interval.
`DropList.java:98-147` then draws one random value and returns only rows whose
interval contains that value. Rate-zero rows are marked always and are emitted
without consuming that selector.

Darkan's
`src/main/java/com/rs/game/model/entity/npc/NPC.java:643-653`
invokes the NPC drop set once and then invokes its legacy charm table
separately. A charm selector is therefore independent of the one ordinary
selector, but sibling nonzero rows inside a single NPC drop JSON are not
independent rolls.

## Corrected targets

- **Jungle horror:** one guaranteed Bones row plus one exact 100,000-slot
  ordinary selector. The 32 nonzero JSON rows occupy 99,858 slots and the
  remaining 142 are empty.
- **Shadow warrior:** one exact 128-slot ordinary selector with 106 occupied
  and 22 empty slots. The independently invoked Darkan charm selector remains
  a separate 606-way table.
- **Infernal Mage:** one guaranteed Bones row plus one exact 64,000-slot
  ordinary selector. Its two 1/512 Mystic rows become 125 slots each, the
  1/1,000 Lava battlestaff becomes 64 slots, and 10,186 slots are empty.
- **Basilisk:** one guaranteed Bones row plus one exact 64,000-slot ordinary
  selector. Mystic hat (light) occupies 125 slots, Basilisk head 32, and 343
  slots are empty.
- **Warriors' Guild Cyclops:** Darkan's 73 nonzero rows occupy 99,959 slots of
  one 100,000-slot ordinary selector. The rate-zero long/curved-bone table and
  guaranteed Big bones remain separate, as does the review-native progressive
  defender system.
- **Cyclossus:** the accepted Darkan ordinary rows occupy 89,390 slots of one
  100,000-slot selector. The period-common Dragon defender row remains a
  separate labeled abstraction because Darkan omits the unique-drop handler.
- **Desert lizard:** one guaranteed Bones row plus one exact 100,000-slot
  ordinary selector with 99,981 occupied and 19 empty slots.
- **Rockslug:** one exact 100,000-slot ordinary selector with 99,993 occupied
  and seven empty slots. Its separately sourced charm selector remains
  independent.
- **Gargoyle:** one exact 512-slot ordinary selector with 511 occupied and one
  empty slot, plus the separately sourced charm selector.
- **Mutated zygomite:** guaranteed Ashes, one exact 100,000-slot reconciled
  Darkan selector with 99,980 occupied and 20 empty slots, and the separate
  period-common Fungicide abstraction.
- **Young grotworm:** guaranteed Bones plus one exact 50,000-slot ordinary
  selector with 49,996 occupied and four empty slots.

The individual marginal probabilities are unchanged. The correction removes
impossible multi-drop combinations that the prior independent-table mapping
allowed.

## Audited unaffected targets

Otherworldly being, Bloodveld, Jelly, and Aberrant spectre already use one
ordinary selector. Crocodile intentionally exposes only its cutoff-proven
guaranteed Bones row. Ogre's rate-zero nested tertiary table is an always row
under `DropList`, so its separate long/curved-bone behavior remains correct.

## Verification contract

Regression coverage proves every selector sums to its exact denominator,
ordinary sibling rows cannot land together, all moved rare rows remain
reachable at their exact boundaries, Shadow-warrior charms still roll
separately, and Qt tooltips expose the actual live numerators and
denominators. Full-suite and audit results are recorded in
`memory-bank/status-updates/slayer-darkan-drop-selector-correction-results-2026-07-18.html`.
