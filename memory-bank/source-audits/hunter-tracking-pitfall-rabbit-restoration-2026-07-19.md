# Hunter tracking, pitfall, and rabbit restoration audit — 2026-07-19

Status: **source-blocked after Darkan restoration reconciliation; no Hunter
targets activated**.  
Cutoff: `2012-11-20T00:00:00Z`.

## Scope and disposition

This pass reopens the source dependency, not the owner design, for the settled
non-Jadinko Hunter card:

- Polar kebbit, Common kebbit, Feldip weasel, Desert devil, Penguin, and
  Razor-backed kebbit tracking;
- Spined larupia, Horned graahk, and Sabre-toothed kyatt pitfall trapping;
- White-rabbit snaring;
- Jim's KGP-agent hand-in;
- tracking- and pitfall-fur clothing;
- Rabbit-foot stringing and its Woodcutting effect; and
- Long kebbit bolt creation.

The July 2026 Darkan restoration now supplies executable ceilings for five
tracking targets, all three pitfalls, and White rabbit. It does **not** supply
the hidden behavior the owner contract requires before activation. The
restoration is deterministic where the period record says a trap can fail,
omits Penguin tracking, omits pitfall damage, emits only tatty pitfall fur, and
preserves neither Rabbit-snare disappearance nor Ferret loss.

No partial target is activated. Doing so would collapse explicitly required
rolls into invented deterministic catches and would make the source dependency
look closed when it is not.

## Direct period evidence

RuneScape Wiki `Hunter`, oldid `6484443`, timestamp
`2012-10-27T06:44:39Z`, establishes the following literal values and behavior.

### Tracking

| Target | Level | Hunter XP | Guaranteed target reward |
|---|---:|---:|---|
| Polar kebbit | 1 | 30 | Polar kebbit fur |
| Common kebbit | 3 | 36 | Common kebbit fur |
| Feldip weasel | 7 | 48 | Feldip weasel fur |
| Desert devil | 13 | 66 | Desert devil fur |
| Penguin | 45 | 250 | Penguin result |
| Razor-backed kebbit | 49 | 348 | Long kebbit spike |

Tracking requires a Noose wand. One trail may contain four or five successful
searches before the final attack, and a successful kebbit catch also gives
Bones and Raw beast meat. The AnkiScape contract already collapses that visible
trail into one internally simulated review transaction; this audit does not
change that decision.

The page does not state a catch/failure probability or an intermediate trail
failure selector. Those hidden rolls remain `source_blocked`.

### Rabbit snaring

White rabbit requires Hunter 27, a Ferret, and a Rabbit snare; a catch awards
144 Hunter XP, Bones, Raw rabbit, and a Rabbit foot. Eagles' Peak is not a
direct snaring gate: it gates obtaining the Ferret used to flush the rabbit.

The page explicitly says Rabbit snares disappear rapidly and a Ferret can be
reused several times until it runs away. It supplies neither disappearance
probability nor Ferret-loss probability. Both remain `source_blocked`.

Stringing a Rabbit foot awards 4 Crafting XP. Wearing the resulting Strung
rabbit foot gives a small increase in the chance of a Woodcutting bird's-nest
drop. The magnitude of that increase is not stated and remains
`source_blocked`.

### Pitfalls

| Target | Level | Hunter XP |
|---|---:|---:|
| Spined larupia | 31 | 180 |
| Horned graahk | 41 | 240 |
| Sabre-toothed kyatt | 55 | 300 |

Pitfalls require Logs, a Knife, and a Teasing stick. The creature often jumps
over the pit and attacks the player, pitfall creatures can deal damage, the
trap collapses, and one creature will not jump the same pit twice in a row.
Fur may be tatty or perfect; perfect fur is obtained approximately one-fourth
of the time.

The period record therefore closes the reward-quality shape and the bounded
`1/4` perfect-fur probability. It does not close the catch/failure probability,
the hit/damage selector, or an exact damage amount. Those values remain
`source_blocked`.

### Direct reward chains

The same Hunter revision states that one Long kebbit spike can be turned into
six Long kebbit bolts, either through Leon for 40 coins or with a Chisel.
The executable Darkan Fletching row independently preserves Long kebbit bolts
at level 42 and `1.33` Fletching XP per bolt. The transformation is source-ready
in isolation, but it has no live acquisition route until Razor-backed kebbit
tracking can ship.

