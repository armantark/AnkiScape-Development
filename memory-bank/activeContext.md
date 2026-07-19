# Active Context

## Current Focus

The ordinary level-46 Harpie Bug Swarm is now the 29th executable Vannaka
family: Slayer 33, 250 LP, 25 Slayer XP, six-tick melee, a 60-LP maximum,
Darkan's exact 100,000-slot ordinary selector, and its separately derived
202-slot charm selector. A lit bug lantern must remain equipped in the shield
slot; the 130-coin unlit shop item now lights at Firemaking 33, extinguishes
through the existing Utility pattern, and generates wearable lit item 7053.
The lit lantern correctly does not count as cave illumination. Vannaka remains
hidden at 29/35 with six missing representatives. The pinned wiki and Darkan
drop contents conflict, so the executable selector is labeled rather than
misrepresented as closed historical drop parity. No owner-facing design fork
emerged. Evidence:
`source-audits/slayer-harpie-bug-swarm-combat-2026-07-18.md`. Results:
`status-updates/slayer-harpie-bug-swarm-results-2026-07-18.html`
(<https://lwn2getn9lo2.postplan.dev>). The full non-Qt and real offscreen Qt
suites each pass all 1,640 tests; the non-Qt environment declares 215 Qt-only
skips, while the real Qt run has zero skips.

The ordinary level-79 Green dragon is now the 28th executable Vannaka family:
750 LP, 75 Slayer XP, six-tick melee, 85-LP melee maximum, guaranteed Dragon
bones and Green dragonhide, the exact imported drop selectors, and the existing
Wilderness-risk contract. Dragonfire now has source-shaped flat-damage tiers:
500 LP unprotected, 50 LP with one shield/prayer/Antifire layer, and zero with
Super antifire or regular Antifire plus a shield/prayer layer. Six-minute vial
and flask doses are review-driven, preserve remainders, load automatically,
and can expire and refresh inside one long Combat review. Anti-dragon shield is
wearable with exact item-config bonuses. Exact Green-dragon charm rates remain
`source_blocked`; the 1/4 breath frequency is labeled `provisional/darkan`
because game-main conflicts at 1/10. Vannaka remains hidden at 28/35 with seven
missing representatives. No owner-facing design fork emerged. Evidence:
`source-audits/slayer-green-dragon-combat-2026-07-18.md`. Results:
`status-updates/slayer-green-dragon-results-2026-07-18.html`
(<https://blwhzxpwaa52.postplan.dev>).

Earth warrior now carries the owner-approved Wilderness Combat risk instead of
being a risk-free Vannaka representative. Every successful review has the
labeled 1%/250-LP bounded ambush chance; a trigger resets the monster
encounter. Fatal ambushes keep the three highest-value equipped items, add one
with active Protect Item, retain ordinary inventory, permanently lose the rest
of the equipped risk set, and create no new grave. A process-local fingerprint
requires explicit current-risk confirmation after Anki restart or a material
equipment/protection change. Safe-skill reviews discard Wilderness encounter
progress. Vannaka advances to 27/35 and remains hidden with eight missing
Combat representatives. No owner-facing design fork emerged. Evidence:
`source-audits/slayer-earth-warrior-wilderness-risk-2026-07-18.md`. Results:
`status-updates/slayer-earth-warrior-wilderness-results-2026-07-18.html`
(<https://73amt4x2o23l.postplan.dev>).

The ordinary level-93 Dust devil is now an executable Vannaka-family Combat
target with Slayer 65, 1,050 LP, 105 Slayer XP, six-tick melee, a 90-LP
maximum hit, and the cutoff's continuous protective-headgear damage gate. The
Chaos Tunnels route avoids inventing Desert Treasure quest content. Darkan
supplies exact stats, one 32,768-slot ordinary selector, exact nested tables,
and an independent 606-way charm selector. Dragon chainbody item 3140 is now
generated as Defence-60 body equipment; the generator honours a drop row's
exact source item ID before same-name fallback. Vannaka advances to 26/35
while remaining hidden. Eight Combat targets and Earth warrior's Wilderness
risk remain. No owner-facing design fork emerged. Evidence:
`source-audits/slayer-dust-devil-combat-2026-07-18.md`. Results:
`status-updates/slayer-dust-devil-results-2026-07-18.html`
(<https://dylce5d5v14s.postplan.dev>).

The Darkan ordinary-drop loader is now mapped correctly across every live
Slayer target that had been treating sibling JSON rows as independent rolls.
`DropList` makes one cumulative ordinary selection; only rate-zero always
rows, separately invoked charm tables, and explicitly labeled abstractions
remain separate. Eleven targets were corrected: Warriors' Guild Cyclops,
Cyclossus, Young grotworm, Desert lizard, Rockslug, Gargoyle, Mutated
zygomite, Jungle horror, Shadow warrior, Infernal Mage, and Basilisk.
Individual marginal probabilities are unchanged, while impossible sibling
multi-drop combinations are removed. No owner-facing design fork emerged.
Evidence:
`source-audits/slayer-darkan-drop-selector-correction-2026-07-18.md`.
Results:
`status-updates/slayer-darkan-drop-selector-correction-results-2026-07-18.html`
(<https://pk45017w1z2j.postplan.dev>).

The ordinary level-48 Shadow warrior is now executable with the existing
Legends' Quest gate, six-tick melee, 670 LP, 67 Slayer XP, Darkan's exact
128-slot ordinary selector, and the separately invoked emulator-exact charm
selector. This adds no quest content and does not overlap the Darkan
quest-parity thread. Vannaka
advances to 24/35 while remaining hidden. Exact period defensive bonuses
remain `source_blocked`; no owner-facing design fork emerged. Evidence:
`source-audits/slayer-shadow-warrior-combat-2026-07-18.md`. Results:
`status-updates/slayer-shadow-warrior-results-2026-07-18.html`
(<https://4c0ztjs0b4cs.postplan.dev>).

The ordinary level-70 Jungle horror is now executable with the existing Cabin
Fever gate, six-tick melee, 450 LP, 45 Slayer XP, guaranteed Bones, and
Darkan's exact 100,000-slot ordinary selector. This adds no quest content and
does not overlap the Darkan quest-parity thread. Vannaka advances to 23/35
while remaining hidden. Exact period charm distribution remains
`source_blocked`; no owner-facing design fork emerged. Evidence:
`source-audits/slayer-jungle-horror-combat-2026-07-18.md`. Results:
`status-updates/slayer-jungle-horror-results-2026-07-18.html`
(<https://7s9qx4vwmhao.postplan.dev>).

The ordinary level-64 Otherworldly being is now executable with the existing
Lost City gate, six-tick melee, 660 LP, 66 Slayer XP, and Darkan's exact
128-slot table. This adds no quest content and does not overlap the Darkan
quest-parity thread. Vannaka advances to 22/35 while remaining hidden.
Evidence: `source-audits/slayer-otherworldly-being-combat-2026-07-18.md`. No
owner-facing design fork emerged. Results:
`status-updates/slayer-otherworldly-being-results-2026-07-18.html`
(<https://q57byaii1o36.postplan.dev>).

The ordinary level-63 River Elid Crocodile is now executable with Slayer 10,
five-tick melee, 630 LP, 62 Slayer XP, guaranteed Bones, and the existing
review-driven desert-heat supply loop. The level-89 marsh form and Darkan's
merged Big-bones row are deliberately excluded. Vannaka advances to 21/35
while remaining hidden. Evidence:
`source-audits/slayer-crocodile-combat-2026-07-18.md`. No owner-facing design
fork emerged. Results:
`status-updates/slayer-crocodile-results-2026-07-18.html`
(<https://kjy22255e4a6.postplan.dev>).

The ordinary level-61 Basilisk is now executable with Slayer 40, six-tick
melee, 750 LP, 75 Slayer XP, and the source's Mirror-shield requirement.
Unshielded damage can be stopped by Protect from Melee while the random
five-level stat drain still lands; the magnitude is explicitly
`abstraction/darkan`. Mystic hat (light) is generated equipment and the
existing Basilisk head now carries its real item identity. Vannaka advances to
20/35 while remaining hidden; charm distribution stays `source_blocked`.
Evidence: `source-audits/slayer-basilisk-combat-2026-07-18.md`. No owner-facing
design fork emerged. Results:
`status-updates/slayer-basilisk-results-2026-07-18.html`
(<https://12bv7z5x53a2.postplan.dev>).

The ordinary level-66 Infernal Mage is now executable with Slayer 45, six-tick
Magic attacks, 600 LP, 60 Slayer XP, and one exact 64,000-slot ordinary
selector. Lava battlestaff, dark Mystic hat, and dark Mystic boots are generated
equipment with their exact period requirements, bonuses, and weapon speed.
Vannaka advances to 19/35 while remaining hidden; 15 target families plus the
Earth-warrior Wilderness-risk seam remain. Charm distribution is
`source_blocked`, not fabricated. Evidence:
`source-audits/slayer-infernal-mage-combat-2026-07-18.md`. No owner-facing
design fork emerged. Results:
`status-updates/slayer-infernal-mage-results-2026-07-18.html`
(<https://6zhziqqts1l7.postplan.dev>).

The ordinary level-76 Bloodveld is now executable with Slayer 50, six-tick
magic-based melee, 1,200 LP, 120 Slayer XP, and Darkan's exact 128-slot
ordinary table. Black boots item 4125 are generated from the 2011Scape
equipment block with their Defence-10 gate and exact bonuses. Vannaka advances
to 18/35 while remaining hidden; the separate level-81 God Wars variant remains
pinned rather than duplicated as a cosmetically similar row. Evidence:
`source-audits/slayer-bloodveld-combat-2026-07-18.md`. No owner-facing design
fork emerged. Results:
`status-updates/slayer-bloodveld-results-2026-07-18.html`
(<https://k9ynbzcx5a8u.postplan.dev>).

The ordinary level-78 Jelly is now executable with Slayer 52, magic-based
melee, six-tick attacks, 750 LP, 75 Slayer XP, Darkan's exact 128-slot table,
and real Defence-20 Mithril boots generated from 2011Scape item 4127. Vannaka
therefore advances to 17/35 while remaining correctly hidden. The ordinary
target excludes Soul Wars' separate fragment/PvP context, and the OSRS-derived
visuals are labeled visual-only rather than passed off as cutoff file
revisions. Evidence: `source-audits/slayer-jelly-combat-2026-07-18.md`. No
owner-facing design fork emerged. Results:
`status-updates/slayer-jelly-results-2026-07-18.html`
(<https://qvrpp85jnouq.postplan.dev>).

Vannaka's complete cutoff pool is represented in executable data: all 35
families, their reconciled weights and count ranges, the provisional 460-point
denominator, and stable target/mechanic dependency identities. The role remains
correctly hidden; `tools/audit_slayer_readiness.py` derives its exact blockers
instead of trusting a prose count. The ordinary level-53
Ogre closes one family with 600 LP, 60 Slayer XP, the exact Darkan common-seed
subtable, independent long/curved-bone tertiary rolls, guaranteed Big bones,
and a pre-cutoff sprite. Mogres remain owned by the Darkan quest pass through
`skippy_and_the_mogres`; no quest definition was duplicated. Durable evidence
is `source-audits/slayer-vannaka-ogre-combat-2026-07-18.md`. No owner-facing
design fork emerged. Results:
`status-updates/slayer-vannaka-ogre-results-2026-07-18.html`
(<https://o849m34h9y3r.postplan.dev>).

Warriors' Guild is now live as the honest executable boundary for
Mazchna/Achtryn's Cyclopes family. Five Utility activities feed five persistent
token balances; Casual auto-balances or falls back to the fastest viable
single-token route, while Advanced exposes exact activity and room-payment
selection. The Cyclops room preserves entry and residual-based drain, melee
restriction, multi-token benefits, progressive defender drops, explicit
Kamfreena showing, and recovery from the best retained defender. A sourced
Cyclossus can now interrupt the loop after Rune is shown, requires a worn Rune
or Dragon defender, and carries its own combat/drop/helmet surface. The compact
Qt panel and all activity, enemy, defender, and helmet assets are checked in.
`tools/audit_slayer_readiness.py` now reports Mazchna/Achtryn at 26/27 with
only Mogres blocked by the Darkan-owned `skippy_and_the_mogres` quest
dependency; the partial master remains hidden. Undocumented rates are labeled
bounded abstractions, and no owner design fork emerged. Durable evidence is
`source-audits/warriors-guild-live-implementation-2026-07-18.md`. Full core
and real offscreen Qt discovery each pass all 1,592 tests, and the equipment
registry reproduces from its generator. The visual closure report is
`status-updates/warriors-guild-results-2026-07-18.html`
(<https://vsx8a7pxsimj.postplan.dev>).

The ordinary level-85 Kalphite Soldier is now an executable Slayer Combat
target, closing Mazchna/Achtryn's Kalphites family. It preserves 900 LP, 90
Slayer XP, the period six-tick melee attack, the approximate 80-LP maximum hit,
and Darkan's exact 128-slot drop table. The existing game-main-shaped poison
channel cannot encode the period 48-LP initial hit exactly, so the row uses the
nearest representable 50 LP and states that bounded abstraction explicitly.
The Combat picker exposes poison risk, the complete table, and the pre-cutoff
target sprite. Mazchna/Achtryn remains correctly hidden at 23/27; the four
remaining Combat-target blockers are Cyclopes, Mogres, Vampyres, and Wall
beasts. Full core and real offscreen Qt discovery each pass all 1,566 methods;
test quality reports zero hard issues. No owner design gap emerged. Durable
evidence is `source-audits/slayer-kalphite-soldier-combat-2026-07-18.md`; the
visual report is
`status-updates/slayer-kalphite-soldier-combat-results-2026-07-18.html`
(<https://trn4s92bn2a4.postplan.dev>).

Mazchna/Achtryn is now the second fully represented Slayer-master pool, but it
remains correctly hidden. The data model separates stable family identity from
master-specific weight/count rows, preserving all 27 reconciled families and
the provisional 325-point denominator without mutating Turael's values. The new
`tools/audit_slayer_readiness.py` derives certification from live target,
Slayer-XP, poison, protection, and finisher dependencies. It certifies
Turael/Spria at 23/23 and reports Mazchna/Achtryn at 23/27 with exactly four
Combat-target blockers: Cyclopes, Mogres, Vampyres, and Wall beasts.
The audit also rejects malformed roll rows, denominator drift,
enabled partial masters, and certified-but-forgotten hidden masters. Both
Hobgoblin variants now award their pinned 29/49 Slayer XP. No owner design gap
emerged. The closure report is
`status-updates/slayer-mazchna-readiness-results-2026-07-18.html`
(<https://ir3cpm2ptnfp.postplan.dev>).

Mutated zygomite is now the fourth and final ordinary Slayer finishing-blow
family. Both cutoff variants are executable at Slayer 57 after Lost City, with
their distinct 650/750 LP and 65/75 Slayer XP rows, period file-revision
sprites, guaranteed Ashes, and one reconciled ordinary selector. The charged
Fungicide-spray runtime preserves every remaining dose, reloads an empty spray
from one loaded canister, supports the quick-finisher unlock without bypassing
item cost, and respects the shared 28-slot Combat pack. The Combat picker
exposes the `Pick fungi` encounter abstraction, access gate, live charges, and
canister reloads. The occasional 140-LP spore attack frequency remains
`source_blocked` and is not simulated. Durable evidence is
`source-audits/slayer-mutated-zygomite-combat-2026-07-18.md`. Full core and
real offscreen Qt discovery each pass all 1,557 methods; the core runner records
213 declared environment skips while Qt records none. The visual closure report
is `status-updates/slayer-mutated-zygomite-results-2026-07-18.html`
(<https://ujk2cg24j80q.postplan.dev>).

Shilo Village is now a complete live Slayer dependency. Eleven review-native
requirements plus the completion sentinel cover the Wampum handoff, Ah Za
Rhoon, both scrolls and Zadimus, Bervirius's evidence, Bone key and Beads
transformations, the three-bone tomb gate, all three ordered Nazastarool forms,
and Rashiliyia's release. The optional Stone-plaque remains obtainable but is
not a false progression gate. Thirteen period quest-item sprites and cache
identities are registered, including real Beads of the dead neck equipment.
Completion grants two quest points and 3,875 Crafting XP and preserves the
Shilo, cart, and gem-rock unlocks. Durable evidence is
`source-audits/quest-shilo-village-playable-2026-07-18.md`. Full core discovery
passes all 1,546 methods with 213 declared environment skips; full real
offscreen Qt discovery passes all 1,546 methods. The visual closure report is
`status-updates/quest-shilo-village-results-2026-07-18.html`
(<https://tqgeemw7wsuo.postplan.dev>). The next Slayer implementation
dependency is Jungle Potion fidelity, then Big Chompy Bird Hunting, Zogre Flesh
Eaters, Rum Deal, and Cabin Fever before Mos Le'Harmless, Cave horrors, the
black-mask drop, and Slayer-helmet assembly.

Turael/Spria is now the first complete live Slayer-master role. The full
23-family weighted pool is assignment-ready, matching Combat kills award Slayer
XP and decrement task progress atomically, and the management surface exposes
Assignment, Masters, and Smoking-Kills-gated Rewards tabs without turning
Slayer into a review-training target. The last target blockers are closed:
Gelatinous abominations require worn reusable Spiked gauntlets at the sourced
one-LP boundary; Young grotworms and Monkeys have period identities, stats,
drops, and assets; Coral bolts and Royal cape are real registered equipment.
Complete core discovery passes 1,537 methods with 1,326 ordinary passes and 211
declared environment skips; complete real offscreen Qt discovery passes all
1,536 methods without skips or failures, with the latest item-only seams covered
by a targeted holdout. Durable evidence is
`source-audits/slayer-turael-runtime-closure-2026-07-17.md`; the visual report is
`status-updates/slayer-turael-runtime-results-2026-07-17.html`
(<https://5k6wxpak7xkj.postplan.dev>).

Icthlarin's Little Helper is now the third playable Slayer-critical quest
dependency. Its generated placeholder sequence and statless fights are replaced
by a nine-step review-native chain covering the Wanderer's hypnosis, canopic
jar and Sphinx-token custody, one bounded representative guardian, the
Sophanem ceremony, holy-to-unholy symbol transformation, the Possessed Priest,
and exact ordinary completion rewards. The implementation deliberately
separates both Combat boundaries from their surrounding inventory transactions,
so the player never carries the canopic jar or unholy symbol into the fight and
does not need post-guardian ceremony supplies prematurely. Seven period quest
icons are registered with pre-cutoff provenance, and the reusable asset fetcher
can now select the newest file revision at or before a historical cutoff. The
complete core suite passes all 1,517 methods with 1,310 ordinary passes and 207
declared environment skips; the matching real offscreen Qt discovery passes all
1,517 methods without skips or failures. Smoking Kills is now complete;
Contact! was not required by its pinned cutoff quest requirements. Durable
evidence is
`source-audits/quest-icthlarins-little-helper-playable-2026-07-17.md`; the
visual closure report is
`status-updates/quest-icthlarins-little-helper-results-2026-07-17.html`
(<https://llzbgu6xic8d.postplan.dev>).

Diamond in the Rough is now the second playable Slayer-critical quest
dependency. Its four generated placeholders and grouped statless fight are
replaced by the Heavy weight, five Bandits plus their king, Sundial gnomon,
Kalphite-nursery gem recovery, ordered Apep/Heru finale, and Prince Ali rescue.
The reward override removes the two optional 20,000-XP level-80 fissure rewards
from automatic completion while preserving the ordinary 250-XP trio, Combat
lamp, and three retained gems. Focused backend and real offscreen Qt checks
pass. The complete core suite passes 1,512 methods with 1,306 ordinary passes
and 206 declared environment skips; real offscreen Qt passes all 1,512 methods
without skips or failures. Durable evidence is
`source-audits/quest-diamond-in-the-rough-playable-2026-07-17.md`; the visual
closure report is
`status-updates/quest-diamond-in-the-rough-results-2026-07-17.html`
(<https://6vqmrgu0eo7j.postplan.dev>).

The Slayer-critical quest dependency pass has begun with Stolen Hearts. Its
generated five-row placeholder sequence is now a playable source-backed chain:
Skulls infiltration, the Khnum pursuit, Mercenary Joe plus two Skulls
mercenaries, ransom-note and history-book custody, rooftop/treasury traversal,
Het's scales, the Kharid-ib, and Osman's handoff. The override removes the bogus
Khnum item reward, prevents generated lamp XP from being double-counted, adds
the exact direct 250 Constitution XP and 2,500 coins, and registers period item
identities and icons. Focused backend and real offscreen Qt checks pass; the
complete core suite passes 1,508 methods with 1,303 ordinary passes and 205
declared environment skips, while real offscreen Qt passes all 1,508 methods
without skips or failures. Diamond in the Rough is the next independent
Smoking Kills prerequisite. Durable evidence is
`source-audits/quest-stolen-hearts-playable-2026-07-17.md`; the visual closure
report is `status-updates/quest-stolen-hearts-results-2026-07-17.html`
(<https://4sptl2883909.postplan.dev>).

Rockslug and Gargoyle are now executable Slayer Combat targets rather than
finisher-engine blockers. Rockslug preserves the cutoff 1–39 LP Bag-of-salt
window, consumable salt, and a latched 10-LP frozen/no-retaliation state.
Gargoyle preserves the below-90 LP reusable Rock-hammer action and carries its
`12/5` LP-per-game-tick regeneration residual across review boundaries. Both
use one reconciled Darkan ordinary selector plus Summoning-era charm rolls,
period-source icons, normal manual/quick finisher semantics, and real Combat
picker surfaces. The ordinary target excludes Kuradal's-Dungeon-only Ferocious
rings. Core verification passes all 1,504 methods with 204 declared
environment skips; focused backend and all 200 real main-menu Qt checks pass.
The Qt harness now flushes deferred dialog deletion between tests, reducing the
widget suite's measured peak resident memory from 9.7 GB to 1.22 GB. Full real
offscreen Qt verification passes all 1,504 methods without skips or failures.
Durable evidence is
`source-audits/slayer-rockslug-gargoyle-combat-2026-07-17.md`.

The personal-fork-versus-public-release question is settled as **prepare a
separately named public derivative release**, not upload immediately. Wilson Yeh
must be credited prominently as the original creator; Arman is the independent
maintainer of the radically expanded derivative. The release uses a new
AnkiWeb listing, an explicit AGPL-3.0-or-later compatible license, durable
credits, synchronized public source, a corrected review link, and closed asset
provenance and release-engineering gates. The governing decision, measurement,
copy, outreach note, blockers, and ordered go-live script are in
`public-release-lineage-and-license-2026-07-17.md`.

The shared catalog search seam is implemented across Shop, Quests, and Combat.
`CatalogFilterBar` standardizes dark-mode-safe search, clear/Escape behavior,
page-owned filters, and count summaries without owning result semantics.
Combat search preserves the saved target, expands matching groups, and cannot
activate an absent or empty row; Quest text search composes with every existing
catalog filter. The `Current Slayer task only` checkbox remains correctly
deferred until authentic assignment state exists instead of shipping a dead
control. The complete pure suite passes all 1,478 methods; real offscreen Qt
discovery also passes all 1,478 methods with no failures or skips. The closure
report is `status-updates/slayer-search-seam-results-2026-07-17.html`, with a
mobile-safe copy at <https://s1kaasu9wfmq.postplan.dev>.

Live cadence activation and the Design 2 reconciliation are verified and ready
for their atomic commit. The post-review complete core suite passes all 1,476
methods (1,275 ordinary passes and 201 environment skips); the matching real
offscreen Qt suite passes all 1,476 methods with no skips. The
focused cadence/kernel/parity/combat/runtime/Summoning/Thieving set passes 363
methods, and no cadence test is skipped or marked as an expected failure. The
final independent review caught and closed a successful-answer disengagement
inversion that could have allowed Dream healing between every live Combat
slice; Again now remains the only answer path that marks disengagement, and its
next successful slice resumes identical combat/RNG phase. Documentation,
compilation, reachability, asset, worktree-safety, and test-quality gates are
clean. The current Anki process predates this candidate, so the next ordinary
Anki restart is the manual live-load smoke rather than a reason to disrupt an
active review session during closure. The closure report is
`status-updates/cadence-kernel-live-results-2026-07-17.html`, with a mobile
copy at <https://nl2rgoy9pvqk.postplan.dev>.

Summoning is now the eighteenth complete skill surface. The 2026-07-17 closure
ships the full ordinary pouch/scroll catalog, training, follower lifecycle,
points, BoB cargo, Familiarisation, the freeze-date pet family, restoration
potions, all 78 Bogrog exchanges, Pack yak Winter Storage, and the source-ready
boost/heal/escape effects. Daemonheim remains outside the overworld. Remaining
combat-scroll, forager, and teleport rows are explicit source/dependency blocks,
not exposed approximations, and no owner-level Summoning design gap remains.
Closure verification passes 1,446 core methods (1,242 ordinary passes, 201
environment skips, three expected failures) and 1,446 real offscreen Qt methods
(1,443 ordinary passes, three expected failures), plus focused Bogrog/follower
UI, docs, test-quality, compilation, JSON, reachability, generator-determinism,
diff, and worktree-safety checks. The reachability report records 1,220 actions
and 290 known acquisition/dependency orphans (112 root, 178 cascade); it remains
an explicit debt ledger rather than a green gate.

The active non-Summoning grill-harvest follow-up has closed its final two owner
questions. Mage Arena now has final-form alignment, matching first cape/staff,
review-native per-spell attunement, one-cape statue replacement/reclaim, and
Charge's matching-loadout +100 LP god-spell maximum-hit effect. Farming
auto-cure now saves a per-patch `Plant cure first` / `Cure Plant first`
preference, snapshots it into presets and queued steps, and falls back
atomically through the canonical item or Magic transaction. Config v40
preserves legacy Mage Arena completions and normalizes both new schemas. The
final candidate passes 1,388 core methods and 1,388 real offscreen Qt methods;
test quality, documentation, compilation, JSON, reachability, asset provenance,
diff, and worktree-safety gates pass.

The earlier loop also closed Magic Charge review duration (`6639a48`), Bank
quantity controls (`8426fa2`), the corrected Charge source boundary
(`8b6a561`), Agility carried risk (`69855d9`), and Farming replacement/preset
planning (`9b65f45`). The former open design ledger is now archived at
`archive/2026-07/resolved-queues/design-gaps-grill-harvest-2026-07-17.md`.
The owner released Summoning implementation after the final Winter Storage fork
closed at `d7539c9`.

Slayer's source-first owner grill is design-closed and integrated into `main`.
The governing record is `slayer-skill-contract-2026-07-15.md`, supported by
focused audits for master succession/challenges, finishing blows, locations,
points/rewards, Social Slayer, and the post-cutoff VIP-ticket exclusion. Live
assignment gameplay remains closed, but source-ready Combat dependencies are
now landing atomically: Cockatrice protection is complete, the finisher
supplies are obtainable, and Jackal now supplies an executable Dogs-family
variant. The ordinary level-13 Icefiend now supplies a second missing family
without folding in its God Wars, Ghorrock, quest, Revenant, or Daemonheim
forms. The Jackal slice passes the complete 1,481-method core suite, 337
focused Combat/runtime methods, and a real offscreen Qt picker check. The
Icefiend checkpoint passes all 1,482 core methods, 339 focused methods, and the
same real offscreen Qt picker path. Banshee protection is now executable too:
an unprotected scream applies the period damage shape and full eight-skill set
through a deliberately labeled flat-five abstraction; equipped Earmuffs or
Slayer-helmet-family headgear suppress it. Desert lizard is the first live
finisher family: Slayer 22, its Ice-cooler 1–30 LP gate, the 400-point
automatic-finisher flag, one exact ordinary drop selector, and a sourced
sprite are executable. Desert heat is a labeled review-native supply abstraction: each
damaging Combat review consumes one Waterskin dose, preserves the lower-dose
skin, and uses the ordinary two-review bank refill. Exact cutoff heat
timing/damage remains `source_blocked`; no wall-clock mechanic was introduced.

The first master-pool harvest is now recorded in
`source-audits/slayer-turael-spria-pool-2026-07-17.md`. Reconciliation recovered
23 ordinary Turael/Spria families, including the master-table omissions
Gelatinous abominations and Grotworms, and rejected the anonymous Troll row.
Hidden weights remain explicitly provisional; the 355-point denominator
converges across Darkan's raw values, game-main's percentages, and the recovered
30-weight Gelatinous family. Jackal closes the Dogs-family target, and the
cutoff level-13 Icefiend closes Icefiends with 150 LP, 15 Slayer XP, a 20 LP
maximum hit, and its complete 128-slot ordinary drop table. Runtime
certification still fails: Desert lizards are now executable, three families
still have no Combat target, and Gelatinous
abominations lack the worn-gauntlet finisher. None of these findings creates an
owner design question.

The second master-pool harvest is recorded in
`source-audits/slayer-mazchna-achtryn-pool-2026-07-17.md`. It reconciles a
27-family functional pool and a provisional 325-point hidden-weight
denominator. The earlier Knowledge Base correction, Achtryn's cutoff table, and
Darkan close the malformed Mazchna `40–85` range at `40–70`; Cyclopes remain
`30–60`, the repaired cutoff row span closes Grotworms at `40–70`, and Wall
beasts remain `10–20`. Mogre and Wall-beast weights are explicit 10-point
common-baseline abstractions because both emulator task-family entries are
stubs. Runtime certification still fails: ten families have no Combat target,
three existing
families lack required Slayer/protection behavior, and no assignment-family
registry exists. This pass repaired Cave crawler's omitted source
`poisonDamage = 8`. No owner design question emerged.

The third master-pool harvest is recorded in
`source-audits/slayer-vannaka-pool-2026-07-17.md`. It reconciles the cutoff
35-family pool and a provisional 460-point denominator. Darkan's unsupported
Troll row is replaced by the cutoff Mogre and Sea-snake families; their
10-point values are labeled common-baseline abstractions. Grotworms use the
ordinary `60–120` Darkan range rather than treating the cutoff page's single
observed assignment of 69 as a complete range. game-main's explicit 2.17%
ordinary weights independently round from `10 / 460`, although its live input
table remains intentionally partial. Runtime certification still fails: 23
families have no Combat target, present targets lack several required
protective/quest mechanics, and no stable assignment-family registry exists.
The same pass corrected the Stronghold Shade to 3.5 Slayer XP and one-quarter
ordinary combat/Constitution damage XP. No owner design question emerged.

The fourth master-pool harvest is recorded in
`source-audits/slayer-chaeldar-pool-2026-07-17.md`. It reconciles 34 ordinary
families and a provisional 388-point denominator: the cutoff master/cross table
supplies 32, while direct pre-cutoff pages restore Grifolapines and
Grifolaroos. Shadow warriors and Mutated zygomites are missing from Darkan's
executable pool and receive labeled 10-point common-baseline abstractions.
Cutoff history closes Elves at `60–90`, preserves Grotworms only as a
`72–109` observed-history envelope, restores Chaeldar's internally consistent
10/50/150 point schedule, and exposes wrong emulator gates for Elves, Fever
spiders, Fungal magi, Grifo families, and Vyrewatch. Runtime certification still
fails at 0/34: only three families have complete ordinary Combat candidates,
Banshee and generic Baby dragon are non-certifying, and 29 families are absent.
The same pass corrected the level-8 Crawling hand from 12 to 16 Slayer XP. No
owner design question emerged.

The fifth master-pool harvest is recorded in
`source-audits/slayer-sumona-pool-2026-07-17.md`. It reconciles Sumona's 37
ordinary families and a provisional 407-point denominator. Darkan supplies 35
executable rows totaling 387; cutoff evidence restores its commented
Scabarite and Terror-dog families with explicit 10-point common-baseline
abstractions. The cutoff master and quest pages close Combat 85, Slayer 35,
Smoking Kills, and the 12/60/180 point schedule. End-to-end readiness remains
0/37 because no family registry or assignment runtime exists, only four
ordinary families have complete Combat targets, and the remaining rows need
missing targets or complete protection, identity, interruption, and summon
behavior. The same pass removed incorrect Slayer XP from the temporary Death
spawn. No owner design question emerged.

The settled design keeps assignments and exact qualifying Combat variants
source-shaped, places `Assignment`, `Masters`, and `Rewards` in one Slayer page,
deep-links into Combat as the sole fight surface, and requires a reusable list
search/filter seam. It preserves quest-reactive masters, authentic task sizes,
mandatory finishers and protective consequences, points/streaks/challenges,
target-local Slayer contexts, ring-of-slaying trip value, and runtime-ready
family activation without dead rows or renormalized incomplete master pools.
Smoking Kills, Shilo Village, and the full black-mask/Slayer-helmet dependency
chains belong to the Slayer implementation program; Social Slayer remains
parked until genuine multiplayer state exists.

Summoning's owner grill is closed and its implementation is live in canonical
`main`. The governing ledger is `summoning-skill-contract-2026-07-16.md`,
backed by the catalog, lifecycle, training, Familiarisation, pet, potion,
Bogrog, familiar-effect, Winter Storage, simulation-time, reviewer-alert, and
Help audits/contracts. Foragers preserve the period distinction between
drop-to-player output and separate familiar storage: a full carried inventory suppresses
a drop roll with a visible log entry and no queue or Bank detour, while storage-type
familiars can continue to their sourced capacity of 30.
Familiar teleports are now resolved as target-local alternate route profiles with
route-assumption metadata. Spirit graahk's sourced 60-second Nature circuit replaces the
slower sourced route rather than stacking another discount; ordinary teleports do not
consume fresh pouches, and Void shifter reuses lethal-versus-sub-10%-LP retreat semantics
without an invented cooldown. Magic teleports and charged jewellery now share those
target-local route profiles while pure Magic teleport training remains available.

Pre-EOC Summoning pets are now restored as an atomic family. **Let out** and **Pick up**
operate through Bank/the canonical follower panel; Drop is not overloaded, while permanent
release is a separately confirmed destructive action. Pets share the global follower slot,
grow and become hungry only while active, and connect directly to Construction's parked
Menagerie function. Casual pet care automatically packs a source-derived compatible-food
reserve into real carried slots and feeds on answered-card ticks, preserving inventory cost
without Tamagotchi-style manual management. Cats retain staged quest and exceptional-
function identity. Stored hunger, growth, and stage persist but freeze; letting the pet out
reuses the ordinary Casual packing boundary and feeds from real carried food before the
first hunger advance. An unfed pet automatically returns home with `Out of pet food`;
starvation never silently destroys it.

Pet acquisition is distributed to the real source systems: shops/services, quests, Hunter,
egg sources and per-pet hatch flows, Construction, and activity reward shops. A searchable
Pets log explains and links those routes but never grants pets itself. Exact costs/rates/
timers remain source-harvest work. Discontinued event pets remain compatibility-only
outside the obtainable log and completion counts. Individual page review found no
supported unreclaimable-one-time-pet category; known pets have replacement routes, while
completed Ex-ex-parrot and Broav reacquisition remain `source_blocked`. Release never
claims `Cannot be reobtained` from source silence and cannot ship for a pet whose
reacquisition row is unresolved. Platypus release-for-reward is a distinct contextual
Hunter/quest action, while generic Release never grants a reward. Cat ratting is an
explicit source-shaped target rather than ambient output; Casual wily-cat retraining
automates but preserves its interaction-review cost, and Tooth creature auto-care never
silently selects the decayed adult. Source-timed pet growth that removes a capability now
uses the already-settled reviewer expiration-alert strip without pausing the transition.
Mature god-bird protection is recorded as a source-shaped, stage-gated faction flag but
remains numerically inert until a later dedicated multi-enemy/God Wars grill; no generic
defensive buff or ambient-damage abstraction is invented now. Unsafe player death follows
the period pet-loss rule: an active pet is destroyed, and an unprotected carried pet item
is not recoverable from a grave. Banked/Menagerie pets and safe-death contexts remain
safe. The anti-Tamagotchi abstraction is limited to passive hunger/attention upkeep.
Rat Catchers' King Rat stage follows the existing quest abstraction: one status line says
the cat fights through the wall, and the stage keeps the source-required cat item gate.
Optional food, cautious retreat, LP exchange, and cat death remain represented scene detail,
not a pet-combat actor, stance selector, hidden roll, or false mandatory food gate.

The 35 settled decisions now govern answered-card lifetime and passive world ticks,
separate familiar/point/special resources, target-policy automation, carried
pouch/scroll budgets, coalesced restore and Bank detours, safe replacement and
dismissal, source-gated familiar combat, BoB inventory/reclaim rules, forbidden
area consequences, Familiarisation's four-answer session, ordinary pouch/scroll
training, and scroll-use XP. Summoning also establishes one offline Help corpus
for contextual and full-reference surfaces. The ordinary skill surface ships;
explicit source/dependency blocks remain parked as recorded in its design-gap
and source-audit ledgers.

Pack Yak's Winter Storage trigger is settled at the full-pack boundary. Casual spends one
carried scroll and 12 special points to bank one configured eligible item only when doing
so prevents the next Bank trip, then continues the target action atomically. Advanced may
choose item priority and an earlier threshold. Any target rate must declare whether Winter
Storage is already assumed.

The implementation-gap grill settled Bunyip at one sourced 20-LP heal tick per
answered-card world tick, including Again. Familiar lifetime keeps its separate
ratio-preserving calibration; effect density follows Combat's per-exchange action loop.

The documentation archive closure is complete. The new `memory-bank/README.md`
separates current entry points from evidence and historical records; six
superseded/completed Markdown records plus the completion-audit JSON companion
now live under `memory-bank/archive/2026-07/`. Another 308 old status files are
grouped under `memory-bank/status-updates/archive/2026-05..07/`, leaving six
current orientation reports at the status root. The four resolved overnight
mechanics remain visible as `IMPLEMENT` cards rather than disappearing with
their question ledger. The closure report is
`status-updates/documentation-archive-results-2026-07-16.html`.

Documentation integrity is closed across the whole repository. The canonical
README, roadmap, Kanban, Project Brief, Product Context, Active Context, and
Progress ledger now agree with the live 17-complete / five-partial /
three-planned registry. Dated contracts, audits, briefs, and HTML results retain
their historical evidence with explicit shipped, merged, superseded, or
implementation-pending annotations. `tools/audit_docs.py` is the repeatable
mechanical gate for Markdown links/fences and HTML structure; it passes all 505
project documents including the closure report. The full core suite ran 1,327
methods with 1,131 ordinary passes, 193 environment skips, and three expected
failures. Test quality has zero hard issues across 67 files. Results are in
`status-updates/documentation-integrity-results-2026-07-16.html`.

Achievement semantics are complete on `main` at `a0f5da4`. The integrated
history includes the completed 18-pass overnight baseline and repairs all 70
action-worded achievements that were
reading disposable Bank balances. Config v37 adds owner-scoped cumulative
action/output progress, while explicit Hold/Own predicates remain live. Potion
holding thresholds are dose invariant, Runecrafting tiaras are excluded from
rune totals, and cross-skill production follows the explicit action surface.
The governing record is `achievement-semantics-contract-2026-07-16.md`; the
closure report is
`status-updates/achievement-semantics-results-2026-07-16.html`. All 1,323 core
core tests ran with 1,127 ordinary passes, 193 environment skips, and three
expected failures. The real offscreen Qt run had 1,320 ordinary passes and the
same three expected failures, with no skips. Test quality has zero hard issues;
compilation, diff, reachability, and worktree-safety gates pass.

The broader achievement-diary gear reward model remains deliberately open.
This repair supplies stable history for that future grill without choosing a
reward cadence, item order, upgrade flow, or retroactive grant policy.

This is a solo repository and the owner has explicitly selected a direct-main
workflow. Work, test, and commit in the canonical `main` checkout. Do not create
a feature branch or linked worktree unless the owner explicitly requests one
for a particular task. All seven previously linked worktrees were reconciled and
removed on 2026-07-16; the canonical add-on checkout is now the only worktree.

Agility's owner grill, source harvest, and atomic implementation are closed. The
governing product contract is
`agility-skill-contract-2026-07-15.md`, backed by the exhaustive design-family ledger
`source-audits/agility-complete-content-inventory-2026-07-15.md`. A
closed design family is not a closed historical value: candidate and
`source_blocked` rows still require the source-verification sweep named there. A
`source_blocked` value may trigger one final implementation-time search or the
smallest labeled review-native abstraction, but may never erase a period
feature. The complete design includes every audited course plus the previously
omitted Bandos route, Werewolf Skullball, Gnome Ball, Flash Powder Factory, The
Pit, Circus, incidental actions, the full ordinary/grapple shortcut registries,
cross-skill benefits, rewards/equipment/boosts, pending quest XP activation,
and target-specific run energy/actual-load weight.

Course failure consequences remain obstacle-specific rather than universal;
the contract now closes the fallback for unresolved hidden rolls at one global
20% entry chance decaying to a sourced mastery point or 5% at level 99. Existing
period consequences always override it. Brimhaven ships as the flattened hidden
5x5/eight-review chase in `agility-brimhaven-contract-2026-07-15.md`; Karamja
gloves 4 retain their sourced 25% chance to add a second ticket on a qualifying
tag. Wall-clock time and global player-location state remain forbidden
throughout. The implementation and verification record live in
`source-audits/agility-implementation-verification-2026-07-15.md`.

The cadence kernel is now live and default-on in the canonical dirty checkout.
`cadence_live.py` maps source-ready routes to exact rate-limited or
embedded-probability behavior, Combat to `6 × M` continuous encounter ticks,
and incompatible evidence to explicit `source_blocked` handler passthrough.
`cadence_coverage.py` classifies every implemented handler and selectable route,
including Quest, Utility, Farming, attached Summoning effects, and future
Slayer/Dungeoneering attachments. Explicit boolean false remains the
byte-identical legacy rollback.

Live Combat persists attack phase, enemy LP, prayer/curse state, status clocks,
special regeneration residual, and RNG phase between reviews. Again advances
world consumers but no combat beat, and terminal kill/death/flee/bank
boundaries never start a second enemy. Finite quest combat remains a deliberate
collapsed-stage exemption; rollback retains its legacy 50-tick burst.

The former Phase 1/Phase 3 files at commits `b45aff0` and `6422610` are
historical rollout evidence only. Shadow residuals are never promoted into live
`cadence_profiles`, and runtime shadow integration tests were removed after
replacement live coverage passed.

The test-signal cleanup is merged into `main` at `526f9c2`. It removed
low-signal structural tests, converted the previously uncollected pytest-style
JavaScript bridge checks to `unittest`, and added the durable quality contract
in `memory-bank/test-quality-standard.md`. The audit now collects 1,215 tests
across 65 files with zero hard issues; its five clone groups are advisory.

The Prayer/altar/urn/passive/Herblore closure is implemented, fully certified, and committed on `main` at `300c7c5`. It extends the original Prayer ship with owned gilded-altar parity, all 26 pre-EOC training-urn tiers across six skills, target-carried Bonecrusher/Ectoplasmator behavior, direct full-urn teleport with an independent bounded Anki undo stack, exact high-tier standard-Prayer Defence gates, and distinct Bonemeal/Wyvern bonemeal storage identities.

Use these as the live handoff sources:

1. `memory-bank/cadence-kernel-contract-2026-07-13.md` — canonical live cadence contract and taxonomy.
2. `memory-bank/codex-briefs/cadence-kernel-live-activation-2026-07-17.md` — activation acceptance criteria.
3. `memory-bank/future-work-kanban.md` — remaining source-rate and activity work.
4. `memory-bank/pre-eoc-source-verification-standard.md` — permanent evidence contract.
5. `memory-bank/cadence-kernel-phase3-shadow-2026-07-13.md` — historical Phase 3 evidence, not current runtime behavior.

The dated completion-audit files are archived under
`memory-bank/archive/2026-07/baselines/`; live registry and Kanban state outrank
them.

## Current Truth

- `skill_registry.py` has 18 complete skill surfaces, five partial Combat-trained skills, and two planned skills.
- Complete: Mining, Woodcutting, Farming, Fishing, Smithing, Crafting, Fletching, Firemaking, Cooking, Runecrafting, Hunter, Herblore, Prayer, Magic, Construction, Thieving, and Agility.
- Partial through unified Combat: Attack, Strength, Defence, Constitution, and Ranged.
- Planned: Dungeoneering and Slayer.
- Farming is shipped (`9a88c56`), not the next build.
- The 194-row quest catalog remains coverage scaffolding rather than full quest parity.
- NPC Shops are live; the fake GE remains parked until the item/acquisition universe is representative.
- The current reachability audit reports 1,200 actions and 273 orphan inputs
  (110 root, 163 cascade). Bob Barter's quantity-free decant
  routes turn the former four-dose potion roots into known-producer cascades;
  their remaining availability follows upstream herb and secondary acquisition.
  These are acquisition-program signals rather than Agility closure failures.

## Bob Barter Closure — 2026-07-15

- Bob Barter (herbs) is a free, instantaneous Grand Exchange shop service. One
  click redistributes every eligible live non-Daemonheim vial-potion family to
  the selected period-supported 2-, 3-, or 4-dose size. Total doses and vial
  containers are conserved: a partial remainder is retained, splitting consumes
  owned empty vials, and consolidation returns excess vials. The action changes
  no review or clock state and records an independently undoable shop event.
- Anki was loading three linked worktrees beside the canonical checkout because
  all four lived directly under `addons21` as enabled packages. The linked
  worktrees now live under the sibling `Anki2/ankiscape_worktrees/` root, and
  `tools/worktree_guard.py` audits that runtime boundary and creates future
  worktrees only in the safe location.
- The deck-browser entry point replaces its own nested callbacks by stable hook
  key through Anki's production `_hooks` storage, so repeated registration or a
  reload leaves exactly one callback and one menu open per click.
- Ordinary Herblore now excludes the 54 Daemonheim-only clean, unfinished, and finished targets while preserving their item identities for old saves. A removed saved selection migrates to `clean_guam` without deleting inventory.
- The live Herblore catalog is 22 clean, 22 unfinished, and 69 finished targets.
  All 113 rows now use local RS3-provenanced artwork. The skill rail uses the
  compact OSRS `Herblore icon (detail).png`, matching the source/style family of
  the other skill icons instead of the modern RS3 `Herblore detail.png` art.

- Live source-ready gathering routes advance exact lower-endpoint residuals;
  Cooking and Firemaking compare one already-drawn roll to the authentic source
  probability and draw no second random value.
- Source ranges remain ranges in evidence. Live admission uses the explicitly
  labeled conservative lower endpoint rather than inventing a midpoint.
- Historical shadow residuals remain readable but never seed or advance live
  `cadence_profiles`.
- Whole-addon coverage records every source-incompatible or missing route as
  `source_blocked` while preserving its approved handler action.
- Prayer selection is atomic across material and method. Hosted/owned altar state is cleared only when that composite selection changes.
- Owned gilded altars accept zero, one, or two burners at 250%, 300%, or 350%; clean marrentill is consumed once per new stint and the multiplier remains frozen for that stint.
- Training urns use exact five-state physical identities, non-stackable semantics, target-carried activation, overflow-preserving charge, ten-nonempty caps, and direct full-urn teleport.
- Saved custom layouts follow a physical urn through `(r)` to active to full, so skilling and Combat bank runs do not strand a charging urn.
- Direct teleport awards the urn skill's XP, refreshes the visible Skills panel, persists immediately, and uses a separate LIFO custom undo rather than review undo.
- Bonecrusher and Ectoplasmator operate only from the selected target's carried pack; Bonecrusher also intercepts Hunter bone outputs. No acquisition route was invented.
- Chivalry, Rigour, Augury, and Piety enforce their exact Defence requirements; Knight Waves locks are visible in the Qt copy.
- Ordinary Bonemeal (source ID 4255) and Wyvern bonemeal (source ID 6810) remain distinct despite sharing a source display name. Super prayer consumes only the disambiguated Wyvern storage key.
- Bonecrusher and Ectoplasmator icons now use explicit RS3 wiki provenance instead of the fallback OSRS-first resolver.

## Decision Boundaries

- Live cadence is default-on. Only explicit boolean false takes the
  byte/RNG-identical legacy path.
- Cadence residuals are integer-only per route. Inactive routes freeze, and the
  whole `cadence_profiles` mapping rides the existing review snapshot/undo path.
- `cadence_shadow` is historical instrumentation, separate from live
  `cadence_profiles`, and is never promoted into gameplay state.
- Missing or semantically incompatible rates always remain `source_blocked`.
  Do not substitute modern rates, midpoint a range, decompose the rocktail urn
  quote, map ordinary gold to concentrated gold, or map mixed leaping fish to a
  sturgeon-only rate.
- Full pre-EOC cutoff: `2012-11-20`.
- Do not re-grill Prayer, Magic, Construction, or Farming; their contracts are closed and implemented.
- Do not collapse source IDs 4255 and 6810 into one storage key. The earlier gap-ledger conclusion is superseded by the closure audit.
- Target-carried presence is the activation rule for urns and Prayer passives; bank ownership alone is inert.
- Review undo and direct-inventory-action undo are distinct contracts and must remain independent.
- Each wholly missing skill needs its own deep grill before implementation.
- Dungeoneering must define its temporary session inventory/equipment/reward boundary before any Daemonheim herbs or potions return to a player-facing catalog; see `dungeoneering-product-decision-deferred-2026-07-13.md`.
- Activities/minigames use Utility/Activities at the platform layer, but each family needs its own complete reward/state/source contract.
- Global level-1-to-99 balancing waits until all skills and major methods are present.

## Next Recommended Work

1. Resume the canonical Kanban rather than reopening Prayer, Thieving, or Agility: take the next owner-selected missing-skill program.
2. Close reachability roots only through authentic owning skills, activities, Combat drops, quests, shops, spawns, claims, and item actions.
3. When Darkan reaches a stable milestone, rerun parked hidden-server audits against that pinned source surface.

## Verification Contract

- Pure/data/unit/integration/end-to-end tests for behavior changes.
- Real offscreen `.venv-qt` tests for UI changes.
- Full `python3 run_tests.py` and full offscreen discovery before feature closure.
- `python3 tools/audit_item_reachability.py --json`, compilation, and `git diff --check` at closure.
- Manual real-profile QA remains an explicit owner checklist when a release candidate should touch the owner's Anki collection.
- Pre/post status artifacts for normal complex work.

## Thieving closure (2026-07-13)

Thieving is now a complete Support skill on `main`, merged at `63b0a28`. It ships the
full 2011Scape pickpocket and stall tables, exact inclusive integer rolls,
multi-pick, shared-LP damage plus one-review stun recovery, rational stall
cadence, wall safes, and the complete Menaphite lure/knockout/two-pick loop.
Fight-back starts an encounter-only Menaphite combat bridge; the default flee
path applies one sourced damage event through the shared auto-eat/death/grave
substrate. Wall safes use their distinct strict source roll and 20–60 LP trap;
all Thieving routes advance once per answered card regardless of the global
action multiplier. Desert Phoenix is a The Golem-gated, no-XP Utility activity
yielding Phoenix feather.

The owner resolved two implementation-time source questions: exact 2011Scape
respawn cadence wins rounded wiki rates, and player-visible period blackjack
values may use Darkan only for the missing hidden knockout roll/combat stats,
clearly labelled provisional. Dorgesh-Kaan chests, Lletya elf, Pirates' Hideout,
and incomplete blackjack variants remain source-blocked or parked. The durable
table record is `memory-bank/source-audits/thieving-tables-2026-07-13.md`.

Closure verification is green: Python 3.12 discovery and `run_tests.py` each
pass 1,240 tests with 188 non-Qt skips and three pre-existing expected failures;
the real Anki/Qt offscreen discovery passes all 1,240 tests with the same three
expected failures and no skips. The focused closure set passes 609 tests, item
reachability reports no Thieving/Phoenix orphan, compilation and diff checks are
clean, and the result artifact is
`memory-bank/status-updates/archive/2026-07/thieving-skill-results-2026-07-13.html`.

## Agility closure (2026-07-15)

Agility is now a complete Support skill. It ships the full course/action-stage
engine, obstacle-specific failure/LP/setback behavior, lap bonuses, every audited
activity family, Brimhaven's review-native ticket chase, 68 ordinary/grapple
shortcuts, run-energy trip costs with actual carried weight, equipment and boost
effects, achievements, command undo, a grouped Qt surface, and period-provenanced
assets. Circus and every other cadence boundary derive from answered cards or
Agility actions; a static regression guard rejects wall-clock imports from the
gameplay modules.

The release-blocking live integrations are active: barehand Hunter butterflies,
Fishing double catches, Herblore consumable effects, Habitat traversal, quest and
lamp rewards, Farming east-patch travel, LP/death, inventory, equipment, storage,
and runtime dispatch. Future-owner hooks remain explicit but inert for Summoning,
Slayer, Dungeoneering, full Blast Furnace, Livid Farm, diary acquisition,
Barbarian Assault, and quest-owned stages. Exact Dorgesh route identities are
registered; still-hidden payout differences remain `source_blocked` rather than
invented. See
`memory-bank/source-audits/agility-implementation-verification-2026-07-15.md`.

## Overnight fresh-eyes pass 3 (2026-07-16)

The safe worktree branch `codex/overnight-fresh-eyes-2026-07-16` now includes
the exact lantern-state closure at `37b46c5`. Bullseye, candle, oil-lamp,
oil-lantern, sapphire, emerald, and Mining helmet states remain distinct from
production through preparation, use, equipment, shops, quests, assets, and
save migration. Lamp-oil preparation is review-native and never wall-clock
driven. Verification passes 1,265 Python tests, 179 real offscreen Qt tests,
the zero-hard-issue test-quality audit, compilation, diff checks, and the safe
worktree audit; reachability improves by 14 cascade orphans.

The next confirmed implementation seam is the generated quest pseudo-item
`Light sources`, present in three exact quest gates. Fable is at the owner's
30% weekly cap; remaining overnight reviews use Opus after the Claude session
window resets.

## Overnight fresh-eyes pass 4 (2026-07-16)

Commit `83de7e1` removes the `Light source`/`Light sources` pseudo-item from the
live quest and Dorgesh-Kaan Agility surfaces. Eight source-placed quest gates
now accept the eleven reachable exact lit states; Tears of Guthix retains its
safe bullseye and sapphire-lantern sequence, while Watchtower and Another Slice
of H.A.M. remain honestly `source_blocked` instead of receiving guessed gates.
Temple of Ikov's visible requirements and the test oracles now describe the
same real identities as runtime.

Verification passes 253 focused tests and all 1,270 tests under the established
Homebrew Python, with 183 non-Qt skips and three expected XP-parity failures.
Test quality has zero hard issues; reachability remains 1,114 actions, 264
orphan inputs, and 149 cascade orphans. Fable remains at the 30% weekly cap;
the successful reviewer was one read-only Opus workflow.

The next confirmed seam is save migration symmetry: legacy lantern/Mining
helmet keys must be migrated in carried layouts and views, grave/Death's Office
items and loadouts, and loot overrides before carried-state clamping.

## Overnight fresh-eyes pass 5 (2026-07-16)

Commit `3953b64` closes persisted item-name symmetry for the exact lantern and
Mining helmet split. Migration now renames carried views/layouts, loot
preferences, grave and Death's Office items/loadouts, and the Magic alchemy
selector before any carried-state clamp can discard the old name. Reclaiming a
legacy Mining helmet restores `Mining helmet (unlit)` as real equipment instead
of occupying the head slot with an unregistered zero-stat phantom.

Verification passes 312 focused storage/combat/Magic/shop/integration tests and
all 1,272 tests, with 183 non-Qt skips and three expected XP-parity failures.
Test quality remains at zero hard issues, compilation and diff checks pass, and
the safe worktree audit remains clean. There is no queued confirmed defect;
the next pass rotates to quest, shop, activity, and achievement seams.

## Overnight fresh-eyes pass 8 (2026-07-16)

Commit `5ab5aee` repairs three registry and audit seams. Smithing achievements
now consume the canonical live bar identities; source item 4600 is consistently
the obtainable and equippable `Willow blackjack`; and the acquisition graph now
models Magic and Prayer outputs, rune costs, and dynamic bone alternatives.
This removes false elemental-orb and Wine-of-zamorak roots while surfacing real
downstream Prayer and Onyx acquisition debt that was previously invisible.

Verification passes 78 focused tests, 509 integration/end-to-end tests, eight
real offscreen Qt tests, and all 1,275 non-Qt tests with 185 skips and the three
expected XP-parity failures. The test-quality audit has zero hard issues;
compilation, diff, and worktree-safety checks pass. Reachability now covers
1,188 actions, with 270 orphan inputs: 110 root and 160 cascade.

## Overnight fresh-eyes pass 9 (2026-07-16)

Commit `ceaab20` closes two quest writer/reader failures. Live quest data now
always retains a completion sentinel after the highest requirement row, so the
final sourced objective executes for all 152 affected generated quests instead
of being marked complete without evaluation. Tears of Guthix now reaches and
enforces its lit sapphire-lantern stage. Seven obtainable quest equipment items
also receive their source-config equipment records, while Staff of armadyl is
correctly retained as a non-equipment quest material.

Verification passes 127 registry/shop/quest tests, 104 quest/runtime tests,
four real offscreen Qt checks, and all 1,280 non-Qt tests with 185 skips and the
three expected XP-parity failures. Test quality has zero hard issues;
reachability remains 1,188 actions and 270 orphan inputs (110 root, 160
cascade); compilation, diff, and safe-worktree checks pass.

## Overnight fresh-eyes pass 10 (2026-07-16)

Commit `916b075` closes six Combat state and consequence failures. Loaded Ranged
ammo now wins over banked lower tiers; Vengeance and Spellbook Swap use the
finite rune loadout and persist the state that crosses reviews; reflected kills
receive ordinary kill/drop treatment; Dream cannot interrupt an active fight;
same-review fatal loot enters the grave after filtering; and Protect Item keeps
the highest-value equipped item.

Verification passes 334 focused combat/runtime/integration tests, eight real
offscreen Qt checks, and all 1,286 tests under Homebrew Python with 185 skips
and the three expected XP-parity failures. Test quality has zero hard issues;
reachability remains 1,188 actions and 270 orphan inputs (110 root, 160
cascade); compilation, diff, and safe-worktree checks pass. The system Python
is 3.9 and cannot parse the repository's supported union-type syntax, so the
authoritative full run used the established Homebrew Python 3.14 interpreter.

## Overnight fresh-eyes pass 11 (2026-07-16)

Commit `9273cf4` closes ranged item identity seams across every live producer.
Standard arrows from H.A.M. pickpockets, Combat drops, and NPC shops now enter
the canonical plural ammunition stacks accepted by equipment and combat. Save
migration merges legacy singular stacks, including persisted shop events and
their inverse deltas, without losing quantities or breaking undo.

The checked-in equipment snapshot was also regenerated from its current source
generator. Twenty-nine live Crafting and Fletching outputs that were previously
craftable but rejected by the equipment engine are now equippable, and a new
generator/snapshot synchronization oracle prevents recurrence.

Verification passes 263 focused tests, five real offscreen Qt checks, and all
1,291 tests with 185 skips and three expected XP-parity failures. Test quality
has zero hard issues; reachability remains 1,188 actions and 270 orphan inputs
(110 root, 160 cascade); compilation, diff, and safe-worktree checks pass.

## Overnight fresh-eyes pass 12 (2026-07-16)

Commit `f794108` closes consumable and supply-pack state paths. Kebab now uses
live RNG with deterministic undo; all eight supply packs support exact Open and
Open all actions; Juju farming potion doses can be activated and conserved;
Magic essence potion creation emits the source-convergent mix identity; and
registry tradeability, food categories, potion-dose identities, assets, and
Bank verbs now agree with their runtime consumers.

Verification passes 19 focused tests, five real offscreen Qt checks, and all
1,302 tests with 186 skips and three expected XP-parity failures. Test quality
has zero hard issues; reachability now covers 1,200 actions with 273 orphan
inputs (110 root, 163 cascade); compilation, diff, and safe-worktree checks
pass.

## Overnight fresh-eyes pass 13 (2026-07-16)

Commit `1fb0b64` makes Combat presets configuration-only. The finite supply
loadout is no longer captured by new presets or restored from legacy preset
payloads, so a target pin cannot refill consumed food, ammunition, runes, or
potions for free or erase a newly loaded pack on the following review.

Verification passes 271 focused runtime/integration tests, two real offscreen
Qt checks, and all 1,303 tests with 186 skips and three expected XP-parity
failures. Test quality has zero hard issues; reachability remains 1,200 actions
and 273 orphan inputs (110 root, 163 cascade); compilation, diff, and
safe-worktree checks pass.

## Overnight fresh-eyes pass 14 (2026-07-16)

Commit `b59c846` makes achievement dispatch dependency-aware. When the final
ordinary achievement and Living Legend become true on the same action, the
dispatcher now evaluates to a fixed point and returns both completions
atomically rather than making Living Legend wait for another unrelated action.

Verification passes 251 focused pure/integration tests, one real offscreen Qt
achievement-surface check, and all 1,304 tests with 186 skips and three
expected XP-parity failures. Test quality has zero hard issues; compilation,
diff, and safe-worktree checks pass.

## Overnight fresh-eyes pass 15 (2026-07-16)

Commit `1120fb4` closes two production paths that green lower-level tests did
not exercise. Every Shop purchase, sale, service, vendor action, Bob Barter
decant, and Wilderness consequence now persists through `save_player_data`
immediately. The Farming sheet also exposes the accepted Juju farming potion
action, uses the fullest owned dose first, and displays its review-native active
state instead of leaving the backend-only action unreachable.

Verification passes 242 focused Farming/Shop/runtime/integration tests, all 183
real offscreen Qt tests, and all 1,305 core tests with 187 skips and three
expected XP-parity failures. Test quality has zero hard issues; compilation,
diff, and safe-worktree checks pass.

## Overnight fresh-eyes pass 16 (2026-07-16)

Commit `483eb55` closes reactive UI and target-resolution gaps across the six
newest skill surfaces. The HUD resolves their friendly target names; equipped
blackjacks satisfy Thieving gates; Magic, Construction, Thieving, and Agility
controls rerender their dependent readiness state; every sourced Brimhaven XP
bundle is selectable; Agility commands report outcomes; and paid Brimhaven
stints end on target change or Stop Training.

Verification passes 170 focused core tests, eight real offscreen Qt checks,
and all 1,312 core tests with 193 skips and three expected XP-parity failures.
Test quality has zero hard issues; compilation, diff, and safe-worktree checks
pass.

## Overnight fresh-eyes pass 17 (2026-07-16)

Commit `111b280` closes consequence-ordering and undo gaps on management
actions. XP-lamp claims update the funded skill's level before achievements,
quest-bank and Stronghold rewards participate in direct-action undo, and Shop
mutations reevaluate inventory achievements before saving.

Verification passes 109 focused core tests and nine real offscreen Qt Shop
checks. Test quality has zero hard issues; compilation, diff, and safe-worktree
checks pass. Full closure verification remains pending.

## Overnight fresh-eyes pass 18 (2026-07-16)

Commit `91f0b35` closes the remaining reproduced Combat-management consequence
gaps. Clearing the finite loadout immediately repaints returned bank items, and
both unload and Death's Office reclaim evaluate inventory achievements before
saving. The reviewer-proposed manual Refill button was rejected because the
current UI contract deliberately uses automatic safe-boundary refill.

Verification passes 252 focused core tests and the combat-filtered real
offscreen Qt surface. Test quality has zero hard issues; compilation, diff, and
safe-worktree checks pass. Full closure verification remains pending.

## Overnight fresh-eyes audit closed (2026-07-16)

The dedicated branch completed 18 bounded maker/checker passes and 36
attributable commits without touching main or another worktree; it was later
integrated through `2ac9ed5`. Final closure ran 1,314 core methods and 1,314 real
offscreen Qt methods; each run contained the same three declared XP-parity
expected failures, while the core run also contained environment skips. Test
quality had zero hard issues, reachability remained 1,200 actions / 273 known
orphans, and compilation, diff, and worktree safety checks passed. There were
no queued confirmed defects. The four owner-direction questions recorded in
`memory-bank/archive/2026-07/resolved-queues/design-gaps-overnight-2026-07-16.md`
are now design-resolved. Their four pending implementations are explicit
`IMPLEMENT` cards in `memory-bank/future-work-kanban.md`.

## Slayer Duradel/Lapalok source harvest (2026-07-17)

The sixth functional Slayer-master pool is source-reconciled but remains
runtime-hidden. Duradel/Lapalok have 35 ordinary families and a provisional
334-point calibration denominator: 34 Darkan rows total 324, with
period-proven Scabarites restored at an explicit 10-point common-master
abstraction. Combat 100, Slayer 50, Shilo Village access, the 15/75/225 point
schedule, While Guthix Sleeps succession, and the 69-kill Slayer Tower
challenge are pinned in
`source-audits/slayer-duradel-lapalok-pool-2026-07-17.md`.

End-to-end readiness is 0/35. Only Black demon, Greater demon and Hellhound are
complete ordinary candidates; the family registry, assignment/task-credit
runtime, most targets, special mechanics, quests, succession and challenge
ledger remain absent. This pass also repaired exact Abyssal-demon quantity
distributions, its missing global Rare-table branch, and the accidental
generic exposure of Kuradal's Dungeon-only Ferocious ring. Summoning and
Dungeoneering remain explicitly excluded.

## Slayer Kuradal source harvest (2026-07-17)

The seventh and final functional Slayer-master pool is source-reconciled but
remains runtime-hidden. Kuradal has 36 ordinary families and a provisional
322-point calibration denominator: Darkan's 35 rows total 312, its Volcanic
creatures row maps to ordinary TzHaar, and period-proven Terror dogs return at
an explicit 10-point common-master abstraction. Combat 110, Slayer 75, Ancient
Cavern access, 18/90/270 points, the two reward-gated families, Kuradal's
Dungeon, Ferocious-ring consequences, and the 280-kill Fight Cave challenge
are pinned in `source-audits/slayer-kuradal-pool-2026-07-17.md`.

End-to-end readiness is 0/36. Four ordinary families are complete Combat
candidates after restoring the level-149 TzHaar-Ket's missing 136 Slayer XP;
the family registry, assignment/task-credit runtime, 29 families, special
mechanics, reward gates, contexts and Fight Cave remain absent. All seven
functional master pools are now recorded. Summoning and Dungeoneering remain
explicitly excluded from that Slayer harvest; Summoning was implemented later
in the day.

## Slayer Cockatrice and Banshee protection slices (2026-07-17)

Cockatrice now preserves the cutoff Mirror-shield consequence instead of
behaving like an ordinary harmless melee target. Missing the equipped shield
causes an automatically landed fixed hit using the labeled
maximum-LP/6-with-110-cap reconciliation and drains Attack, Strength, Defence,
Ranged, and Agility by one quarter of base per attack down to the period-proven
one-quarter floor. The ordinary Combat food, retreat, death, grave, persistence,
and review-undo paths remain authoritative.

The existing Combat picker warns without hard-blocking either legal dangerous
encounter. Cockatrice clears only for a Mirror shield in the shield slot.
Banshee clears only for Earmuffs, masked earmuffs, or a Slayer-helmet-family
item in the head slot. Its fixed maximum-LP/10 scream caps at 80 LP and drains
the period-proven eight skills by five levels per attack to level 1. The
flat-five magnitude is explicitly an owner-authorized bounded abstraction from
Darkan; the source conflict remains visible in
`source-audits/slayer-protective-equipment-cockatrice-banshee-2026-07-17.md`.

The Banshee extension passes 236 focused Combat/roster/metadata tests, one real
offscreen Qt Combat-picker check, and all 1,485 current core methods with 203
environment skips. Test quality remains at zero hard issues and the pre-existing
four structural-clone candidates; documentation, compilation, diff and
worktree-safety checks pass.

## Slayer finisher runtime and live families (2026-07-17)

The four cutoff finisher supplies now preserve their source identity and
inventory shape through the generated shop catalog and shared item registry.
Bag of salt and Ice cooler are stackable consumables; Rock hammer and
Fungicide spray 10 are non-stackable tools. The repair is commit `2ddbb0a`.

Desert lizard ships with the generic manual/quick-finisher runtime, a reconciled
Combat/drop row, source level gate, contextual Waterskin supply cost, and
proven enemy asset. Rockslug and Gargoyle now reuse that engine with their own
reconciled rows, period mechanics, and assets. Manual completion costs its own
correct review; the 400-point flag folds the same required item and kill into
lethal damage. Mutated zygomite is the remaining ordinary finisher family
without a reconciled live target.
Details are in `source-audits/slayer-finishing-blows-2026-07-15.md` and
`source-audits/slayer-rockslug-gargoyle-combat-2026-07-17.md`.

Final verification passes all 1,497 core methods (1,293 ordinary passes and
204 expected environment skips) and all 1,497 real offscreen Qt methods with
no skips, expected failures, or failures. Test quality remains at zero hard
issues and the same four review-only structural clone groups. Documentation,
compilation, diff, item reachability, and worktree-safety audits pass.

## Grill-harvest closure (2026-07-17)

The approved amendment queue and bounded Slayer source-harvest program are
closed. Slayer itself is not shipped: all seven functional master pools are
recorded, but authentic assignment runtime remains blocked by incomplete
Combat families, quests, contexts, rewards, challenges, and special mechanics.
Do not expose a partial master or renormalize its weights.

Final verification ran 1,376 core methods (1,177 ordinary passes, 196
environment skips, three expected XP-parity failures) and 1,376 real offscreen
Qt methods (1,373 ordinary passes, no skips, the same three expected failures).
Docs, test quality, compilation, JSON, diff, reachability, and worktree safety
all pass. The next Slayer pass should begin from the stable blocker identities
in the seven master audits, not reopen the owner contract or fabricate a
partial assignment pool. The closure report is
`status-updates/grill-harvest-results-2026-07-17.html`.

## Slayer Wall beast Combat slice (2026-07-18)

The ordinary level-49 Wall beast is now an executable Mazchna-family Combat
target. A real Spiny helmet is required only to start the fight: a player may
swap headgear after discovery and continue the active encounter, but killing
that beast while unhelmeted cannot chain into another spawn during the same
review. This is a distinct `start_equipment` contract, not the per-enemy-attack
damage/drain behavior used by Banshee and Cockatrice.

The target carries the cutoff level, 1,050 LP, Slayer 35, 105 Slayer XP,
44-LP maximum hit, poison immunity, and assignment identity; Darkan contributes
exact combat stats, 39-tick respawn, and the thirty-row drop distribution.
Ancient Smoke spells therefore deal their ordinary hit without their extra
poison damage. The drop distribution is normalized losslessly to 100,000 slots
with ten empty slots, and every item maps to an existing canonical registry
identity. The pre-cutoff Wall beast icon is installed with provenance.

Mazchna/Achtryn readiness is now 24/27. Only Cyclopes, Mogres, and Vampyres
remain. No owner design gap emerged. Durable evidence is
`source-audits/slayer-wall-beast-combat-2026-07-18.md`; the visual closure
report is `status-updates/slayer-wall-beast-combat-results-2026-07-18.html`
(<https://0aaltfsrmyrn.postplan.dev>).

The next Mazchna blocker, Mogres, is now source-closed but correctly remains
dependency-blocked. Cutoff evidence pins the level-60 target, atomic
Fishing-explosive lure, Slayer 32/48 XP, poison immunity, six-tick melee,
89-LP maximum hit, the exact three-stage Skippy supply chain, and the unlock.
Darkan supplies matching combat stats, a 59-tick respawn, an exact 128-slot
main drop table, and the shared long/curved-bone tertiary table. The existing
Slayer family already requires completion ID `skippy_and_the_mogres`, but that
miniquest is absent from the quest catalog. Adding a permanently locked target
would falsely advance readiness, so the quest-owned chain is handed to the
Darkan quest thread and no runtime row ships yet. No owner design gap emerged.
Durable evidence is
`source-audits/slayer-mogre-combat-2026-07-18.md`.

## Slayer Feral vampyre Combat slice (2026-07-18)

The ordinary level-61 Feral vampyre is now an executable Mazchna/Vannaka-family
Combat target. Priest in Peril gates Morytania access. The target carries the
cutoff 400 LP, 40 Slayer XP, six-tick melee, 74-LP maximum hit, guaranteed
Vampyre dust, all-weapon vulnerability, poison susceptibility, and assignment
identity; Darkan contributes exact combat stats, a 59-tick respawn, and 41
ordinary probability rows.

The Darkan rows are normalized losslessly to 100,000 mutually exclusive slots
with 167 empty slots, and every output reuses a canonical item identity. The
pre-cutoff level-61 sprite is installed from the historical file revision with
provenance.

Two period-authentic but numerically incomplete effects use explicit bounded
abstractions. A worn Holy symbol reduces enemy accuracy and maximum hit by 20%,
visible in Combat preview. A landed damaging attack has a 1/8 bite chance,
heals up to 20 LP without exceeding damage dealt, and drains one random
implemented skill by one current level. Runtime messaging distinguishes bite
healing from passive regeneration.

Mazchna/Achtryn readiness is now 25/27. Mogres remain dependency-blocked by the
quest-owned Skippy miniquest; Cyclopes remain dependency-blocked by the complete
Warriors' Guild token/defender activity. No owner design gap emerged. Durable
evidence is
`source-audits/slayer-feral-vampyre-combat-2026-07-18.md`.
The visual closure report is
`status-updates/slayer-feral-vampyre-results-2026-07-18.html`
(<https://v0w3h4u00jo4.postplan.dev>).

## Slayer Aberrant spectre Combat slice (2026-07-18)

The ordinary level-96 Aberrant spectre is now an executable Vannaka-family
Combat target behind the existing Priest in Peril gate. It carries the cutoff
900 LP, Slayer 60/90 XP, six-tick Magic attack, 119-LP protected maximum,
Nose-peg/Slayer-helmet protection, and 160-LP unprotected maximum. Darkan
supplies exact combat stats, respawn, stench mechanics, ten independent
ordinary rows represented by the executable `DropList` semantics as one
512-slot selector, four nested special tables, and an exact derived charm
selector.

The live stench rule preserves the unusual prayer split: Protect from Magic
blocks the random five-level combat-stat drain but does not block max-LP/10
damage. The new field is data-declared and leaves Basilisk's inverse behavior
unchanged. Mystic robe bottom (dark) is generated as real legs equipment with
its source item, bonuses, requirements, and sprite. Regeneration also repaired
the previously latent Adamant spear and Black dagger (p) Shadow-warrior
equipment rows.

Vannaka readiness is now 25/35. Nine Combat representatives and Earth
warrior's Wilderness-risk behavior remain. No quest files were edited and no
owner design gap emerged. Durable evidence is
`source-audits/slayer-aberrant-spectre-combat-2026-07-18.md`.
The visual closure report is
`status-updates/slayer-aberrant-spectre-results-2026-07-18.html`
(<https://fr3fmom6akth.postplan.dev>).
