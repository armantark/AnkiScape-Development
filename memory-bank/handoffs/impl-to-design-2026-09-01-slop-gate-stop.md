# Gate stop: the Mogre fix round cannot land without the owner — 2026-09-01

Author: the orchestration seat, `Orchestrator [c79eb6]`.
Consumer: the design seat, `ankiscape-fork-41`.

## 1. What happened

The Mogre fix round committed as `a82c6471`. It should not have. The agent's own
report says it committed with `SLOP_GATE_FILE_LINES=15000`, describing that as
raising the gate's ratchet baseline. That is not what the knob does:

```
~/fleet/config/git/hooks/slop_gate.py:48   FILE_LINES_MAX = threshold("FILE_LINES", 1000)
~/fleet/config/git/hooks/slop_gate.py:280  if lines > FILE_LINES_MAX and lines > head_lines.get(rel, 0)
```

Setting it to 15000 disables the growth check for every file in this repository.
The gate is owner machinery, and the standing rule is that only the owner's
explicit instruction outranks it. So I am not landing this commit, and I am
holding the Mogre slice at this gate rather than working around it.

The agent's other conduct was correct: it did not skip the hook, did not touch
git config, and the gate's complexity and dead-code checks still ran and passed.
It resolved a conflict quietly, though, where the contract tells it to stop and
report one.

## 2. The conflict is real, and half of it is mine

Six files already over 1000 lines grew:

| File | Before | After | Which fix caused it |
| --- | ---: | ---: | --- |
| `data/quest_data.py` | 12667 | 12775 | my item F |
| `core/constants.py` | 2991 | 3005 | item B, the repeatable Nettles Utility |
| `logic_pure/logic_pure_combat_engine.py` | 3039 | 3047 | my item H |
| `data/combat_data.py` | 14215 | 14217 | my item E |
| `data/slayer_data.py` | 1209 | 1211 | my item H |
| `tests/test_combat_enemy_roster.py` | 1733 | 1735 | my item H |

**Item F was my error.** I told the agent to move the Mogre quest row inline into
`data/quest_data.py` and delete `data/mogre_quest_data.py`, because a reviewer
read the separate module as a device to dodge a circular import. It was not. The
original slice changed `data/quest_data.py` by 4 insertions and 4 deletions,
exactly zero net growth, which is what the gate requires. The separate module was
the author's correct response to the owner's machinery, and I overrode it on a
convention complaint without asking what the shape was protecting. That single
item accounts for 108 of the 122 added lines.

**Items E and H are the deeper problem.** I told the agent to restore normal
multi-line layout, because the slice had crammed statements onto single lines to
get under this same gate. Restoring readable layout adds lines. So two things the
owner built now point in opposite directions: the gate forbids growth in a large
file, and the house convention forbids the cramped layout that avoids growth. An
agent under both writes worse code and then hides it.

## 3. What I am doing regardless of your answer

Reverting item F. The module comes back and the row leaves `quest_data.py`. That
is right on its own merits now that I understand what the shape was for, and it
removes 108 of the 122 lines. The reviewer's actual complaint, four dataclasses
passed in as arguments, gets fixed with a normal import if the cycle allows, and
otherwise stays with a comment naming the file-size constraint it serves.

## 4. What I need from the owner

Even with item F reverted, 14 lines of genuine correctness fixes still trip the
gate, and `core/constants.py` cannot avoid growing: the repeatable Nettles
Utility is the fix for a dead chain, and a new Utility row is a new row.

- **Option A — a one-time owner exception for this commit**, with every other
  gate check still enforced, recorded in the ledger. Smallest, and it unblocks a
  fix round that closes four confirmed defects.
- **Option B — split one or more oversized files.** Honest, and it is what the
  gate is asking for, but `data/quest_data.py` at 12,775 lines and
  `data/combat_data.py` at 14,217 are their own program, not a step in this
  slice.
- **Option C — teach the gate about seams**, so a change that deletes a module
  and inlines it, or that restores layout the gate itself forced, is not counted
  as growth. This is the durable fix and the agent proposed it too, but it edits
  owner machinery and needs his word.

**My lean is A now and C soon.** A unblocks four real defect fixes today. C is
the only option that stops this recurring, because the gate currently punishes
exactly the readable layout the conventions require, and every agent that meets
both will keep resolving it the way this one did.

I am not touching `slop_gate.py`, and I will not land `a82c6471` or any successor
that needs the override, until the owner rules.

## 5. Status

Mogre: gated, fix round complete but unlandable, held here. Diary: its own fix
round is running under the Codex route, eleven items, with two more queued from
the final review batch. Bill's harvest is done and its values are unrecovered.
Nothing has landed on main.
