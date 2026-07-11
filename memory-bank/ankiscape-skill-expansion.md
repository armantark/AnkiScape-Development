# AnkiScape Skill Expansion

Focused continuation document for the partially completed **Prayer** deep grill.
It is not the global post-Herblore roadmap; that role now belongs to
`completion-audit-2026-07-10.md` and `future-work-kanban.md`.

Status: parked mid-grill on 2026-07-09 and refreshed 2026-07-11. Resume from the
settled decisions and open questions below; do not restart the Prayer design or
treat the tentative open values as implementation-ready.

Global status now lives in the completion kanban. The registry distinguishes
11 complete skill surfaces, six partial Combat-trained skills, and eight planned
skills; Prayer remains planned and must not be promoted merely because its save
keys and some Herblore/Combat dependencies exist. All source work below follows
`pre-eoc-source-verification-standard.md`: pinned pre-EOC wiki revisions and
period caches establish history, while 2011Scape/current Darkan code is
reconstruction evidence that must be reconciled. Never fill a gap from modern
RS3 or OSRS behavior.

---

## Parked continuation: Prayer

### Framing
Prayer is really two separable features wearing one name:

1. **Prayer training (the skill)** — consume a bone → gain Prayer XP. A one-action
   recipe-transform, the same engine shape as Herblore/Cooking. Low risk.
2. **Prayer points + protection prayers (the combat overlay)** — the drain-based
   combat layer (Protect from Melee, Piety, etc.). This is the hard part and the
   one with real balance questions.

The owner does **not** want v1/v2 phasing — build everything whose dependencies
already exist in one pass and tweak as we go. The only things that sit out are
*dependency-blocked*, not phase-deferred (see Parked).

### What already exists (no work needed)
- **Bone inputs flow from combat**: `"Bones"` on ~47 drop-table entries in
  `combat_data.py`, `"Big bones"` on 4, `"Wolf bones"` on 3. Like Herblore's
  economy phase, the inputs are already near their authentic ceiling.
- **Prayer-point restore economy already built via Herblore**: Prayer potion (3),
  Super prayer, Prayer renewal, Prayer mix are all live
  (`herblore_data.py:123,148,149,162`).
- **`prayer_level` already feeds the combat-level formula**
  (`logic_pure.py:4208`: `base = 0.25 * (defence + constitution + int(prayer*0.5)
  + int(summoning*0.5))`), and `prayer` is already in `_COMBAT_AFFECTABLE_SKILLS`
  (`logic_pure.py:1166`). So training a stat that already matters in combat.

### Sourcing (revised 2026-07-09 — game-main is incomplete, wiki fills gaps)
A GPT-5.6 audit confirmed game-main **stubs** three authentic pre-EOC Prayer
systems entirely: **ancient curses**, the **chaos-temple bone altar**, and the
**gilded altar** (only static object/item/sound metadata, no behaviour). Per the
revised gap-fill policy (see the `ankiscape-skill-expansion` skill's SKILL.md and
`wiki-parity-scrape.md`), these are now sourced from `runescape.wiki` pinned to
the eve of EOC (2012-11-20) via `tools/wiki_parity.py`, cited by `oldid`.

- **Bury XP per bone (game-main):** `content/skills/prayer/burying/BoneData.kt` +
  `bone_burying.plugin.kts`.
- **Protection-prayer drain rates + effects (game-main):**
  `content/mechanics/prayer/prayer.kt`, `Prayers.kt`. Drain resistance
  `60 + prayerBonus*2`; points stored internally as `level*10`. The wiki's
  bonus formula `interval * (1 + prayerBonus/30)` is the same model.
- **Ancient curses (wiki, `Ancient Curses`?oldid=6535713):** full ladder L50–95,
  effects, drain rates. game-main has none.
- **Gilded/POH altars (wiki, `Prayer`?oldid=6539264):** altar tier ladder
  Oak→Marble→Gilded, 100%–250%, +50%/+100% for 1/2 lit burners (clean marrentill
  + tinderbox), max 3.5×. game-main stubs it.
- **Ectofuntus (wiki, `Ectofuntus`):** flat **4×** bury XP via ground bonemeal +
  ectoplasm. game-main coverage TBD; treat as wiki-sourced.
- **Chaos Temple Wilderness altar (wiki, `Chaos Temple (Wilderness)`):** bonus
  offering XP + ~50% bone-save, wilderness risk. game-main stubs it.

### Training methods this pass (maximalist — owner: "everything to the utmost detail")
Roster surfaced by the wiki sweep; build all whose modeling is self-contained,
model dependency-gated ones with the owner's friction abstractions:
1. **Bury bones** — 1×, zero friction (game-main BoneData).
2. **Scatter demon ashes** — parallel to burying; demons drop ashes (newly listed).
3. **Ectofuntus** — 4×, two-step (grind bones→bonemeal + collect ectoplasm→worship).
4. **Gilded altar (POH)** — tiered up to 3.5× with burners; un-parked via the
   house-finding friction model (random 1–10 turns to "find a suitable house").
