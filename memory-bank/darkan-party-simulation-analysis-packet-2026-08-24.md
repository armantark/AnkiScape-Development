# Darkan party-simulation analysis packet

Date: `2026-08-24`

Status: **analysis only; owner approval is required before implementation.**

Queue basis: `memory-bank/design-thread-queue.md` entry `4.15`, item `4`.

Cutoff: RuneScape immediately before EOC, `2012-11-20`.

## Goal

This packet describes the Darkan Dungeoneering party model in plain language.
It also shows how that model can correspond to AnkiScape.

This packet records no design decision. It changes no runtime behavior.

## Scope and source boundary

The Darkan checkout is:

`/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server`

All three required commits exist as commit objects:

- `d4d43060688d3ed10a007a546aace3368c848625`
- `fcad1e89d4535abf4334824ead6f5bd486efd2e4`
- `f2ed1d7251be3b35c190b055593918af990f6a0a`

The three commits are not consecutive. The exact path between them is:

1. `d4d43060688d3ed10a007a546aace3368c848625`
2. `c7d2ed907fc0e128796b7afa563b2c97a17f6407`
3. `fcad1e89d4535abf4334824ead6f5bd486efd2e4`
4. `a1c34b198adf529f2ea5c290295c15e1733a0789`
5. `8f4981ad87d46e4289c7357dd0ba88c8352342c4`
6. `1d8f8286cd81bd56c297b9cf631a3ce1843c82d3`
7. `f2ed1d7251be3b35c190b055593918af990f6a0a`

This distinction matters. The first section describes only the exact diff in each named commit.
The later sections describe the cumulative tree at `f2ed1d7251be3b35c190b055593918af990f6a0a`.

The cumulative tree contains role and skill-door work from the four intermediate commits.
This packet does not present that work as part of a named commit diff.

The Ring of Kinship implementation in Darkan is legacy Darkan code.
The AnkiScape audit independently closes the class roster and token costs only.
It says that exact class effects were outside that harvest.
See `memory-bank/source-audits/dungeoneering-harvest-2026-07-28.md:250-278`.

Therefore, this packet uses Darkan class code as implementation evidence.
It does not claim that every formula in that code is period-accurate.

## 1. What the three named commits actually change

### 1.1 `d4d43060688d3ed10a007a546aace3368c848625`

This commit adds a headless floor-entry probe.

It adds the `testDungeonProbe` control field and reports its result.
See `d4d43060688d3ed10a007a546aace3368c848625:src/main/java/com/rs/game/content/world/npcs/FakePlayerWorld.kt:635` and `:799`.

The probe creates two headless `Player` objects at Daemonheim.
It adds both players to one `DungeonPartyManager`.
It selects Complexity `1`, difficulty `1`, `Small`, and floor `1`.
It then starts the floor.
See the same file at `:19098-19111`.

After `12` ticks, the probe checks both controllers.
It records success only when both controllers are `DungeonController`.
It then destroys the dungeon and finishes both actors.
See the same file at `:19112-19139`.

The probe actors receive level `50` in seven skills.
Those skills are Attack, Strength, Defence, Ranged, Magic, Hitpoints, and Dungeoneering.
See the same file at `:19151-19164`.

The commit also adds a telemetry block.
The block records `probesRun`, `floorEntries`, `errors`, and recent events.
See the same file at `:15548-15560` and `:19142-19148`.

The commit message reports a narrower live result than the code expects.
The leader entered, but the non-leader did not enter.
The intermediate commit `c7d2ed907fc0e128796b7afa563b2c97a17f6407` later fixed that gap.

Thus, `d4d430606` proves initial feasibility only.
It does not prove that a complete headless party entered in that commit.

### 1.2 `fcad1e89d4535abf4334824ead6f5bd486efd2e4`

This commit adds a driven party member.

It adds the `testDungeonMate` control field and result text.
See `fcad1e89d4535abf4334824ead6f5bd486efd2e4:src/main/java/com/rs/game/content/world/npcs/FakePlayerWorld.kt:636` and `:801`.

The probe creates one headless leader and one `FakeDungeonMate`.
It starts a Complexity `1`, difficulty `1`, `Small`, floor `1` party.
See the same file at `:19111-19123`.

After `18` ticks, the probe moves the leader by five tiles.
After `40` ticks, it checks that both actors are inside the floor.
It also checks that the mate is no more than two tiles from the leader.
See the same file at `:19124-19140`.

