# Rat Catchers player-access boundary, 2026-10-07

Static review inspected exact main `d919d479838724fd16bad91c1aff60d67ba488e3`.
The retained oldid `6589064` route is source-ready; this finding covers Rat Catchers only.
The settled [quest-cat ownership contract](summoning-pet-acquisition-2026-07-16.md#quest-cats) requires Gertrude completion to grant a real pet entity.
The [active-cat contract](summoning-pets-2026-07-16.md) requires the follower slot only for steps that need active cat behavior.
Current `logic_pure/logic_pure_quest.py:1372` adds ordinary inventory rewards; `tests/test_logic.py:10369` expects inventory `Kitten`.
Existing `ui/ui.py:27525` activation controls require a stored instance ID. `logic/pet_logic.py:121` activates that instance.
Root confirmed those source anchors and the production acquisition callers. Gertrude does not connect completion to a cat instance.
A complete route requires Gertrude completion, a real kitten entity, and the source-required cat stage and follower checks.
Inventory aliases, seeded prerequisite completion and removed gates do not satisfy this dependency.
The owner settled King Rat as an ordinary quest stage; unknown pet-combat numbers do not block that representation.
The poison-exchange test seeds prerequisites and supplies, and stops at the next sentinel. It is local evidence only.
A full quest slice must also obtain Snake charm during the route and grant cat-training access, rather than a free Wily cat.
The retained target contract is `/Users/ArmanTarkhanian1/Documents/2012scape with bots/memory-bank/audit/evidence/static/rat-catchers-target-contract.json`.
The reviewer performed no harvest, test, product execution or writes. Root performed source checks only.