5. **Chaos Temple Wilderness altar** — bonus XP + ~50% bone-save + wilderness risk.
6. **Shades of Mort'ton cremation** — quest/activity-gated pyre-log + shade-remains
   method (heaviest dependency; may trail the others).
7. **Restless Ghost** — 5 one-time Ancient bones (minor landmark).

### Design decisions (agreed in grill)
- **No flicking.** It was not a 2012 core mechanic and there is no per-tick player
  input in a review-paced burst to represent it. Any flicking model would be an
  invented heuristic — excluded on parity grounds.
- **EV (expected-value) damage mitigation.** Protection prayers multiply each
  enemy hit by `(1 - uptime_fraction)` rather than binary per-hit blocking.
  Offensive prayers become effective-level multipliers scaled by uptime, applied
  pre-loop. Drain accrues per simulated tick at the authentic rate × uptime.
  Combat hooks: enemy damage `logic_pure.py:3502-3516`; pre-loop player
  accuracy/max-hit `3457-3486`; per-tick loop `3435`.
- **Efficiency via a player policy, not an assumed 100% uptime.** A per-combat
  toggle (Off / Conservative ≈40% / Aggressive ≈70% / Always 100%) maps to an
  uptime fraction applied to both the authentic per-tick drain and the authentic
  effect. Drain and effect are sourced; the uptime fractions are the *one*
  genuinely invented knob, tuned from telemetry.
- **Checkbox prayer selection.** A check-mark UI selects which prayers are enabled
  (each gated by unlock level), sharing the one uptime. Includes a "hide
  lower-tier prayers" toggle mirroring the in-game option.
- **All 30 standard prayers in** (full ladder Thick Skin 1 → Augury 77), plus the
  **full Ancient Curses book** (L50–95) as a second, toggleable book. Smite,
  Retribution, and Protect from Summoning included for completeness even if
  rarely used (Summoning hooks in when that skill lands).
- **Prayer points:** max = `prayer_level` (RS convention; internally `level*10`).
  Bank-run refill = restore to full, FREE, "as if stopping by an altar."
  Mid-burst restore = Prayer potions auto-drunk (like existing stat-potion
  auto-drink, `logic_pure.py:3331`). At 0 points with no potion, prayers switch
  off until the next bank-run refill.
- **Rapid Restore analog** via a new per-tick current-level decay model, mirroring
  how RuneScape drained stats recover — gives Rapid Restore/Renewal a real effect
  (`_combat_recover_current_levels`, `logic_pure.py:3192`).
- **Protect Item** is meaningful because death has real costs (graves equipment +
  carried inventory, `_combat_apply_pvm_death`, `logic_pure.py:1455`).
- **Automatic bank runs during combat refill Prayer points automatically**, as if
  stopping by an altar on the way back. Ties Prayer restore into the existing
  carried-inventory bank-run mechanic so combat with prayers on is self-sustaining.
- **Auto-bury-during-combat** folded in this pass as a combat toggle that spends
  extra simulated ticks per bone (off by default).

### Un-parked by the maximalist decision
- **Gilded altar** — no longer waits for full Construction. Built now with the
  owner's friction abstraction: a random 1–10 turns to "find a suitable player's
  house" when you lack your own gilded altar (mirrors house-party loaning). Real
  Construction, when it lands, replaces the friction with an owned altar.

### Still parked (dependency-blocked)
- **GE-bought bones** — needs the Grand Exchange (parked in
  `fake-grand-exchange-design.md`). When GE lands, add a coin-paid bone-buying
  training path. Note as a known future hook.

### Open decisions (to resolve in grill)
- Uptime fractions for the policy toggle (starting guess: Conservative ≈ 40%,
  Aggressive ≈ 70%).
- Chaos altar risk model (per-action chance to lose the bone stack / forfeit
  bonus, sourced parallel to wilderness rune-buying risk).
- Ectofuntus modeling: keep the two-step grind→worship friction, or collapse to a
  single higher-friction 4× action?
- Ancient curses PvE translation: how leech/sap (enemy stat drain + self boost)
  and deflect (protect + reflect a fraction) map onto the EV combat model.
- Rapid Restore per-tick current-level decay/recovery rate (the new analog).
- Shades of Mort'ton: build cremation this pass or trail it (heaviest dependency)?
- Where training lives in the UI (dedicated Prayer skill action vs Utility hub),
  and how the many methods are presented without clutter.

### Cross-cutting status

The eleven-skill completeness audit is no longer running. Its settled results
live in `gap-backlog.json`, `gap-grill-decisions-2026-07-10.md`, and the new
project-wide `completion-audit.json`. Prayer remains a separate deep-grill card.
