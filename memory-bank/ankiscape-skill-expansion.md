# AnkiScape Skill Expansion

Focused continuation document for the **Prayer** deep grill.
It is not the global post-Herblore roadmap; that role now belongs to
`archive/2026-07/baselines/completion-audit-2026-07-10.md` and
`future-work-kanban.md`.

Status: **historical Prayer grill, implemented 2026-07-11 and closed
2026-07-13.** The body below preserves the pre-implementation contract; the
post-implementation addendum and linked source audit record the shipped state.

Global status lives in the completion kanban. At the time of this grill, the
registry distinguished 11 complete skill surfaces, six partial Combat-trained
skills, and eight planned skills; Prayer was still `planned` until its surface
shipped.
All source work below follows `pre-eoc-source-verification-standard.md`: pinned
pre-EOC wiki revisions and period caches establish history, while
2011Scape/current Darkan code is reconstruction evidence that must be
reconciled. Never fill a gap from modern RS3 or OSRS behavior.

---

## Completed grill: Prayer (implementation-ready)

### Framing
Prayer is two separable features wearing one name:

1. **Prayer training (the skill)** — consume a bone/ash → gain Prayer XP. A
   one-action recipe-transform, the same engine shape as Herblore/Cooking.
2. **Prayer points + the prayer/curse combat overlay** — the drain-based combat
   layer, translated to the EV model below.

The owner does **not** want v1/v2 phasing — build everything whose dependencies
already exist in one pass. Only *dependency-blocked* items sit out (see Parked).

### What already exists (no work needed)
- **Bone inputs flow from combat**: `"Bones"` on ~47 drop-table entries in
  `combat_data.py`, `"Big bones"` on 4, `"Wolf bones"` on 3.
- **Prayer-point restore economy already built via Herblore**: Prayer potion (3),
  Super prayer, Prayer renewal, Prayer mix are all live
  (`herblore_data.py:123,148,149,162`).
- **`prayer_level` already feeds the combat-level formula**
  (`logic_pure.py:4208`) and `prayer` is in `_COMBAT_AFFECTABLE_SKILLS`
  (`logic_pure.py:1166`).
- **Equipment already models a prayer bonus**: `prayer` is in
  `EQUIPMENT_BONUS_FIELDS` (`equipment_data.py:15`), so the drain-resistance
  formula consumes it with no schema change.
- **Buckets, empty pots, and tinderboxes are live in NPC shops** (verified in
  `shop_data.py` stock); clean marrentill is live via Herblore.

### Sourcing (all pins closed 2026-07-11)
- **Bury XP per bone (game-main, primary):**
  `content/skills/prayer/burying/BoneData.kt` + `bone_burying.plugin.kts`.
  Ladder: Bones/Wolf/Burnt 4.5, Monkey 5.0, Bat 5.3, Zogre 12.5, Big/Jogre 15,
  Shaikahan 25, Baby dragon 30, Wyvern 50, Dragon 72, Fayrg 84, Raurg 96,
  Dagannoth 125, Ourg 140, Frost dragon 180, Ancient 200.
- **Protection-prayer drain rates + effects (game-main):**
  `content/mechanics/prayer/prayer.kt`, `Prayers.kt`. Drain resistance
  `60 + prayerBonus*2`; points stored internally as `level*10`.
- **Ancient curses (wiki, `Ancient Curses`?oldid=6535713):** full L50–95 ladder,
  effects, and drain-rate column. Sap −10%→−20% enemy; Leech +5%→+10% self /
  −10%→−25% enemy; Deflects stop 100% of NPC damage like protects; Wrath up to
  250% of Prayer level on death; Soul Split heals 20% of damage dealt; Turmoil
  +15% Att/Def +15% of enemy level, +23% Str +10% of enemy level. Unlock:
  completing The Temple at Senntisten.
- **Curse hidden-server cadence (Darkan, sanctioned reconstruction):**
  `CurseManager.java:15-16` — leech procs 20%/attack, sap 25%/attack, stepping
  toward the wiki caps; deflect returns 10% of the raw hit at a 60% roll
  (`Player.java:2140-2146`); conflict groups in `PrayerManager.kt` closePrayers.