`FakeDungeonMate.processEntity()` drains the mate's task queue.
The mate then reads the leader's current combat target.
If the target is valid, the mate starts `PlayerCombatInteraction` against it.
Otherwise, the mate follows the leader when their distance is more than one tile.
See the same file at `:19218-19257`.

The commit directly measures follow distance.
It does not directly measure damage from the assist path.
The commit message says that assist reuses the existing monster-combat interaction.

Thus, `fcad1e89d` adds follow and target assist.
It does not add Ring of Kinship classes or player-selected party size.

### 1.3 `f2ed1d7251be3b35c190b055593918af990f6a0a`

This commit adds the fake-host direction.

`offerDungeonInvite()` rejects a player who already has a party.
It also rejects a target that `World.getPlayerByDisplay()` cannot resolve as the same real player.
The fake host then uses the normal `DungManager.invite()` path.
See `f2ed1d7251be3b35c190b055593918af990f6a0a:src/main/java/com/rs/game/content/world/npcs/FakePlayerWorld.kt:1099-1115`.

The commit adds `hostPartyWithGuest()` as a test seam.
That seam directly adds the guest to the fake-hosted party.
It does not execute the real request-and-accept round trip.
See the same file at `:1118-1127`.

The fake host checks for a real guest on each entity tick.
When the guest exists, the host transfers leadership to that guest.
See the same file at `:19483-19496`.

The host test waits `4` ticks and checks the leader.
The commit also adds the `handoffs` counter and handoff events.
See the same file at `:19190-19199`, `:19213-19245`, and `:19403-19412`.

The snapshot writes the host to `pendingDungeonHosts` at `:1113`.
It declares that map at `:1129`, but the same snapshot never reads or removes an entry.
The retention and cleanup purpose is ambiguous.

Thus, `f2ed1d725` gives the player control before floor start.
It does not test the real client acceptance step.
It does not add a party-count control or new Kinship effects.

## 2. The cumulative Darkan party model

This section describes the tree at `f2ed1d7251be3b35c190b055593918af990f6a0a`.
Some behavior comes from the four intermediate commits listed above.

### 2.1 What a party is

A party is a native `DungeonPartyManager` team.
In the player-facing path, the team contains the real player and headless `FakeDungeonMate` actors.
The all-headless actors in `d4d430606` and `fcad1e89d` are test probes.

The code rejects an invite when the team already has five members.
Therefore, a player-led party can contain at most four simulated members.
See `f2ed1d7251be3b35c190b055593918af990f6a0a:src/main/java/com/rs/game/content/world/npcs/FakePlayerWorld.kt:1136-1150`.

Each simulated member comes from one `FakePlayerProfile`.
The profile supplies a display name and skill levels.
See the same file at `:20333-20360`.

A mate copies the profile's skills and sets Dungeoneering to `50`.
It also sets `maxFloor` to `10` and `maxComplexity` to `6`.
See the same file at `:19450-19465`.

The mate selects one of two companion roles:

- `tank` when `maxOf(defence, strength) >= ranged`
- `assist` otherwise

See the same file at `:19466-19470`.

A `tank` binds a tiered rapier and kiteshield.
An `assist` binds a tiered shortbow.
The item tier is clamped to `1..8`.
See the same file at `:19471-19480`.

The real player is the operational leader.
A fake host transfers leadership when a real guest joins.
See the same file at `:19488-19495`.

### 2.2 What the party does on each Darkan entity tick

The mate uses this order on each entity tick:

1. It drains its own task queue.
2. It runs the normal `Player` entity process.
3. It transfers leadership when it is a fake host with a real guest.
4. It stops if it is not inside `DungeonController`.
5. It reads the current party leader.
6. It selects a combat target.
7. It attacks a valid target.
8. It stops an old combat interaction when no target exists.
9. It tries one nearby skill door.
10. It follows the leader when no door action starts.

The task and leadership order is at `f2ed1d7251be3b35c190b055593918af990f6a0a:src/main/java/com/rs/game/content/world/npcs/FakePlayerWorld.kt:19483-19499`.

A `tank` first selects an NPC that attacks the leader.
If no such NPC exists, it selects the leader's target.
An `assist` selects only the leader's target.
See the same file at `:19500-19507` and `:19549-19553`.

Without a target, the mate tries a nearby skill door.
It considers doors within three tiles on the same plane.
It tries each door at most once.
See the same file at `:19518-19534`.