Source:
<https://runescape.wiki/w/Hunter?oldid=6484443>.

## Penguin and Jim

RuneScape Wiki `Penguin (Hunter)`, oldid `6099750`, timestamp
`2012-08-17T02:00:17Z`, establishes:

- Hunt for Red Raktuber completion gates the Penguin Hunting Area;
- tracking is available at Hunter 45 for 250 XP;
- the result can be either an ordinary Penguin or a KGP agent;
- only a KGP agent can be handed to Jim; and
- releasing a KGP agent gives 2 Hunter XP.

`Jim`, oldid `6529009`, timestamp `2012-11-03T14:43:10Z`, independently
confirms the quest gate and that Jim exchanges each KGP agent for **2 extra
Hunter XP**.

Neither page states the ordinary-Penguin versus KGP-agent probability. That
selector remains `source_blocked`.

Sources:

- <https://runescape.wiki/w/Penguin_%28Hunter%29?oldid=6099750>
- <https://runescape.wiki/w/Jim?oldid=6529009>

No pre-cutoff `Talk:Penguin (Hunter)` revision exists in the current history.
`Talk:Hunter`, oldid `5319217`, timestamp `2012-03-03T17:56:38Z`, contains no
numeric tracking, pitfall, rabbit, or Penguin selector. Targeted pre-cutoff talk
history for Polar kebbit likewise supplies no missing rate.

## Darkan restoration ceiling

The July 2026 Darkan restoration is useful executable reconstruction evidence,
but its own bounded implementation leaves the required selectors unresolved.

### Tracking

Commit `37957d17d62d6b14d326cd719a0ae0c239c76cf9` restores
`Track.java` and `Tracking.java` with five deterministic rows:

- Polar kebbit: level 1, 30 XP;
- Common kebbit: level 3, 36 XP;
- Feldip weasel: level 7, 48 XP;
- Desert devil: level 13, 66 XP; and
- Razor-backed kebbit: level 49, 348.5 XP.

The action requires a Noose wand and three free inventory spaces, follows a
route, then always produces Bones, Raw beast meat, and the target reward. It
contains no catch/failure selector and omits Penguin tracking entirely. The
`348.5` reconstruction also conflicts with the direct cutoff table's `348`, so
AnkiScape keeps the direct period value.

### Pitfalls and rabbit

Commit `b50683616d8997a4718060b0c82420b46b41471a` restores
`PitfallHunting.java`, `RabbitHunting.java`, and
`traps/RabbitSnare.java`.

The pitfall rows preserve levels and XP, consume one set of Logs at setup, keep
Knife and Teasing stick reusable, and always produce Big bones plus a tatty
fur. They contain no catch/failure selector, no attack/damage branch, and no
perfect-fur reward.

White rabbit preserves Hunter 27, Ferret plus Rabbit snare requirements, 144
XP, and the Bones/Raw-rabbit/Rabbit-foot outputs. It always succeeds, returns
the snare, never loses the Ferret, and directly applies Eagles' Peak to the
action. That direct gate conflicts with the owner-settled contract and the
cutoff Hunter article, both of which gate Ferret acquisition instead.

The restoration's deterministic ceilings cannot be promoted into
source-authentic AnkiScape rolls.

## Exact remaining source blockers

Implementation remains blocked on:

1. tracking catch/failure behavior, including whether any intermediate trail
   sub-roll can fail;
2. Penguin's ordinary-versus-KGP result selector;
3. pitfall catch/failure probability;
4. pitfall attack/damage selector and damage amount;
5. Rabbit-snare disappearance probability;
6. Ferret-loss probability;
7. the numeric Strung-rabbit-foot bird's-nest modifier; and
8. the still-unverified exact level/input semantics for Rabbit-foot stringing.

The `1/4` perfect-fur selector, Jim's `+2` XP, visible levels/XP, tools,
outputs, gates, and Long-kebbit-bolt quantity are closed. They are insufficient
to activate the complete owner-settled card without violating its explicit
source gate.

This is a source gap, not a creative-design gap. No owner question was added.

Codex Workflows run `287714b0-bed1-488d-a085-91ad641ede97` was canceled
without a review result. One Sol-high leaf spent 225,142 generated tokens on
six broad repository-search calls without returning a bounded report; the
other established a session but emitted no token or tool telemetry. The
primary pass independently reproduced every accepted source and integration
finding, and no partial leaf output was used.
