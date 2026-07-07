# Kebab and Beer Consumables — Source Audit

Audited: 2026-07-07 (implementation deferred to its own slice; owner decided
both become edible with source effects, auto-eat opt-in only).

## Kebab (2011Scape `Foods.kt calculateKebabEffect`, wiki-pinned Oct 2011:
`https://runescape.wiki/w/Kebab?oldid=4868155`)

Roll `Random.nextDouble(100)`:

| Range | Effect |
| --- | --- |
| < 8.71 | nothing ("That kebab didn't seem to do a lot.") |
| < 69.95 | heal 10% of max Constitution (LP) |
| < 91.07 | heal uniform 100..200 LP (`nextInt(100, 201)`) |
| < 94.72 | heal 300 LP **and** +2..3 (`nextInt(2, 4)`) to Attack, Strength, Defence current levels |
| else | lower a random non-Constitution skill (ids 0..24) by a few levels |

Kebab is excluded from the normal heal path (`heal = 0` in `Food.kt`; no
"restores health" message branch).

## Beer (2011Scape `PotionType.BEER` — it is a *potion* in the engine)

Strategies applied to current levels: `beerHealth` = +1 Constitution tick
(10 LP heal), `beerStrength` = `+floor(currentStrength * 0.04)`,
`beerDrain` = `-floor(currentAttack * 0.07)`.

## Blocking dependency

Both need a **temporary current-level substrate** (current vs base skill
levels with restoration over time). AnkiScape's combat recovery has
stat-drain *scaffolding* only; `attack_level` etc. are persistent base
levels today. The slice must build current-level state (restore 1 toward
base per N reviews, mirroring the engine's 100-tick restore loop) before
wiring either consumable. Auto-eat: both stay out of the default auto-eat
table — eligible only when the player explicitly ranks them in food
priority (owner decision).
