# Darkan quest agent handoff — 2026-07-18

This Slayer slice did not implement or edit quest content.

The current generated Jungle Potion objectives still need the Darkan quest
parity pass to replace the unreachable clean-herb/blocker sequence. Existing
source work already recovered the relevant ordinary shape: Druidic Ritual and
Herblore 3 to start, five sequential herb stages, 2.5 Herblore XP per clean
herb, and 775 Herblore XP plus one quest point on completion. If the quest
runtime cannot award per-stage XP yet, add that as a quest-owned schema and
migration rather than special-casing Slayer or Combat.

