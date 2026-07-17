# Summoning pets source audit (2026-07-16)

Scope: establish the pre-EOC pet boundary that was omitted from the initial Summoning
contract and isolate the one product decision historical evidence cannot make. Cutoff is
2012-11-20.

## Pinned period sources

1. **Pet**, oldid
   [6579897](https://runescape.wiki/w/Pet?oldid=6579897),
   2012-11-19 05:28:42 UTC.
2. **Follower details**, oldid
   [6093772](https://runescape.wiki/w/Follower_details?oldid=6093772),
   2012-08-15 03:51:25 UTC.

The literal Pet oldid contains the full freeze-date Summoning-pet level, stage, food,
acquisition, and colour table. Follower details corroborates that the live familiar
interface also served pets and exposed their hunger meter.

Reconstruction leads:

- Darkan `src/main/java/com/rs/game/content/pets/PetManager.java`,
  `Pet.java`, `PetDetails.java`, and `Pets.java`.
- Darkan `src/main/java/com/rs/game/content/skills/construction/playerOwnedHouse/`
  for the Menagerie projection.

Darkan corroborates the single-follower gate, per-pet Summoning requirements, stage
records, compatible foods, hunger, growth, and Menagerie integration. Its current
`Pet.java` increments hunger and growth but does not implement the period 100%-hunger
abandonment consequence; it cannot replace the pinned wiki for that behavior.

## Closed source facts

- Most pets were Summoning content: they required a Summoning level to obtain, raise, or
  keep, even when their acquisition route belonged to Hunter, quests, Soul Wars, nests,
  shops, or another system.
- A player could have only one pet, familiar, or NPC follower out at once. Pets therefore
  use the same global follower slot as familiars rather than a cosmetic parallel slot.
- A pet in the Bank, inventory, or player-owned-house Menagerie was inactive and required
  no care. The highest-level pet houses stored up to 15.
- Active pets exposed growth and hunger. Hunger reaching 100% caused the pet to abandon
  its owner. Young pets needed feeding more often than adults; feeding frequency did not
  affect growth rate.
- Most pets grew through two stages; cats and god birds had three. Some eggs first required
  a pet-shop incubator and remained there safely until collected.
- Kittens additionally required interaction or could run away.
- Nearly all pets were cosmetic. Period exceptions include god birds' God Wars protection,
  Broav quest function, cats catching rats, and other explicitly sourced pet-specific
  behavior. These exceptions must be catalogued rather than generalized into a pet buff.
- Pets could enter familiar-restricted areas, so the familiar forbidden-area catalog does
  not automatically apply to them.

## Source-shaped AnkiScape boundary

Pets are the tenth atomic Summoning family. Their complete catalog, stages, requirements,
food, acquisition routes, incubator state, exceptional functions, icons, persistence,
undo, and Menagerie storage must be designed and sourced before Summoning can close.
Construction's existing Menagerie dependency becomes a projection of these same pet
entities rather than a second pet inventory.

An active pet occupies the canonical global follower slot. Familiar automation cannot
summon or replace a familiar while a pet is out; it remains enabled but visibly lapsed
with `Pet occupying follower slot`. Picking up or storing the pet re-arms the familiar
policy under its already-settled next-successful-answer rules.

Active-pet growth and hunger advance on every answered-card world tick, including Again.
Stored pets do not advance either meter. Exact per-pet growth stages, hunger rates, food
effects, and interaction exceptions remain harvest work; Darkan values require period
corroboration before use.

Casual may reserve and automatically consume compatible target-carried pet food before a
hunger tick would reach 100%. It never feeds from Bank. Advanced chooses the exact food
budget and may disable automatic feeding. Feeding and direct pet interaction are bounded
UI commands with command undo, not review actions.

## Open owner fork: starvation safety

The source says 100% hunger immediately loses the pet. AnkiScape must decide whether to
preserve that immediate permanent loss or insert a visible review-native rescue window so
an unnoticed hunger transition during study cannot silently destroy a potentially rare or
quest-linked pet.

The recommended smallest safety abstraction is: reaching 100% creates a prominent hungry
pet world alert and a **one-answered-card rescue window**. The player may feed or pick up
the pet before the next answer. If the next answered card resolves while the pet remains
active and unfed, it runs away permanently, exactly as the source consequence requires.
Review undo restores the pet and pre-loss hunger state. This changes timing by one tick,
not the underlying loss rule.
