# Goal blocked: the acquisition program has no viable settled slice

Date: 2026-08-12

## What is blocked

The acquisition-completion program on `goal/acquire-2026-08-12` has exhausted
its settled queue. Curly root was the last untested candidate. Its player gates
are satisfiable, but the branch has only the Firemaking consumer and no Jadinko
Lair curly-vine Woodcutting producer. Every other remaining queue entry is
blocked by a named owner, source, dependency, or integration boundary recorded
in `memory-bank/audits/acquisition-queue-final-2026-08-12.md`.

The dominant blocker is the production quest-action emitter gap. The live quest
registry has 196 playable entries; 185 directly contain required actions that no
runtime path emits, and prerequisite closure raises the approximate completion
impact to 190 of 196. Authentic acquisition routes gated on those quests are
therefore inert for an ordinary player progressing from level one.

## What was tried

The day began from the corrected reachability baseline of 1,556 actions, 2,493
reachable items, 103 orphan inputs, and 102 blocked actions. The program:

- proved Bush snake, the Crab pair, Raw chompy, the four crafting moulds, Inferno
  adze, White tree sapling, Cursed magic logs, Magic essence (2), and Relicym's
  balm (2) are blocked by unavailable quest progression;
- kept Emerald lens and Shrunk ogleroot with their owning Darkan quest threads;
- did not establish a Spirit-roots producer and ruled out only the unsupported
  inference from ordinary spirit-tree roots, not the existence of another source;
- established that Skewer stick and Spider carcass need missing producers and a
  corrected returned-stick transformation;
- shipped the Polar kebbit quota repair in `baca063f`;
- shipped four Jadinko secondaries in `16375023`;
- shipped filled Dragon-impling jar loot in `a08827aa`; and
- finally source-pinned and mechanically probed Curly root, including positive
  controls and multiplicity checks, before classifying its missing producer.

Those shipped routes moved the graph to 1,562 actions, 2,503 reachable items, 97
orphan inputs, and 100 blocked actions. The final closeout is documentation-only,
so those numbers do not change.

## The single thing that would unblock it

Implement and verify the production quest-action emitter mechanism. It removes
the structural blocker affecting the large majority of the remaining queue and
allows each quest-gated acquisition route to be tested from an actually
reachable player state.