The game owns the door requirement check.
The mate only asks the normal object-click handler to open the door.
After `5` ticks, the mate records whether the object changed.
See the same file at `:19518-19543`.

If no door action starts, the mate follows the leader.
It starts `EntityFollow` only when the distance is more than one tile.
See the same file at `:19509-19515`.

### 2.3 What the model needs from the player

The player supplies party membership before the floor starts.
Darkan exposes this through individual display-name invites.
It does not expose one player-selected count field.
See the same file at `:1131-1150`.

The player also supplies the floor start decision.
The fake host transfers leadership before the dungeon starts.
See the same file at `:19488-19495`.

Inside the floor, the player supplies route and target intent.
The mate follows the leader's location and combat target.
The player does not issue a command to the mate on each tick.

The player does not select `tank` or `assist` directly.
Darkan derives that role from the fake profile's Defence, Strength, and Ranged levels.
See the same file at `:19454-19470`.

### 2.4 What the model produces

The model produces these direct effects:

- native party membership;
- one visible headless party actor for each mate;
- combat damage against the leader's target;
- target peel behavior for `tank`;
- skill-door attempts that use the mate's own skills;
- automatic following;
- player leadership before floor start; and
- telemetry for joins, follows, doors, entries, handoffs, and errors.

The telemetry fields are `floorEntries`, `matesJoined`, `mateFollows`, `doorsOpened`, `handoffs`, and `errors`.
See `f2ed1d7251be3b35c190b055593918af990f6a0a:src/main/java/com/rs/game/content/world/npcs/FakePlayerWorld.kt:15633-15643` and `:19403-19412`.

The named commits do not add a direct loot or token award.
They do not define an XP split between the player and simulated members.
They do not define a reward multiplier for party count.

The native game can observe full `Player` objects in the team.
Other Dungeoneering code can therefore react to party state.
The three named commits do not quantify those downstream effects.

### 2.5 The flattened AnkiScape correspondence

AnkiScape does not have location ticks or visible headless actors.
A flattened port must preserve the effect of each Darkan action, not its scene graph.

| Darkan concept | Smallest flattened AnkiScape concept | Source limit |
| --- | --- | --- |
| `DungeonPartyManager.team` | The player plus `0..4` simulated members | Darkan caps the complete team at `5`; it has no count control. |
| `FakePlayerProfile` | A member skill and role source | Darkan uses names and full profiles; the packet does not settle persistent identities. |
| Player leadership | The player always controls floor start, route, and target | The fake-host path transfers leadership before the floor starts. |
| `EntityFollow` | The party remains with the player's current room | Follow has no separate output in a location-free model. |
| `PlayerCombatInteraction` | A party combat contribution during the review combat burst | The commits do not define XP ownership for that contribution. |
| `tryOpenSkillDoor()` | A party member can attempt a skill door with member skills | The commits do not settle whether this can bypass the player's level gate. |
| One Darkan entity tick | One party action step inside a successful Dungeoneering review | The source does not define this time translation. |
| Fake invite flow | A between-floor party control | Entry `4.15` requires player-chosen count, not a name-entry replica. |

The current Dungeoneering contract uses one successful review as one room beat.
See `memory-bank/dungeoneering-design-contract-2026-07-18.md:14-29`.

Therefore, a review is the available AnkiScape time boundary.
The source does not say how many member actions one review must contain.
That remains an owner decision.

## 3. Darkan roles and Ring of Kinship classes are different systems

Darkan uses `tank` and `assist` as fake-member roles.
Darkan also has twelve Ring of Kinship classes.

The name `tank` appears in both systems.
The two meanings are not the same.

- The fake-member `tank` peels an NPC from the leader.
- The Ring class `TANK` reduces incoming damage while the wearer has a shield.

See `f2ed1d7251be3b35c190b055593918af990f6a0a:src/main/java/com/rs/game/content/world/npcs/FakePlayerWorld.kt:19500-19507`.
See `f2ed1d7251be3b35c190b055593918af990f6a0a:src/main/java/com/rs/game/content/skills/dungeoneering/DungeonController.java:193-199`.

The fake-member `assist` role is not a Ring of Kinship class.
It means "attack the leader's current target."

The fake-member skill-door behavior is also not a Ring class.
It is a general party contribution.

### 3.1 Darkan companion-role crosswalk

