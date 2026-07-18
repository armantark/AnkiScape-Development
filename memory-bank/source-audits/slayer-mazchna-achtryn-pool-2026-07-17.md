# Slayer Mazchna/Achtryn assignment-pool audit — 2026-07-17

Status: **functional source contract provisionally closed; runtime hidden**.
Cutoff: `2012-11-20T23:59:59Z`.

## Finding

Mazchna's ordinary assignment pool contains 27 families. Achtryn is a temporary
While Guthix Sleeps presentation replacement for the same functional master
role, not a second pool or ledger. The cutoff master pages are useful but not
individually complete:

- Mazchna contains all 27 families, but an anonymous edit inflated the first
  eight task ranges from `40–70` to `40–85`;
- Achtryn preserves the older `40–70` range but omits Cyclopes and Grotworms;
- Darkan has executable rows for 25 families but cannot represent Mogres or
  Wall beasts because both task-family enum entries are comments; and
- game-main explicitly marks 10 Mazchna rows as unfinished and omits Grotworms.

The reconciled contract therefore uses the cutoff family table, the earlier
Jagex Knowledge Base correction preserved in page history, individual cutoff
monster pages, the cutoff cross-master table, and emulator convergence. Hidden
weights remain provisional. Mogre and Wall-beast weights are the smallest
labeled abstractions needed to complete the roll table.

## Reconciled ordinary pool

`Weight` is the raw hidden roll-table value, not a percentage. `Baseline` means
no family-specific assignment gate beyond access to this Combat-20 master.
Protective and finishing items are combat obligations, not reasons to silently
remove an otherwise eligible family from the roll.

| Family | Weight | Count | Assignment gate | Combat obligation | Provenance |
|---|---:|---:|---|---|---|
| Banshees | 20 | 40–70 | Slayer 15 | Earmuffs or an accepted Slayer-helmet equivalent | weight `provisional/darkan`; count `period-history+achtryn+darkan` |
| Bats | 10 | 40–70 | baseline | none | weight `provisional/darkan`; count `period-history+achtryn+darkan` |
| Bears | 10 | 40–70 | baseline | none | weight `provisional/darkan`; count `period-history+achtryn+darkan` |
| Catablepon | 10 | 40–70 | baseline | none | weight `provisional/darkan`; count `period-history+achtryn+darkan` |
| Cave crawlers | 20 | 40–70 | Slayer 10 | poison | weight `provisional/darkan`; count `period-history+achtryn+darkan` |
| Cave slimes | 10 | 40–70 | Slayer 17 | poison | weight `provisional/darkan`; count `period-history+achtryn+darkan` |
| Cockatrice | 20 | 40–70 | Slayer 25 | Mirror shield or accepted Slayer-helmet equivalent | weight `provisional/darkan`; count `period-history+achtryn+darkan` |
| Crawling hands | 20 | 40–70 | Slayer 5 | none | weight `provisional/darkan`; count `period-history+achtryn+darkan` |
| Cyclopes | 10 | 30–60 | Attack + Strength 130 | none | membership/count `period-history+cross-table+darkan`; gate/weight `provisional/darkan` |
| Desert lizards | 10 | 40–70 | Slayer 22 | Ice coolers for the finishing blow | weight/count `provisional/darkan`, count corroborated by period pages |
| Dogs | 10 | 40–70 | baseline | none | weight `provisional/darkan`; count `period-history+achtryn+darkan` |
| Flesh crawlers | 10 | 40–70 | baseline | none | weight `provisional/darkan`; count `period-history+achtryn+darkan` |
| Ghouls | 10 | 40–70 | baseline | none | weight `provisional/darkan`; count `period-history+achtryn+darkan` |
| Ghosts | 10 | 40–70 | baseline | none | weight `provisional/darkan`; count `period-history+achtryn+darkan` |
| Grotworms | 10 | 40–70 | baseline | none | membership/count `period-history+cross-table+monster-pages`; weight `provisional/darkan`; Darkan count rejected |
| Hill giants | 10 | 40–70 | baseline | none | weight `provisional/darkan`; count `period-history+achtryn+darkan` |
| Hobgoblins | 10 | 40–70 | baseline | none | weight `provisional/darkan`; count `period-history+achtryn+darkan` |
| Ice warriors | 10 | 40–70 | baseline | none | weight `provisional/darkan`; count `period-history+achtryn+darkan` |
| Kalphites | 10 | 40–70 | baseline | none | weight `provisional/darkan`; count `period-history+achtryn+darkan` |
| Mogres | 10 | 40–70 | Slayer 32 and Skippy and the Mogres | Fishing explosive or super fishing explosive to lure | membership/count `period-pages+cross-table`; weight `abstraction/common-mazchna-baseline` |
| Pyrefiends | 20 | 40–70 | Slayer 30 | none | weight `provisional/darkan`; count `period-history+achtryn+darkan` |
| Rock slugs | 15 | 40–70 | Slayer 20 | Bag of salt for the finishing blow | weight/count `provisional/darkan`, count corroborated by period pages |
| Skeletons | 10 | 40–70 | baseline | none | weight `provisional/darkan`; count `period-history+achtryn+darkan` |
| Vampyres | 10 | 40–70 | baseline | none beyond ordinary target mechanics | weight `provisional/darkan`; count `period-history+achtryn+darkan` |
| Wall beasts | 10 | 10–20 | Slayer 35 and Defence 5 | Spiny, spiked, Slayer, or full Slayer helmet | membership/count `period-pages+cross-table`; weight `abstraction/common-mazchna-baseline` |
| Wolves | 10 | 40–70 | baseline | none | weight `provisional/darkan`; count `period-history+achtryn+darkan` |
| Zombies | 10 | 40–70 | baseline | none | weight `provisional/darkan`; count `period-history+achtryn+darkan` |

