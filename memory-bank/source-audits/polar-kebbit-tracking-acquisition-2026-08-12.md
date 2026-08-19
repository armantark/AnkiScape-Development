# Polar kebbit tracking acquisition audit — 2026-08-12

Status: **implemented with one registered hidden-rate placeholder**.
Cutoff: `2012-11-20T00:00:00Z`.

## Defect and scope

The Big Chinchompa Polar kebbit quota ticket named `catch_polar_kebbit`, but
Hunter did not register that target. The ticket could therefore be bought and
packed but could not point at a performable activity. This slice adds only the
missing ordinary Polar kebbit tracking route and reuses the existing private-
ground, Hunter, cadence, carried-pack, telemetry, persistence, and undo paths.

## Period-visible contract

RuneScape Wiki `Hunter`, oldid `6484443`, timestamp
`2012-10-27T06:44:39Z`, supplies the visible mechanic.

In section **Tracking**, it states that tracking uses a noosing wand, a trail
contains “4-5 successful searches” before the final attack, and catching a
kebbit gives Bones, raw beast meat, and kebbit fur. The tracking table states
that Polar kebbit requires Hunter level 1, awards 30 Hunter XP, and gives fur
for Polar camouflage gear.

In section **Hunter locations → Training areas → Snow**, the page places Polar
kebbits in the Rellekka Hunter area north of Rellekka and lists multiple ordinary
routes: fairy ring `DKS`, walking from Rellekka, and Rellekka teleports. It does
not state a quest requirement. The page has no `{{beta}}` marker; its obsolete
and script-error categories do not change the literal period table or route
prose cited here.

Source: <https://runescape.wiki/w/Hunter?oldid=6484443>.

One answered review represents the complete four- or five-search trail and
final attack. This is the established Hunter action abstraction, not a claim
that the period game completed tracking in one click.

## Executable corroboration and hidden roll

Darkan path
`src/main/java/com/rs/game/content/skills/hunter/tracking/Track.java`, supplied
by commit `37957d17d62d6b14d326cd719a0ae0c239c76cf9`, contains Polar kebbit at
level 1, 30 XP, and reward item `10117`.

Darkan path
`src/main/java/com/rs/game/content/skills/hunter/tracking/Tracking.java` was
introduced by that commit; its current path tip is
`c2535866140b8c6e6f6e2ce94d8ef6c367fd0548`. It requires Noose wand `10150`
and awards one Bones `526`, one Raw beast meat `9986`, and one target reward.
Darkan's restored route is deterministic, so it corroborates the visible
contract but does not settle the period catch/failure probability. Files under
`src/main/java/com/rs/web/*AuditProbe.kt` were excluded unconditionally.

The live row therefore registers `hunter.polar_kebbit_success_curve`: the
shared Hunter fallback `rate1=128`, `rate99=256`. At level 1, the source-roll
adapter computes integer chance 129 and probability `130/255` before the
established review normalization. A period tracking routine or qualified
measured table would retire this value.

## Item identities and art

OpenRS2 rev-742 (`2012-11-07`) pins:

- item `10117`, Polar kebbit fur;
- item `10150`, Noose wand, with `Wield` and `Add-to-toolbelt` actions;
- item `9986`, Raw beast meat; and
- item `526`, Bones.

Rev-727 finds the same identities as a positive control, but it is Darkan's
cache base and is not independent corroboration of Darkan server behavior.
The local game-main checkout contains no Hunter tracking implementation; it
corroborates item/shop identities only and supplies no roll, timer, or quantity.

The route reuses `shopitems/polar_kebbit_fur.png`, a normalized period asset
with timestamp `2009-06-12T02:55:29Z` and SHA-1
`d297733bcc01b7e49c2480a807fe7d3913119d1d` in
`assets_provenance.json`.

## Route-wall disposition

No route wall was invented. Unlike Arctic pine, the period source states no
quest gate. Unlike a single inaccessible region dependency, it explicitly
lists several ordinary ways to reach the Rellekka Hunter area. The existing
Hunter target and generic quest-lock abstractions can represent a real gate,
but there is no Polar-kebbit gate to encode.

## Verification boundary

The ordinary acquisition regression starts from default level-one player state,
earns coins through the real level-one Thieving kernel, buys a Noose wand
through the real shop kernel, and catches a Polar kebbit through the real Hunter
kernel. This proves that the new tracking target is genuinely early-game
reachable without a quota ticket or injected private-ground state.

A separate Hunter-level-70 regression starts from a valid level-70 skill state,
spends 15 Competence points through the Big Chinchompa reward kernel, configures
the purchased `polar_kebbit_ticket` through the real carried-layout API, enables
private ground, and catches through the carried-overlay and Hunter kernels. It
proves that the actual ticket defect is closed end to end and that the ticket is
consumed only after success. Focused pure and registry checks pin the target,
reusable tool, outputs, source chance, item identity, and Big Chinchompa target
resolution. The reachability audit attributes Polar kebbit fur to
`Hunter:catch_polar_kebbit`.