| Darkan companion role or behavior | AnkiScape correspondence | Result |
| --- | --- | --- |
| `tank` | An ally selects an enemy that attacks the player before it selects the player's target. | Partial analog. It does not equal the Ring `Tank` damage-reduction effect. |
| `assist` | An ally contributes damage to the player's active Dungeoneering target. | Direct behavioral analog. No Ring class has this exact meaning. |
| Skill-door contributor | An ally uses its own skill level for a nearby door attempt. | Direct room-utility analog. No Ring class has this exact meaning. |
| Fake host | A party exists before the player joins, then gives the player leadership. | No needed gameplay analog if AnkiScape uses a count control. |
| Follower | The ally stays with the player between rooms. | No separate mechanical analog in the room-graph model. |

### 3.2 Per-class analog table

Darkan lists all twelve classes in `KinshipPerk`.
It marks `SNIPER`, `BLASTER`, `GATHERER`, and `ARTISAN` as `TODO`.
See `f2ed1d7251be3b35c190b055593918af990f6a0a:src/main/java/com/rs/game/content/skills/dungeoneering/KinshipPerk.java:19-31`.

A repository-wide positive-control search found executable uses for the other implemented classes.
The same search found no `KinshipPerk.SNIPER`, `KinshipPerk.BLASTER`, `KinshipPerk.GATHERER`, or `KinshipPerk.ARTISAN` use.
The command was `git grep -n "KinshipPerk\." f2ed1d725 -- src/main/java`.

AnkiScape stores the same twelve classes and their source-effect labels.
See `data/dungeoneering_data.py:165-194`.

| Class | Executable Darkan behavior at `f2ed1d725` | Party-simulation analog | Existing AnkiScape correspondence | Correspondence status |
| --- | --- | --- | --- | --- |
| `TANK` / Tank | With a shield, incoming damage uses `damage × (0.94 - tier × 0.01)`. See `f2ed1d7251be3b35c190b055593918af990f6a0a:src/main/java/com/rs/game/content/skills/dungeoneering/DungeonController.java:193-197`. | A fake `tank` peels enemies, but does not apply this shield formula to the player. | The class and tier exist. The current view says the combat effect is not applied. See `logic/dungeoneering_logic.py:1150-1186`. | **Partial only.** The shared name hides two different effects. |
| `TACTICIAN` / Tactician | Accurate melee uses `accuracy = 1.1 + tier × 0.01`. See `f2ed1d7251be3b35c190b055593918af990f6a0a:src/main/java/com/rs/game/content/items/CombatEnhancers.kt:85-100`. | No companion-role analog. | The combat kernel has attack styles and accuracy rolls. It has no Kinship hook. | **Kernel analog; no party analog.** |
| `BERSERKER` / Berserker | Aggressive melee uses `strengthLevel = 1.1 + tier × 0.01`. See `f2ed1d7251be3b35c190b055593918af990f6a0a:src/main/java/com/rs/game/content/items/CombatEnhancers.kt:85-100`. | No companion-role analog. A fake `tank` can use melee equipment, but receives no Berserker effect. | The combat kernel has melee styles and effective Strength. It has no Kinship hook. | **Kernel analog; no party analog.** |
| `SNIPER` / Sniper | The enum says `TODO`. The inspected tree has no `KinshipPerk.SNIPER` use. | No analog. The ranged fake uses a shortbow, but it has no longrange maximum-hit proc. | The combat kernel computes ranged maximum hit. It has no Sniper proc. | **No executable Darkan analog.** |
| `KEEN_EYE` / Keen-eye | Accurate ranged uses `int(40 + tier × 6.5)` percent to call `lowerDefense(1, 0.0)`. See `f2ed1d7251be3b35c190b055593918af990f6a0a:src/main/java/com/rs/game/content/skills/dungeoneering/DungeonController.java:201-214`. | No companion-role analog. | The combat kernel stores enemy Defence factors. It has no Kinship proc hook. | **Kernel analog; no party analog.** |
| `DESPERADO` / Desperado | Rapid ranged uses `strengthLevel = 1.1 + tier × 0.01`. See `f2ed1d7251be3b35c190b055593918af990f6a0a:src/main/java/com/rs/game/content/items/CombatEnhancers.kt:94-97`. | No companion-role analog. | The combat kernel has ranged styles and attack-speed rules. It has no Kinship level hook. | **Kernel analog; no party analog.** |
| `BLAZER` / Blazer | A magic hit has `5 × tier` percent chance. It schedules five hits at `2 × i` ticks, each for `hit damage / 10`. See `f2ed1d7251be3b35c190b055593918af990f6a0a:src/main/java/com/rs/game/content/skills/dungeoneering/DungeonController.java:215-225`. | No companion-role analog. Darkan has no magic fake-member role. | The combat kernel has tick status damage. It has no Blazer hook. | **Kernel analog; no party analog.** |
| `BLASTER` / Blaster | The enum says `TODO`. The inspected tree has no `KinshipPerk.BLASTER` use. | No analog. Darkan has no magic fake-member role. | The combat kernel supports freeze-like enemy delay. It has no Blaster proc. | **No executable Darkan analog.** |
| `BLITZER` / Blitzer | `10 × tier` percent chance changes spell delay from `4` to `3`. See `f2ed1d7251be3b35c190b055593918af990f6a0a:src/main/java/com/rs/game/content/combat/CombatSpell.kt:592-599`. | No companion-role analog. Darkan has no magic fake-member role. | The combat kernel models attack speed. It has no Kinship proc hook. | **Kernel analog; no party analog.** |
| `MEDIC` / Medic | Food given to another player uses `heal × (1.2 + tier × 0.03)`. See `f2ed1d7251be3b35c190b055593918af990f6a0a:src/main/java/com/rs/game/content/skills/cooking/Foods.java:67-72`. | Party simulation supplies another player-shaped target. `FakeDungeonMate` does not transfer food or heal. | The current view states that the solo floor has no Medic effect. See `logic/dungeoneering_logic.py:1169-1172`. | **Structural analog only.** A party target exists, but the action does not. |
| `GATHERER` / Gatherer | The enum says `TODO`. The inspected tree has no `KinshipPerk.GATHERER` use. | No Darkan party-role analog. | AnkiScape already rolls one extra gathered resource and reduces failed-task damage. See `logic/dungeoneering_logic.py:1155-1161`, `:1576-1586`, and `:1643-1649`. | **Existing AnkiScape analog; no executable Darkan analog.** |
| `ARTISAN` / Artisan | The enum says `TODO`. The inspected tree has no `KinshipPerk.ARTISAN` use. | No Darkan party-role analog. | AnkiScape already saves processing inputs and reduces failed-task damage. See `logic/dungeoneering_logic.py:1162-1168`, `:1620-1629`, and `:1658-1666`. | **Existing AnkiScape analog; no executable Darkan analog.** |