The 25 executable Darkan rows total 305. The two missing families receive the
ordinary 10-point baseline, producing a provisional denominator of **325**.
Those two values are implementation abstractions, not recovered RuneScape
facts, and must stay labeled as such in data and telemetry.

## Count conflict resolution

RuneScape Wiki, `Mazchna`, oldid `4333869`, timestamp
`2011-05-29T09:53:13Z`, records an edit explicitly described as correcting task
size from the Jagex Knowledge Base:
<https://runescape.wiki/w/Mazchna?oldid=4333869>.

That revision changes the old shared `40–120` range to:

- `40–70` for Banshees through Crawling hands;
- `30–60` for Cyclopes;
- `40–70` for Desert lizards through the ordinary late-table families; and
- `10–20` for Wall beasts.

RuneScape Wiki, `Mazchna`, oldid `5496342`, timestamp
`2012-04-15T17:46:13Z`, is an anonymous, uncommented edit that changes only the
first shared range from `40–70` to `40–85`:
<https://runescape.wiki/w/Mazchna?oldid=5496342>.

That isolated value loses to three-way convergence:

1. the earlier Knowledge Base correction;
2. cutoff `Achtryn`, oldid `6584691`, timestamp
   `2012-11-19T11:24:59Z`, which still says `40–70`; and
3. Darkan's executable Mazchna rows, which say `40–70`.

The accepted count is therefore `40–70`, not `40–85`.

Grotworms initially entered Mazchna's table with a malformed shared-row span.
RuneScape Wiki, `Mazchna`, oldid `6298558`, timestamp
`2012-09-26T08:44:59Z`, explicitly changes that span from 14 to 15 rows:
<https://runescape.wiki/w/Mazchna?oldid=6298558>. Counting the enclosed rows
places Grotworms inside the `40–70` group. That direct period correction
outweighs Darkan's later `20–40` executable row.

## Family-membership resolution

The cutoff Mazchna page, oldid `6548393`, timestamp
`2012-11-11T21:24:57Z`, lists all 27 accepted families:
<https://runescape.wiki/w/Mazchna?oldid=6548393>.

The cutoff cross-master `Slayer assignment` table, oldid `6303852`, timestamp
`2012-09-27T13:49:08Z`, independently assigns Cyclopes, Grotworms, Mogres, and
Wall beasts to Mazchna:
<https://runescape.wiki/w/Slayer_assignment?oldid=6303852>.

Grotworms were added to the Mazchna page at oldid `5748303`, timestamp
`2012-06-12T15:26:12Z`, shortly after Song from the Depths:
<https://runescape.wiki/w/Mazchna?oldid=5748303>. The cutoff individual
`Grotworm` page, oldid `6600424`, timestamp `2012-11-20T19:01:44Z`, also marks
Mazchna as an assigning master:
<https://runescape.wiki/w/Grotworm?oldid=6600424>.

The cutoff individual pages close the other apparent emulator omissions:

- `Mogre`, oldid `6493220`, timestamp `2012-10-29T17:57:37Z`, marks Mazchna
  and states the Slayer-32 miniquest and lure requirements:
  <https://runescape.wiki/w/Mogre?oldid=6493220>.
