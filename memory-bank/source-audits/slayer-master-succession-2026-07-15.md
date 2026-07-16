# Slayer master quest succession audit — 2026-07-15

Status: **cutoff-live succession closed; runtime integration unimplemented**.
Cutoff: `2012-11-20T00:00:00Z`.

## Finding

While Guthix Sleeps is live at the cutoff and canonically changes the visible
Slayer-master roster. Turael and Duradel die during the quest. Upon completion,
Spria permanently replaces Turael and Lapalok permanently replaces Duradel.
Achtryn replaces Mazchna only during the quest; Mazchna survives and returns.

## Period evidence

1. RuneScape Wiki, `While Guthix Sleeps`, oldid `6584290`, timestamp
   `2012-11-19T10:55:09Z`:
   <https://runescape.wiki/w/While_Guthix_Sleeps?oldid=6584290>.

   The historical wikitext states that Lucien kills Turael and Duradel and its
   `Replaced characters` section records:

   - Turael to Spria;
   - Duradel to Lapalok; and
   - Mazchna to Achtryn only during the quest.

2. RuneScape Wiki, `Slayer Masters`, oldid `6461968`, timestamp
   `2012-10-23T20:43:28Z`:
   <https://runescape.wiki/w/Slayer_Masters?oldid=6461968>.

   The cutoff-period roster presents the functional pairs `Turael/Spria` and
   `Duradel/Lapalok`, corroborating that the successors occupy the same master
   roles and assignment surfaces.

3. AnkiScape's generated quest catalog already contains While Guthix Sleeps and
   its staged scaffolding in `quest_catalog_generated.py`. Under the permanent
   source standard, catalog presence is not proof of full quest fidelity; the
   Slayer implementation must consume the authoritative quest completion/stage
   state rather than infer succession from an unrelated action.

## Design consequence

- Stable Slayer-master role IDs persist across succession; visible NPC identity
  is derived from quest state.
- `Get assignment`, challenge copy, portraits, shop attribution, and task tips
  show the correct living or temporary master.
- The replacements do not duplicate assignment pools, point ledgers, streaks,
  or UI rows.
- Exact behavior for an assignment already active when the quest crosses a
  succession boundary remains a product detail to settle before implementation.