The Darkan role code does not close the ten inactive AnkiScape class effects.
It only gives direct party behavior for target assist, target peel, and skill doors.

The Medic class is the one clear structural gain from party simulation.
A second actor makes the source's "another player" target possible.
The source still does not settle the AnkiScape healing interaction.

## 4. What AnkiScape already supports

### 4.1 Existing substrate

| Existing substrate | Evidence | Use for a future party model |
| --- | --- | --- |
| Persistent floor state | `logic/dungeoneering_logic.py:729-767` | Can store a party choice after the owner selects a representation. |
| Persistent room graph | `logic/dungeoneering_logic.py:62-82`, `:380-495`, and `:621-701` | Gives the shared room, frontier, death, and completion state. |
| One room beat per review | `logic/dungeoneering_logic.py:2501-2649` | Gives the available party action boundary. |
| Player route ownership | `logic/dungeoneering_logic.py:2281-2295` and `:2541-2549` | Keeps the player as leader in Casual and Advanced modes. |
| Skill-door resolution | `logic/dungeoneering_logic.py:2322-2379` | Can host a party-member door attempt after eligibility rules exist. |
| Session inventory and equipment | `logic/dungeoneering_logic.py:2137-2169` and `:2393-2431` | Can supply floor-only combat and healing resources. |
| Auto-eat for the player | `logic/dungeoneering_logic.py:2300-2319` | Supplies a healing primitive, but only for the player. |
| Tick-based combat burst | `logic_pure/logic_pure_combat_engine.py:1017-1030`, `:1252-1264`, and `:1569-1644` | Can supply attack rolls, attack speed, damage, and status timing. |
| Combat result state | `logic_pure/logic_pure_combat_engine.py:2517-2543` | Can report damage, lifepoints, kills, death, and elapsed ticks. |
| Ring class and tier state | `logic/dungeoneering_logic.py:753-754`, `:1150-1186`, and `:1988-2020` | Keeps one active class and authentic tier spending. |
| Gatherer and Artisan effects | `logic/dungeoneering_logic.py:1576-1666` | Already supplies the two live skiller effects. |
| Honest no-effect text | `logic/dungeoneering_logic.py:1169-1177` | Prevents an unsigned analog from appearing as settled behavior. |

