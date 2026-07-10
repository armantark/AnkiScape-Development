# Gap Grills 1-9 Provenance Audit — 2026-07-10

Scope: factual mechanics recorded during owner Grills 1-9. User-authored
AnkiScape abstractions are classified separately from claims about November
2012 RuneScape. Cutoff: `2012-11-20`.

## Result

- One confirmed OSRS contamination had already entered the backlog: craftable
  javelin heads/shafts. It is rejected and must not be implemented.
- One exact table was overstated as period-proven: Grenwall's 15% and 18% herb
  rolls. It is now quarantined pending historical corroboration.
- Two source translations were too coarse: Eagles' Peak gates ferret capture,
  not rabbit-snare placement, and ordinary ceremonial swords are a deliberate
  Grade-IV/Egil method rather than random burial interruptions. Both records are
  corrected; Aksel bronze-order scheduling is reopened for owner input.
- The other concrete numbers already recorded in these grills are either
  directly present in literal pre-cutoff wikitext or explicitly remain
  source-gated. No other modern RS3/OSRS value was found locked as parity.

## Grill-by-Grill Classification

### 1. Hunter tracking, pitfall, and rabbit snaring — verified scope; rolls gated

`Hunter` oldid 6484443 (2012-10-27) verifies all six recorded tracking targets,
the three pitfall creatures, rabbit snaring, noose/log/knife/teasing-stick and
ferret/snare requirements, pitfall damage, tatty/perfect furs and clothing,
long-kebbit bolt crafting, rabbit-foot stringing, and the relevant camouflage
effects. `Penguin (Hunter)` oldid 6099750 verifies the Hunt for Red Raktuber
gate, four capture methods, KGP-agent result, Jim hand-in, and bonus XP.
`Eagles' Peak` oldid 6579761 (2012-11-19) verifies that quest completion grants
the ability to capture ferrets and that those ferrets flush rabbits into snares.

The audit corrected one gate: the Hunter article explicitly says Eagles' Peak
is not required to lay/use a rabbit snare; it is required to catch the ferret
used to flush rabbits. AnkiScape must gate ferret acquisition and require the
item, not apply a direct quest lock to the snaring action. Unified inventory,
abstract travel, and review packing remain owner design. Exact success curves,
resource-loss rolls, pitfall damage amounts, and reward probabilities remain
source-gated where the literal pages do not supply them.

### 2. Herblore Habitat and Grenwalls — one quarantined table

Habitat is parked as an owner-approved Farming seed. `Herblore Habitat` oldid
6513740 (2012-10-31) verifies that Farming-grown vine flowers, vine bushes,
fruit trees, the constructed habitat feature, and relevant juju effects jointly
attract specific jadinkos; it also verifies real seeds, growth, costs, and
weekly changing god-jadinko preferences. Literal wikitext in `Grenwall` oldid
6196272 (2012-09-05) confirms 18-21 spikes, bones, and random grimy herbs from
roughly irit through dwarf weed. It does not state the precise 15% and 18% split.

Those exact rolls come from
`data/npcs/drops/hunter/hunter_grenwall.json`, introduced to the local Darkan
repository in commit `087e34d11` on 2022-03-01. They also match the live modern
RS3 table. This does not prove the values are wrong, but it means they are not
yet acceptable November 2012 parity evidence.

### 3. Runespan — period feature, rates still gated

`Runespan` oldid 6563925 (2012-11-16) confirms the period activity, temporary
essence/runes, creature and node siphoning, traversal costs, yellow wizards,
nodes, points, and reward shop. Persistent session handling, target labels,
checkboxes, and exit/reset behavior are owner design. The assertion that altar
runs should remain faster is a desired AnkiScape tradeoff awaiting the parked
historical training-guide audit; it is not recorded as a proven 2012 rate.

### 4. Bonfires — confirmed period mechanics plus owner abstractions

`Bonfire` oldid 6532063 (2012-11-04) literally confirms the five-or-more-player
Firemaking bonus, five-log warmth contribution, level-scaled maximum-lifepoint
boost, log-dependent warmth and burn durations, 10% Cooking XP bonus, and
1-in-100 fire-spirit chance. Automatic bank deposit, non-interrupting popup,
busy-public abstraction, and action-counter translation are deliberate
AnkiScape decisions rather than claims about the original client.

### 5. Artisan's Workshop — major source correction; narrow gaps remain

`Artisans' Workshop (historical)` oldid 6547352 (2012-11-10), `Respect
(Artisans' Workshop)` oldid 5579337 (2012-05-08), and `Ceremonial sword` oldid
6492957 (2012-10-29) verify storage caps, ingot grades, Suak's assigned burial
pieces, one percent Respect per 10,000 XP, ceremonial sword levels/materials,
plans and hammering/breakage, burst-pipe rewards, and the period reward catalog.

