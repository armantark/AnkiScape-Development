# AnkiScape grind-loop queue

Source: `memory-bank/codex-briefs/ankiscape-grind-loop-2026-08-03.md`.
Process one unblocked item per iteration. Move discovered design gaps to
`memory-bank/design-thread-queue.md`.

1. [x] Pass 6 item B.15 — skill-selector hybridization.
   Implement only `memory-bank/codex-briefs/pass6-b15-handoff-2026-08-03.md`.
2. [x] Design answer 3.25 — guardian coin drops.
   Remove the Dungeoneering starter Herblore coin cache and pay the registered
   guardian-room placeholder on critical-path C5+ floors.
3. [x] The 384-diary-task clause.
   Implement the 32 tiers of 12 curated tasks settled in
   `memory-bank/achievement-diary-item-grants-design.md`.
4. [ ] Depth work.
   Start with `memory-bank/breadth-next-tranche.md`, then process registered
   placeholders and player-visible data-depth debt from `activeContext.md`.
   - [x] Decode period-cache enums, structs, and params.
   - [x] Decode interface definitions.
   - [x] Re-walk client-side `source_blocked` rows; leave server-side gaps alone.
     Rev-727 Conquest NPC params retire the Foot Soldier cost conflict at 50;
     diary lamp floors and the remaining server-owned formulas stay blocked.
   - [x] Decode exact item model/recolour rows and re-walk item-identity and
     asset placeholders. Rev-727 fixes the Temple Trekking blue/yellow swap;
     rev-741 fixes all four Goblin Raids equipment IDs, trade rules, and bonus
     arrays. Dominion Tower's unknown reward IDs remain source-blocked.
   - [ ] Retire the Achievement Diary's recorded depth debt: make the generator
     input portable and add the missing v108 revalidation migration regression.