### 4.2 New mechanism that any party port needs

Any party port needs a party state that does not exist now.
The current `DungeonSession` has no party member field.
See `logic/dungeoneering_logic.py:62-82`.

The following mechanisms are new:

- a player-chosen simulated-member count;
- a stored party representation;
- role or class assignment for each simulated contribution;
- a party action order inside one review;
- ally target selection;
- ally combat damage that does not duplicate player XP;
- ally lifepoints if Medic targets a member;
- food transfer or shared healing if Medic becomes live;
- member skill checks for doors;
- one-attempt tracking for member door actions;
- party action result text;
- defaults and sanitization for the new persisted state; and
- user controls between floors.

Some options need more new mechanism:

- Named members need persistent identities and profiles.
- Per-member combat needs equipment, supplies, lifepoints, and action state.
- Party-aware boss scaling needs count and combat-level inputs.
- Full party payout scaling needs period-qualified formulas.

The current placeholder register already names party-aware boss scaling.
See `logic/dungeoneering_logic.py:335` and `memory-bank/source-audits/dungeoneering-harvest-2026-07-28.md:567-576`.

## 5. Open design questions

The Darkan source does not answer these AnkiScape questions.
Each question needs an owner choice before implementation.

### P1. What is one simulated member?

| Option | Model | Trade-off |
| --- | --- | --- |
| `P1-A` | Store each member with role, skills, lifepoints, equipment, and state. | This preserves Darkan actor semantics. It adds the most state and UI. |
| `P1-B` | Store one aggregate party with count and total contribution. | This is small and easy to undo. It cannot model individual Medic targets or member death. |
| `P1-C` | Store role buckets, such as two `assist` and one `tank`. | This preserves role mix without names. It still cannot model individual supplies or lifepoints. |

### P2. What does the player choose between floors?

| Option | Input | Trade-off |
| --- | --- | --- |
| `P2-A` | Choose only simulated-member count `0..4`. Derive composition deterministically. | This matches queue entry `4.15`. The derivation rule becomes a new design choice. |
| `P2-B` | Choose count and each member role. | This gives clear control. It adds more controls and can become a setup screen. |
| `P2-C` | Choose named persistent members from a fake-player roster. | This is closest to Darkan invites. AnkiScape has no fake-player population substrate. |

### P3. How many party actions occur in one successful review?

| Option | Tick translation | Trade-off |
| --- | --- | --- |
| `P3-A` | Each simulated member receives one action step. | Count has visible value. Power and runtime scale with party size. |
| `P3-B` | The party receives one aggregate action step. Count changes its chance or magnitude. | Runtime stays fixed. Individual roles become less visible. |
| `P3-C` | Fold party effects into the player's room or combat action. | This is the smallest runtime change. The party can feel like a passive modifier. |

Darkan runs each `FakeDungeonMate.processEntity()` on every entity tick.
AnkiScape resolves one room beat per successful review.
No source defines the ratio between those units.

### P4. What owns the Ring of Kinship class effect?

| Option | Ownership | Trade-off |
| --- | --- | --- |
| `P4-A` | The active Ring class changes only the player's actions. | This keeps the source meaning. It does not assign companion behavior. |
| `P4-B` | The active Ring class selects or changes a simulated-member role. | This makes the party visible. It changes a player perk into a companion role. |
| `P4-C` | The class changes both player and party actions. | This gives strong class identity. It can apply the same tier value twice. |

Darkan does not connect `FakeDungeonMate.role` to `KinshipPerk`.
Any such connection is an AnkiScape analog.

### P5. How does party combat affect damage and XP?

| Option | Combat output | Trade-off |
| --- | --- | --- |
| `P5-A` | Run an independent combat actor for each member. Give no player combat XP for ally damage. | This is closest to Darkan. It needs per-member combat state and damage ownership. |
| `P5-B` | Apply one party-damage bundle to the enemy each review. | This is smaller. It loses weapon speed, ammo, and per-member status detail. |
| `P5-C` | Give party members only defensive and utility effects. | This avoids damage attribution. It does not preserve Darkan assist attacks. |

The three named commits do not define player XP for ally damage.
They also do not define a party reward split.

