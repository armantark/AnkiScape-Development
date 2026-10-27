# Witch's House diary and key qualification

**Held.** Owner authorization to correct the existing Witch's House journal and stage-gate/readout sequence for the diary deed and the basement glove gate before magnet acquisition. No product change is authorized. This report qualifies the source and complete path only.

Reference: `4ba68a4e266f4efeacba0e3f806b7015396ead74` at `/Users/armantarkhanian/ankiscape_worktrees/pool/.treehouse/AnkiScape-091389/2/AnkiScape`. The cutoff is `2012-11-20T00:00:00Z`. All repository Markdown came from `git show` at that revision. Measurements below came from raw bytes at `2026-10-15T14:58:52.281908+00:00`. Root owns every mutable resource except these two output files.

## The old assertion and the source

The June 22 audit correctly described the older Darkan handler. It was not an owner decision to omit the diary forever. Original commit `1bc2d48174b6319eb0878b9c905d2578e36100db` has a diary item and a Read handler. That handler only opens the book. Its fountain handler grants item2411 without a diary check. The original spawn file supplies diary item2408 at `(2895, 3371, 0)`.

The literal period guide says: `You must read the diary in order to obtain the key.` This is Witch's House oldid6474931, `2012-10-26T12:16:36Z`, line43. Earlier oldid5933243, `2012-07-14T10:22:31Z`, line43 states the same gate. These revisions are one Wiki lineage. Diary oldid5849371, `2012-06-27T19:24:38Z`, lines53–54 supplies the mouse mechanism and fountain clue.

Restoration `88db0f79dfa881b21db697646b27ce5157b69eab` adds READ_DIARY on Read and checks it before the fountain key. Supply `c73c79aae7d5fb45e7677376f70fb108447c8dd2` retains that gate. The restored handler agrees with the period guide. It does not provide independent historical corroboration. The original handler contradicts the mandatory gate; its omission does not override the period prose. Cache727 proves item identities and gate/box options only. It cannot prove the diary gate. This packet makes no complete historical parity claim.

## Complete actual journal

The existing journal contains these exact rows. The last row contains two separate strings.

1. Harvey asked me to get his ball back from the witch's garden.
2. I found the front door key under a potted plant.
3. I entered the Witch's house and need to investigate the security system.
4. I found a magnet in the cupboard.
5. The mouse-hole mechanism needs cheese and the magnet.
6. The back of the house is open, but the witch patrols the hall.
7. I reached the electric gate and need gloves before touching it.
8. I passed the electric gate and should search the fountain for the shed key.
9. I found the backroom key and can unlock the shed.
10. The Witch's experiment is guarding the ball in the shed.
11. The experiment is defeated. I can pick up the ball and return it to Harvey.
12. Harvey got his ball back. / Quest complete!

The engine exposes row1 after start. Each successful stage transaction advances progress. The UI strikes every earlier row. Thus a journal change affects the existing UI.

## Complete actual ordinary path

The current composed row has no quest prerequisites, skill prerequisites, quest-point gate or start items. Actual prerequisite IDs `[]` equal disposition IDs `[]`. Combat19/30/42/53 describes the four enemies; it is not a required player start level.

| Current stage | Ordinary deed and custody | Qualification |
|---|---|---|
| Start | Accept Harvey's request. Journal1 is visible. | The period guide line34 and original boy dialogue support the request. |
| 1 | Search the potted plant; produce Door key1. | The period guide line36 and original handler support the producer. |
| 2 | Hold Door key; auto-action enters the house. | Keep the existing ordinary auto-action. |
| 3 | Search cupboard; produce Magnet1. | Current model grants the magnet before its insulating glove gate. |
| 4 | Consume Cheese1; retain Magnet; auto-action attaches magnet to mouse. | Keep the real input consumption and existing ordinary auto-action. |
| 5 | Auto-action passes the witch's patrol. | Keep the existing target-local successful route. Do not inject a later route flag. |
| 6 | Require reusable Leather gloves. | Gloves in inventory satisfy the current tool check. It does not require worn gloves. |
| 7 | Search fountain; produce Backroom key1. | No diary item, diary read proof or prior-read check exists in this path. |
| 8 | Hold Backroom key; auto-action unlocks shed. | Keep earned key custody and the existing ordinary auto-action. |
| 9 | Defeat the four stat-bearing experiment encounters. | Keep all four encounter identities and their data. No fight proof ran in this task. |
| 10 | Produce Ball1 after the four fights. | Keep the actual pickup after combat. |
| 11 | Consume Ball1; auto-action returns it to Harvey. | Keep the actual hand-in and single completion. |
| 12 | Show completion. | Preserve the current reward contract; no reward proof ran here. |