- **Gilded/POH altars (wiki, `Prayer`?oldid=6539264):** tier ladder Oak→Gilded
  100%–250%, +50% of base per lit burner, max 3.5×.
- **Ectofuntus (wiki, `Ectofuntus`?oldid=6544994):** 4× bury XP; 1 pot of
  bonemeal + 1 bucket of slime per worship; demonic ashes skip grinding;
  5 ecto-tokens per worship (265 per 53).
- **Demonic ashes (wiki, `Infernal ashes`?oldid=6529055):** released 15 Feb 2011
  (pre-EOC). Infernal: 62.5 XP scattered, 250 at Ectofuntus, 218.7 at 2-burner
  gilded — i.e. scatter XP is the ash "base" and methods multiply exactly like
  bones. 100% drops from black/abyssal/tormented demons, nechryael, demon bosses.
- **Restless Ghost ancient bones (game-main, primary):**
  `TheRestlessGhost.kt:122` and `father_aereck.plugin.kts:250-251` grant 5
  Ancient bones (200 XP each) one time. Confirmed; no wiki page needed.
- **Rapid Restore (wiki, `Rapid Restore`?oldid=6268755 + `Temporary skill
  boost` pre-EOC snapshot):** stats decay/recover toward base ~1 level/min
  (= the engine's existing 100-tick cadence); Rapid Restore doubles it for all
  skills except Constitution, Prayer, Summoning.
- **STRUCK — Chaos Temple Wilderness bone altar.** Both pre-EOC pages —
  `Chaos Temple (Wilderness)`?oldid=5934985 (level-11 temple, 2012-07-14) and
  `Chaos Temple (hut)` (level-38 hut, pre-EOC snapshot 2012-11-09) — describe
  prayer-recharge altars only; game-main has only static constants. The
  bone-offering altar with the 50% bone save arrived in **OSRS on 7 December
  2017** ("The Corsair Curse and Wilderness Chaos Altar" update, at the
  level-38 hut), and RS3 never added it at all — a false positive of the
  `fletch-javelin-construction` class. The "chaos altar risk model" open
  decision is moot. (Bone-spawn gathering was deliberately not added as a
  route: combat bone drops are already at their authentic ceiling.)

### Training methods (final roster)
1. **Bury bones** — 1×, zero friction, one bone per review (game-main BoneData).
2. **Scatter demon ashes** — 1× of the ash's scatter XP, one per review
   (impious/accursed/infernal only; regular Ashes are not a Prayer item).
3. **Ectofuntus** — 4×, authentic two-step. Utility prep: **grind bones at
   ~9 per review** (explicit owner-chosen pacing knob: grinding was famously
   slow, and this keeps the gilded altar the premium-speed method as in 2012);
   **collect slime at 28 per review**. Worship = 1/review, consumes one pot of
   bonemeal (per bone type) + one bucket of slime, grants 4× bury XP + 5
   ecto-tokens. Ashes worship directly without grinding. Effective ≈3.4×/review.
4. **Gilded altar (hosted)** — flat **3.5×**, one bone/ash per review.
   Friction: a random **1–10 review "find a suitable house" roll paid once per
   stint** (when switching to a gilded target). **Burners are free while
   hosted** — the host's runners supply marrentill (owner decision 2026-07-11).
   When Construction lands, an owned POH altar replaces the roll and the owner
   supplies burner herbs; the full Oak→Gilded tier ladder ships with
   Construction, not now.
5. **Restless Ghost** — 5 one-time Ancient bones (minor landmark, game-main).
6. ~~Chaos Temple Wilderness altar~~ — struck (see Sourcing).
7. **Shades of Mort'ton cremation** — trails as dependency-blocked on the
   Shades activity-family grill (not phase-deferred).

### Design decisions (settled)
- **No flicking.** Not a 2012 core mechanic; any model would be invented.
- **EV damage mitigation.** Protection/deflect prayers multiply each enemy hit
  by `(1 − uptime)`; offensive prayers become effective-level multipliers
  scaled by uptime, applied pre-loop. Drain accrues per simulated tick at the
  authentic rate × uptime. Combat hooks: enemy damage `logic_pure.py:3502-3516`;
  pre-loop accuracy/max-hit `3457-3486`; per-tick loop `3435`.
- **Uptime policy, not assumed 100%.** Toggle Off / Conservative 40% /
  Aggressive 70% / Always 100%, scoped through the combat preset system below.
  The fractions are the one invented knob, tuned from telemetry later.
- **Checkbox prayer selection via combat presets** (owner decision 2026-07-11,
  second pass). Prayer checkboxes + uptime do not attach directly to targets;
  they fold into a **named combat preset system with per-target override** —
  saved presets bundle the whole combat configuration (the existing global
  `combat_supply_loadout`, `combat_pack_mode`, auto-eat settings, plus the new
  prayer selection and uptime), and any combat target can pin a preset or
  override individual fields. This mirrors skilling's casual-preset /
  advanced-saved-layout split (`runtime_actions.py:428`) and generalizes the
  current global-only combat state (`default_combat_state_pure`,
  `logic_pure.py:1201`); migration keeps the existing global loadout as the
  initial default preset. Checkboxes are gated by unlock level, enforce the
  authentic conflict groups (protect/deflect one-of; sap ⊥ leech ⊥ turmoil;
  overheads ⊥ Wrath/Soul Split), and get a "hide lower-tier prayers" toggle.
- **All 30 standard prayers + full Ancient Curses book.** Book toggle is
  **global** (as in-game), gated on The Temple at Senntisten completion, and
  applies from the next combat burst. The Altar of Zaros +15% switch boost is
  omitted — there is no altar-visit action to hang it on; the free bank-run
  refill already abstracts altars. Vs-NPC-inert prayers/curses (Smite, Protect
  from Summoning, Sap Spirit, Leech Special/Energy) ship included-but-inert.
- **Curse EV translation (sourced, mechanics-glue):**
  - Sap/Leech: per-player-attack EV ramp (proc chance × step from Darkan
    `Sap.java`/`Leech.java`, capped at the wiki percentages), applied to enemy
    effective levels (and self levels for leeches), all × uptime.
  - Deflect: protection EV + reflected damage EV = `0.1 × 0.6 × raw hit ×
    uptime` credited against the enemy.
  - Soul Split: heal `20% × damage dealt × uptime`; enemy prayer drain inert.
  - Turmoil: Att/Def `×(1 + 0.15·uptime) + 0.15·enemy_level·uptime`; Str
    `×(1 + 0.23·uptime) + 0.10·enemy_level·uptime` (enemy base levels from
    `combat_data.py`).
  - Wrath/Retribution: on player death, roll up to 250% / 25% of Prayer level
    as damage to the enemy.
  - Berserker: boost-decay interval `×(1 + 0.15·uptime)`.
- **Rapid Restore analog:** recovery-step multiplier `(1 + uptime)` on the
  existing `COMBAT_STAT_DRAIN_RECOVERY_TICKS` 100-tick cadence
  (`_combat_recover_current_levels`, `logic_pure.py:2529`), excluding
  Constitution/Prayer/Summoning. Rapid Heal analog: natural LP trickle
  `×(1 + uptime)`. Rapid Renewal / Prayer renewal potion restore points
  gradually per tick (pin exact rate at implementation).
- **Prayer points:** max = `prayer_level` (internally `level*10`). Bank-run
  refill = free full restore "as if stopping by an altar." Mid-burst restore =
  Prayer potions auto-drunk (existing stat-potion auto-drink,
  `logic_pure.py:3331`). At 0 points with no potion, prayers switch off until
  the next bank-run refill. Drain resistance `60 + 2×prayer equipment bonus`.
- **Protect Item** is meaningful because PvM death has real costs
  (`_combat_apply_pvm_death`, `logic_pure.py:1455`).
- **Auto-bury/scatter during combat**: per-combat toggle spending extra
  simulated ticks per bone/ash, off by default.
- **Piety/Chivalry gates:** pre-EOC these required King's Ransom + the Knight
  Waves training ground. Model Knight Waves with the established one-time
  landmark pattern (see `stronghold-landmark-pattern` memory); pin exact
  requirements at implementation.
- **UI:** Prayer is a normal XP-bearing skill surface: grouped
  `TargetRowMetadata` rows by method (Bury / Scatter / Ectofuntus / Gilded
  altar), same grouping pattern as Smithing tiers. Grinding and slime
  collection are no-XP Utility prep activities. Ecto-tokens are a stackable
  currency item with no sink yet (authentic sinks arrive with later Morytania
  content) — normal input-starved-in-reverse, no special UI state.

### Still parked (dependency-blocked)
- **Shades of Mort'ton cremation** — needs the Shades activity-family grill.
- **GE-bought bones** — needs the Grand Exchange
  (`fake-grand-exchange-design.md`). Known future hook.
- **Owned-POH altar tiers + self-supplied burner marrentill** — Construction.

### Implementation-time source extractions (mechanical, not decisions)
1. Full 30-prayer standard book table (levels, effects, drain rates) from
   game-main `prayer.kt` / `Prayers.kt`.
2. Full curse drain-rate column from `Ancient Curses`?oldid=6535713 (e.g.
   Turmoil / Soul Split 1 point per 0.2 s).
3. Sap/Leech per-proc step sizes and caps from Darkan `Sap.java` / `Leech.java`
   to drive the EV ramp.
4. Impious/accursed ashes pins (scatter XP, dropping monsters) and 100%-drop
   ash wiring for the demon families in `combat_data.py`.
5. Bonemeal item set (one per bone type) + ecto-token + bucket-of-slime item
   definitions, assets, and provenance.
6. Piety/Chivalry/King's Ransom/Knight Waves requirement pins.
7. Prayer renewal / Rapid Renewal per-tick restore rate pin.
8. Migrate any pending Prayer XP holdings the moment the surface flips
   `planned → complete` (same path the partial Combat skills used).

### Cross-cutting status

The then-current eleven-skill completeness audit is preserved in `gap-backlog.json`,
`gap-grill-decisions-2026-07-10.md`, and
`archive/2026-07/baselines/completion-audit.json`. Prayer's
kanban card moves to `IMPLEMENT` (with the extraction list above as its
`SOURCE AUDIT` residue) as of 2026-07-11.

## Post-implementation closure addendum — 2026-07-13

The design body above is preserved as the original contract. Its live status is now:

- Prayer shipped in `ed1327b`, and the altar/urn/passive/Herblore closure is complete in the 2026-07-13 working tree.
- The previously parked owned-POH altar dependency is closed: zero, one, and two burners yield 250%, 300%, and 350%; clean marrentill is consumed once per new owned stint.
- All 26 training-urn tiers across Mining, Cooking, Fishing, Woodcutting, Smithing, and Prayer ship with exact five-state source IDs, target-carried activation, overflow-preserving charge, substitution-aware bank repacks, and direct full-urn teleport.
- Bonecrusher and Ectoplasmator ship as target-carried passives without invented acquisition routes. Their icons use explicit RS3 wiki provenance.
- Direct urn teleports use a separate bounded LIFO custom undo and do not consume review undo.
- Chivalry/Rigour/Augury/Piety enforce their exact Defence gates, and the Qt surface explains Knight Waves locks.
- Source item IDs 4255 and 6810 remain distinct storage identities (`Bonemeal` and `Wyvern bonemeal`) even though the source display names collide; this supersedes the earlier gap-ledger collapse conclusion.

The authoritative conflict/test record is `source-audits/prayer-altar-urn-passives-herblore-closure-2026-07-13.md`; the live forward status is `future-work-kanban.md`.