### P6. Can a simulated member satisfy a skill-door requirement?

| Option | Door rule | Trade-off |
| --- | --- | --- |
| `P6-A` | A qualified member can open any reachable skill door. | This matches Darkan behavior. It can bypass the player's skill gate. |
| `P6-B` | A member can open only optional or bonus doors. | This preserves the player's critical-path gates. It narrows Darkan behavior. |
| `P6-C` | A member cannot satisfy the level gate. It can only reduce failure damage or retry cost. | This protects progression. It has no direct Darkan analog. |

Darkan calls the normal door handler with the member actor.
The member's own skill level therefore supplies the requirement check.
See `f2ed1d7251be3b35c190b055593918af990f6a0a:src/main/java/com/rs/game/content/world/npcs/FakePlayerWorld.kt:19518-19543`.

### P7. What makes Medic live?

| Option | Medic model | Trade-off |
| --- | --- | --- |
| `P7-A` | The player gives floor food to a wounded simulated member. Medic increases that heal. | This keeps the Darkan action direction. It needs member lifepoints and food transfer. |
| `P7-B` | The party uses one shared lifepoint pool. Medic improves shared healing. | This is smaller. It removes individual targets. |
| `P7-C` | A Medic companion heals the player. | This is easy to understand. It reverses the sourced giver and receiver roles. |
| `P7-D` | Keep Medic at no effect until a member-health model exists. | This adds no invented effect. Medic stays inactive after party count ships. |

Darkan applies Medic only when `givenFrom` is the Medic.
The recipient is another player.
See `f2ed1d7251be3b35c190b055593918af990f6a0a:src/main/java/com/rs/game/content/skills/cooking/Foods.java:67-72`.

### P8. How does party size affect floor difficulty and payout?

| Option | Scaling | Trade-off |
| --- | --- | --- |
| `P8-A` | Party count changes only party contributions. Boss and payout stay on the current solo model. | This is bounded. It can make larger parties strictly easier. |
| `P8-B` | Party count changes boss level or lifepoints, but not payout. | This restores some challenge. The boss-scaling formula is still a registered placeholder. |
| `P8-C` | Party count changes boss state and completion payout. | This gives full party economics. The required period formulas are not closed. |

The current audit rejects the legacy three-player difficulty row.
It records a suspicious `0.95` value.
See `memory-bank/source-audits/dungeoneering-harvest-2026-07-28.md:221-224` and `:593-597`.

## 6. Owner ruling sheet

This table records the choices that implementation needs.
It does not select any option.

| Decision | Owner choice |
| --- | --- |
| `P1` member representation | `P1-A` / `P1-B` / `P1-C` |
| `P2` between-floor input | `P2-A` / `P2-B` / `P2-C` |
| `P3` actions per review | `P3-A` / `P3-B` / `P3-C` |
| `P4` Ring class ownership | `P4-A` / `P4-B` / `P4-C` |
| `P5` combat output and XP | `P5-A` / `P5-B` / `P5-C` |
| `P6` skill-door authority | `P6-A` / `P6-B` / `P6-C` |
| `P7` Medic model | `P7-A` / `P7-B` / `P7-C` / `P7-D` |
| `P8` difficulty and payout scaling | `P8-A` / `P8-B` / `P8-C` |

## 7. Uncertainty that must remain visible

- `d4d430606` did not get the non-leader into the floor during its live run.
- `fcad1e89d` measured follow distance, not assist damage.
- `f2ed1d725` bypassed the real invite acceptance step in its host test.
- `pendingDungeonHosts` is write-only in the inspected `f2ed1d725` snapshot.
- The three named commits do not form the complete party-simulation sequence.
- The final tree has only two fake-member roles: `tank` and `assist`.
- The final tree has no magic, Medic, Gatherer, or Artisan fake-member role.
- `SNIPER`, `BLASTER`, `GATHERER`, and `ARTISAN` remain `TODO` in `KinshipPerk`.
- Darkan does not provide one player-selected party-count control.
- Darkan does not define the AnkiScape world-tick-to-review translation.
- The commits do not define ally XP ownership or party payout scaling.
- The current party-aware boss formula remains a registered placeholder.
- The Ring class formulas cited here are Darkan implementation evidence, not a new parity ruling.

## 8. Non-goals

This packet does not implement party simulation.
It does not change tests, audits, data, or runtime files.
It does not settle any option in `P1` through `P8`.
It does not replace the current honest no-effect display.
