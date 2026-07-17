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
Stored pets do not advance either meter, but both values and the growth stage persist
unchanged. Darkan commit `c343a917712649675989315009ce250639e0850f` stores
`PetDetails` separately by base pet item in
`src/main/java/com/rs/game/content/pets/PetManager.java:40-43,95-97`;
`Pet.pickup()` returns the item and clears only the active follower identifiers at
`src/main/java/com/rs/game/content/pets/Pet.java:96-105`.
Respawning therefore reuses the same details rather than constructing a fresh meter.
This reconciles with the period page's statement that stored pets are inactive and need
no care. Exact per-pet growth stages, hunger rates, food effects, and interaction
exceptions remain harvest work; Darkan's numeric values still require period
corroboration before use.

Pet activation follows the existing Bank item-action pattern without overloading item
discard: right-clicking a stored pet offers **Let out**, while **Release permanently...**
is a separate destructive command with a confirmation naming the pet, its growth stage,
and any known quest dependency. The canonical follower panel offers **Pick up** and shows
growth, hunger, compatible-food status, and the follower-slot lapse reason. These are
bounded UI commands with command undo, not review actions.

Casual pet care is enabled by default. At an existing Bank/preset boundary it
automatically chooses and packs compatible food from owned Bank stock into the real
28-slot carried inventory. The reserve is calculated from the sourced hunger cadence and
the target's expected next Bank boundary; it is not an invented fixed number of slots.
Food therefore keeps its authentic inventory opportunity cost without requiring the
owner to arrange it manually. Auto-care consumes carried compatible food before a hunger
tick would cross its feed threshold, including on Again. It never consumes food remotely
from Bank. At later Bank boundaries the same preset refills the reserve. Advanced chooses
the exact compatible food and quantity or disables auto-care.

A high-hunger stored pet is not healed by Bank. **Let out** runs the ordinary Casual
packing boundary, so compatible food is placed into real carried slots. On the first
answered-card tick, auto-care consumes carried food before hunger advances across its
threshold. If no compatible food exists, the pet may still be let out but the settled
automatic-return rule sends it home before the 100% tick. Advanced retains the stored
hunger value and its exact food/auto-care controls.

Cats remain stateful pet entities with their sourced three growth stages and exceptional
functions rather than becoming a generic quest flag. Quest requirements inspect the
specific owned cat/kitten stage. A step that sourcedly needs the cat to act also requires
the cat in the follower slot; mere ownership is sufficient only where the sourced quest
requirement is possession rather than active pet behavior. Kitten attention can be
fulfilled by Casual auto-care without a separate review or manual interaction, while the
exact quest and cat-function matrix remains catalog harvest work.

## Settled owner decision: no-food safety

The source says 100% hunger immediately loses the pet. The owner rejected the broader
Tamagotchi-style burden of monitoring hunger and kitten attention inside a game already
full of competing systems; rescue-window maintenance would preserve that burden rather
than solve it. AnkiScape therefore uses an explicitly labeled safety abstraction:
when an active pet has no compatible carried food and the next hunger tick would reach
100%, it automatically returns home to Bank (or its Menagerie slot) and the pet-care
policy lapses with `Out of pet food`. The triggering review's undo restores the active
pre-return state. Permanent loss remains available only through the explicit **Release
permanently...** command.

This preserves feeding's food and inventory cost, growth's follower-slot opportunity
cost, and the period consequence that an unfed pet stops following, while removing silent
loss of a quest-linked pet. Acquisition ownership and the full source-route matrix are in
`summoning-pet-acquisition-2026-07-16.md`.

## Release and reacquisition — source resolved 2026-07-16