They also disprove the recorded scheduling premise. Ordinary members'
ceremonial swords use a deliberately withdrawn Grade IV ingot and a plan from
Egil. Separately, Aksel can issue random bronze ceremonial-sword orders as a
diversion. The previous design merged the two and is corrected. The compact UI,
simulated hammering, rewards-tab placement, and hidden inert rewards remain
owner design; Aksel-order scheduling is reopened. Exact burst-pipe repair time
and values present only through a transcluded reward template remain gated.

### 6. Blast Furnace, Goldsmith gauntlets, and cannonballs — confirmed

- `Blast Furnace` oldid 6555731 (2012-11-14) states the 2,500-coin, ten-minute
  under-level-60 fee and Ring of charos (a) halving it.
- `Goldsmith gauntlets (historical)` oldid 6544750 (2012-11-09) states the
  22.5-to-56.2 Smithing XP effect.
- `Cannonball` oldid 6541276 (2012-11-07) states level 35, Dwarf Cannon, ammo
  mould, one steel bar to four cannonballs, and 25.6 XP per bar.

The busy-public machinery, one inventory run per review, automatic fee renewal,
and target-specific equipment behavior are owner-approved abstractions. The
OSRS automated-worker coffer was explicitly rejected.

### 7. Karambwan, wine, and gnome recipes — confirmed core; tables gated

- `Gnome cooking` oldid 6438943 (2012-10-18) verifies the multi-stage gnome
  cocktail, crunchie, batta, and bowl recipe families and their intermediate
  ingredients.
- `Raw lava eel` oldid 5850448 (2012-06-28) and `Raw karambwanji` oldid 6174536
  (2012-09-01) verify both period input families.
- `Poison karambwan` oldid 6250179 (2012-09-16) states level 1 and 80 Cooking
  XP for the poor-cook result.
- `Cooked karambwan` oldid 6154936 (2012-08-28) states level 30, 190 Cooking
  XP, Tai Bwo Wannai Trio completion, and Tiadeche instruction.
- `Jug of wine` oldid 6151933 (2012-08-27) states grapes plus jug of water,
  level 35, 200 XP on success, an unfermented intermediate, and a ten-second
  wine/bad-wine resolution.

Atomic wine resolution and one recipe stage per review are owner decisions.
Exact lava-eel and gnome tables are still explicitly source-gated and were not
silently filled from current pages.

### 8. Javelin construction — confirmed contamination, resolved

`Javelin` oldid 6381785 (2012-10-10) literally says period javelins were not
smithable or fletchable. The proposed shaft/head chain belongs to later OSRS
Monkey Madness II/ballista content. The backlog item is rejected as
out-of-period rather than implemented.

### 9. Overload — confirmed pre-EOC

User-supplied `Overload` oldid 6552017 (2012-11-13) literally states level 96,
the five three-dose extreme potions plus clean torstol, overload (3), four
empty vials, 1,000 Herblore XP, five 100-lifepoint damage ticks, repeated boosts
for five minutes, and a 500-lifepoint restoration on expiry. The 500 restoration
therefore predates EOC. It is a direct expiry effect; the source gives no deeper
ingredient or regeneration explanation.

### 9a. Sanfew serum stages — confirmed pre-EOC

`Sanfew serum` oldid 6333478 (2012-10-02) literally defines three ordered
ingredient additions, two named intermediate mixtures, and a separate partial
XP award for every addition at each one-to-four-dose input size. Total XP is
96/128/160/192 for one/two/three/four doses, split as
28.5/38/47.5/57 for unicorn horn dust, 31.5/42/52.5/63 for clean snake weed,
and 36/48/60/72 for nail beast nails.

`Mixture - step 1` oldid 5500383 and `Mixture - step 2` oldid 5500399 (both
2012-04-16) explicitly mark the intermediates tradeable and use the period
Grand Exchange potion template. They are durable item/economy outputs, not
invented internal states. Owner design maps the three additions to three
separate dose-aware review targets.

## Operational Rule

For every remaining grill, attach each concrete value to one of:

1. literal pre-cutoff oldid wikitext;
2. a dated Wayback capture;
3. a period cache/script or local 2011 source; or
4. an explicit `source-gated` marker.

Current RS3, OSRS, and modern emulator reconstruction may suggest where to
look, but cannot independently close parity.

This rule is now project-wide, not limited to these nine grills. The durable
contract and dated cache manifest live in
`memory-bank/pre-eoc-source-verification-standard.md`.
