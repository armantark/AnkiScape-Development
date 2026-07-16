# Ranked design gaps from the overnight audit — 2026-07-16

This file is reserved for genuine creative-direction decisions that existing source evidence, product contracts, and established AnkiScape patterns do not settle. Routine bugs, parity facts, and implementation choices do not belong here.

## Priority ranking

### 1. Agility-course carried weight and death risk

The Werewolf deathslide formula requires actual carried weight, but Agility is excluded from the target-carried pack overlay. The shipped code instead reads `agility_carried_weight_kg`, which nothing writes. Simply weighing the flat `inventory` would incorrectly treat the entire Bank as carried. Adding Agility to the existing custom-pack UI also requires deciding whether course deaths grave that pack and what Casual mode carries.

Recommended direction: give Agility targets the existing Auto/Custom 28-slot pack. Auto carries only target-required items; Custom uses the saved layout. Agility failures use the clamped target pack plus equipment for weight, and fatal failures grave that same pack through the shared death channel. This is the most consistent interpretation of the settled actual-load rule, but it changes player-facing risk and deserves owner confirmation.

### 2. Charge duration in a review-native combat system

Charge spends runes and sets `magic_charge_active`, but nothing reads or clears it. Period behavior is time-limited and boosts god spells while the matching cape is worn; wall-clock duration is forbidden and the answered-card calendar is not a universal action-duration converter.

Recommended direction: make one Charge cast grant a fixed budget of eligible god-spell combat attacks, consumed only when a matching cape/staff god spell is attempted. The budget magnitude still needs an owner-approved review abstraction after the final source sweep.

### 3. Replacing mature regrowth crops

Bushes, fruit trees, cactus, calquat, and Habitat bushes regenerate produce indefinitely. The settled Farming contract defines `Clear` only for dead crops and tree stumps, so a healthy mature regrowth patch cannot be replaced with a different crop. Both `clear` and `chop` currently reject a depleted redberry bush.

Recommended direction: add an explicit one-review `Dig up` field verb for a healthy mature regrowth crop, requiring a Spade and returning no produce. Keep `Clear` restricted to the already-settled dead/stump semantics.

## Resolved without owner input

- The Pit's existing invitation gate now remains satisfied while its six-review challenge session is active.
- Fatal Agility failures use the established Thieving/Combat death presentation and deactivate training.
- Farming's settled watering multiplier, Magic's existing Farming-patch selector pattern, canonical Crafting item identities, Thieving's source denominator, and tooltip damage ranges required no new creative direction.