The proposed special category of an unreclaimable one-time pet is not supported by the
period evidence. Pet rock explicitly permits repeated claims and multiple copies
([oldid 6359073](https://runescape.wiki/w/Pet_rock?oldid=6359073),
2012-10-06 21:07:09 UTC); Tooth creature explicitly gives a free replacement after
dismissal or running away
([oldid 6431044](https://runescape.wiki/w/Tooth_creature?oldid=6431044),
2012-10-17 01:38:42 UTC); Rune guardian, Baby troll, and the Firemaker's Curse fire pets
name replacement or respawn routes
([oldid 6546314](https://runescape.wiki/w/Rune_guardian?oldid=6546314),
2012-11-10 04:47:33 UTC;
[oldid 6570210](https://runescape.wiki/w/Baby_Troll?oldid=6570210),
2012-11-18 02:47:30 UTC;
[oldid 6387133](https://runescape.wiki/w/Searing_Flame?oldid=6387133),
2012-10-12 02:23:23 UTC). Pet fish is a repeatable Harry-owned catch procedure
([oldid 6530403](https://runescape.wiki/w/Fishbowl_%28pet%29?oldid=6530403),
2012-11-04 02:41:10 UTC), and clockwork cats are repeatably craftable and tradeable
([oldid 5918433](https://runescape.wiki/w/Clockwork_cat?oldid=5918433),
2012-07-10 20:53:05 UTC).

The Ex-ex-parrot and Broav pages document their initial routes but do not establish what
happens after the completed pet is deliberately released
([oldid 6546370](https://runescape.wiki/w/Ex-ex-parrot?oldid=6546370),
2012-11-10 04:59:32 UTC;
[oldid 6362753](https://runescape.wiki/w/Broav?oldid=6362753),
2012-10-07 05:51:05 UTC). Their reacquisition rows are therefore `source_blocked`, not
evidence of permanent loss.

There is no special unreclaimable-pet confirmation. The ordinary destructive confirmation
states a replacement route only when the catalog has a pinned route, and never claims
`Cannot be reobtained` without affirmative period evidence. A source-blocked reacquisition
row blocks shipping Release for that pet until the route is resolved; it does not invent
either a reclaim or permanent-loss rule.

## Exceptional-function execution

Exceptional functions remain native to the system and context that gives them meaning;
the Pets log only explains and links them.

- Releasing a platypus at the same quest location grants another casket or oyster
  ([oldid 6579823](https://runescape.wiki/w/Platypus?oldid=6579823),
  2012-11-19 04:45:04 UTC). This is a distinct contextual Hunter/quest action,
  **Release for reward...**, that atomically consumes the active platypus and grants the
  sourced roll. It is not generic **Release permanently...** and cannot award that reward
  outside the sourced context.
- Cats catch ordinary rats through the explicit **Interact-with → Chase-vermin** command
  ([oldid 6283489](https://runescape.wiki/w/Cat?oldid=6283489),
  2012-09-23 03:37:47 UTC). Hell-rats use the same deliberate chase and produce ashes plus
  a random spice
  ([oldid 6504243](https://runescape.wiki/w/Hell-Rat?oldid=6504243),
  2012-10-30 17:15:00 UTC). Cat ratting is therefore an explicit native target with one
  chase attempt per review by default, not ambient output while training something else.
- Wily cats become lazy after a sourced random short interval and require a random amount
  of interaction to retrain
  ([oldid 6390175](https://runescape.wiki/w/Wily_cat?oldid=6390175),
  2012-10-12 12:21:52 UTC). Casual automates those interactions but does not erase their
  cost: retraining consumes source-mapped interaction reviews before ratting resumes.
  Exact distributions remain source-harvest work.
- Tooth creature's adult form is irreversibly selected if it receives chocolatey milk
  even once
  ([oldid 6431044](https://runescape.wiki/w/Tooth_creature?oldid=6431044),
  2012-10-17 01:38:42 UTC). Casual defaults to the healthy form and never silently packs
  variant-changing food; with no non-transforming compatible food, the existing
  automatic-return rule applies. Advanced's exact food selection is the deliberate path
  to the decayed form.

Review-driven growth that removes a pet capability, such as an adult cat becoming
overgrown and losing rat-catching, uses the owner's already-settled expiration-alert rule:
the shared reviewer world-alert strip gives a one-time warning with approximate answered
cards remaining. It never pauses or delays the sourced transition.

God bird oldid
[6579887](https://runescape.wiki/w/God_bird?oldid=6579887)
(2012-11-19 05:27:38 UTC) establishes that only the mature Zamorak hawk and Saradomin owl
stop their respective God Wars warriors from attacking; the Guthix raptor has no matching
faction and no protection. The individual owl and hawk pages further require the mature
bird to be actively following rather than carried in inventory
([oldid 6474427](https://runescape.wiki/w/Saradomin_owl?oldid=6474427),
2012-10-26 02:35:48 UTC;
[oldid 6274378](https://runescape.wiki/w/Zamorak_hawk?oldid=6274378),
2012-09-21 03:25:13 UTC).

The current one-enemy Combat model cannot represent ambient faction aggression honestly.
The owner parked that larger multi-enemy design grill. The pet catalog still records the
stage-gated faction-protection flag now, but it has no invented damage reduction or
ambient-pressure number. A future God Wars/multi-enemy substrate consumes the flag
automatically without changing the pet row.