No source or code change occurred. This table describes the retained path, not a new product proof.

## Why unchanged UI is not enough

The source path enters the house, reads the diary, obtains or wears insulating gloves, passes the basement gate, then searches the cupboard. Period guide lines43/45/49 give that sequence. The current journal instead claims magnet receipt before the glove gate. It places the gate after the mouse and patrol. Journal7 explicitly says the player still needs gloves at that later point.

A hidden READ_DIARY flag alone does not repair the whole path. A same-transaction required flag and auto-action also fails: the engine checks blockers before it records auto-actions. A seeded diary, flag, key or completed prerequisite does not prove the ordinary deed. A spatial proxy is not a diary read.

The existing widgets can support a corrected path. No separate dialogue or new interface is proved necessary. However, this task cannot silently change the existing journal, gate placement or visible blocker text. The source alone does not authorize those changes. This is the first hold. Root must obtain the owner decision before product work.

## Conditional implementation contract after the hold

1. Preserve Harvey's complete request and the earned potted-plant Door key.
2. Add ordinary diary acquisition after house entry. Retain diary item2408 as the source identity.
3. Record the diary Read deed only after ordinary diary access. Do not grant fountain-key credit from mere quest progress.
4. Place the insulating glove gate before cupboard/magnet access. Keep gloves reusable. Preserve an ordinary source for gloves.
5. Preserve the Cheese transaction, magnet deed, target-local patrol and earned shed-key custody.
6. Require an earlier diary Read proof before the fountain produces Backroom key.
7. Preserve the four actual experiment fights, Ball pickup and single Ball hand-in.
8. Use ordinary review actions for every deed. Do not require manual proof injection or seeded state.
9. Keep backend scope explicit. Correct existing journal/readout only within the owner's approved frontend scope.

The period guide says gloves can come from basement boxes. Supply c73c79aae adds that source, object24692, with quest and inventory checks. The present AnkiScape route only requires owned Leather gloves. Diary acquisition, Read proof, fountain custody and correct gate order remain implementation work. This report does not classify those missing paths as impossible.

## Exact disputes for Root

- The June22 no-diary statement describes the original implementation, not the period gate or the later restoration.
- The mandatory diary gate has explicit period proof. The restored handler cannot count as an independent second historical layer.
- The whole actual journal conflicts with source order at the glove gate. Root must settle owner scope for the existing journal/readout.
- A successful target-local patrol remains accepted for the retained route. No new catch simulation or global location model is authorized.
- Period guide line65 describes key loss when caught before shed access. Line81 states both doors remain unlocked after the later escape. Do not erase these contexts or invent a global catch rule.

No broader absence conclusion follows from this bounded read. The first unblock remains the owner decision above. All later source or product proof remains unclaimed.

## Provenance and boundaries

The JSON manifest retains full paths, fixed revisions, timestamps, byte counts, SHA256 values and selected literal lines. It references original raw bodies. It embeds no full body, prior packet or cache payload. It also records exact inspection friction for Root to transfer to the owned papercut record.

- `1bc2d48174b6319eb0878b9c905d2578e36100db` — `2021-12-19T09:02:17-06:00` — Implemented Witch's House
- `88db0f79dfa881b21db697646b27ce5157b69eab` — `2026-07-10T20:18:45-07:00` — Restore Witch's House target-era mechanics.
- `c73c79aae7d5fb45e7677376f70fb108447c8dd2` — `2026-07-10T20:37:49-07:00` — Complete Witch's House basement supply behavior.
- `fd0e202de3a9d4ebdbfa2c0f297f20ecca7e768b` — `2021-12-19T09:02:17-06:00` — Implemented Witch's House

Only `/Users/armantarkhanian/Documents/ankiscape-goal-evidence-2026-10-14/witchs-house-diary-key-qualification-2026-10-15/report.md` and `/Users/armantarkhanian/Documents/ankiscape-goal-evidence-2026-10-14/witchs-house-diary-key-qualification-2026-10-15/qualification.json` were written. No registry import, source harvest, test, audit, decoder, product probe or native check ran. No repository, source, Git, UI, profile, collection or lease changed. No child agent or sibling/session message occurred. No product acceptance, promotion or source exhaustion is claimed.