- `Wall beast`, oldid `6079584`, timestamp `2012-08-11T23:52:21Z`, marks
  Mazchna, states Slayer 35 and Defence 5, and documents the helmet consequence:
  <https://runescape.wiki/w/Wall_beast?oldid=6079584>.
- `Cyclops`, oldid `6565802`, timestamp `2012-11-17T10:14:24Z`, marks Mazchna:
  <https://runescape.wiki/w/Cyclops?oldid=6565802>.

Achtryn's cutoff page omits Cyclopes and Grotworms, but the master-succession
contract proves Achtryn is only Mazchna's temporary presentation replacement.
The omissions do not create a smaller temporary pool.

Infernal mages are excluded. The cutoff cross-master table names Mazchna, but
Infernal mages never appear in Mazchna's own table history, no Mazchna count
survives, and the cutoff `Infernal Mage` page, oldid `6446423`, timestamp
`2012-10-20T01:07:22Z`, names only Vannaka and Chaeldar:
<https://runescape.wiki/w/Infernal_Mage?oldid=6446423>. This is a disputed
cross-table row, not a 28th executable family.

## Role and variant gates

Mazchna requires Combat 20. RuneScape Wiki, `Mazchna`, oldid `6112475`,
timestamp `2012-08-19T12:36:05Z`, also preserves Priest in Peril as the Canifis
access requirement before later infobox housekeeping removed that field:
<https://runescape.wiki/w/Mazchna?oldid=6112475>. Achtryn occupies the same
functional role only during the While Guthix Sleeps interval already closed in
the master-succession audit.

Family certification does not certify every qualifying variant. In particular,
the cutoff master and cross-master tables disagree over Terror dogs and several
Bat, Bear, Cyclops, and Vampyre variants. Mighty banshees additionally require
Slayer 35 and Smoking Kills. Those variant memberships remain `source_blocked`
and must be resolved in the stable family-to-variant registry before runtime
activation.

## Emulator evidence and limits

Darkan:

- `Task.java` contains 25 Mazchna rows with the weights and counts recorded
  above;
- `TaskMonster.java` leaves enum ids 61 (`WALL_BEASTS`) and 67 (`MOGRES`) as
  comments, explaining why the two otherwise period-attested families have no
  executable task rows; and
- the 25 executable weights total 305.

Pinned paths:

- `/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/src/main/java/com/rs/game/content/skills/slayer/Task.java`
- `/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/src/main/java/com/rs/game/content/skills/slayer/TaskMonster.java`

game-main's `SlayerMaster.kt` is an incomplete lower-fidelity implementation.
It includes 16 executable Mazchna families and marks Catablepon, Cyclopes,
Desert lizards, Dogs, Flesh crawlers, Hobgoblins, Kalphites, Mogres, Vampyres,
and Wall beasts as `TODO`; it does not mention Grotworms. It corroborates gates
for the families it does implement but cannot define the complete pool.

Pinned path:

- `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/skills/slayer/data/SlayerMaster.kt`

## Current AnkiScape readiness

This audit does **not** authorize a partial live Mazchna/Achtryn role.

- The complete 27-family pool now exists as hidden data. Stable family identity
  is separate from master-specific weight/count rows, so Mazchna's 325-point
  denominator cannot overwrite Turael's values.
- `tools/audit_slayer_readiness.py` derives blockers from the current Combat
  registry instead of trusting this dated prose snapshot. It reports 21/27
  families ready and keeps the role runtime-disabled.
- The exact remaining target blockers are Cyclopes, Kalphites, Mogres,
  Pyrefiends, Vampyres, and Wall beasts. When Mogre and Wall-beast targets land,
  the same audit will additionally require their lure and protective-equipment
  feature keys before certification.
- Banshee and Cockatrice protection, Cave-crawler and Cave-slime poison,
  Desert-lizard and Rockslug finishers, Dogs, Grotworms, and both Hobgoblin
  Slayer-XP rows are now executable and no longer appear as blockers.
- The audit rejects empty pools, duplicate families, invalid roll rows,
  denominator drift, enabled masters with blockers, and certified masters left
  hidden. Family membership remains explicit by stable id; display-name
  matching cannot admit Werewolves into Wolves.

No owner-level design choice is needed. The remaining blockers are source/data,
Combat-content, item-mechanics, quest-gate, and integration work.
