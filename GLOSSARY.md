# Glossary

Domain terms with one settled meaning each. Implementation detail stays out.

- **Bank Claims** — the Bank tab's inbox of pending claimable rewards. A claim
  row persists until the player claims it; it is the delivery surface for
  deferred rewards such as XP lamps.
- **Carried view** — the projection of the single item ledger that shows what
  the player carries right now (retained loot plus remaining supplies). It is
  not a second ledger; the Bank and the carried pack share one ledger.
- **Deed task** — a diary row whose completion requires a performed action. A
  level or quest prerequisite on a deed task is an access gate, never the
  trigger.
- **Dormant task** — a deed task whose designed trigger awaits a named,
  plausible future game system. Its trigger is fully designed and recorded in
  the curation ledger; the row activates when its system lands. A dormant task
  differs from the retired "latent" stub, which had no designed trigger at
  all. A deed that can never translate must not be dormant; it is swapped or
  translated instead.
- **Translated deed** — a diary deed rebuilt for AnkiScape from a source deed
  whose literal form does not exist here (for example, world traversal). It
  keeps the source's region, family, and difficulty. In the game it carries
  its own name and sentence with no reference to the source deed; the source
  lives only in the curation ledger, which marks every translation.
- **Invented deed** — a diary deed written from scratch in the spirit of its
  region and tier, used when no honest translation of the source deed
  survives. Like a translated deed, it shows no reference to the source.
- **Curation ledger** — the reviewable per-task table (task → trigger →
  source citation → translation flag) that authorizes diary wiring. Wiring
  that bypasses the ledger is invalid.
- **Action** — the one skill, activity, or utility that reviews advance for
  the player. The player has exactly one action at a time. Combat is the action
  "attack" against a chosen target.
- **Action queue** — an ordered list of up to five actions, each with a count
  in that action's own unit (bars made, logs cut, kills), that reviews work
  through once from top to bottom. An add starts the queue at once, in place
  of whatever runs, unless the queue already runs. The player can move entries
  up and down; a new top entry starts at once and the old one keeps its
  remaining count. The player can remove any entry; removing the running top
  entry starts the next one. Whole lots stay whole even when the last lot
  exceeds the count. The rest of that card's play goes to the next entry when eligible;
  otherwise the successor can begin next card. A finished or stopped entry
  leaves the queue, and a finished quest removes every entry for that quest. An action started
  ahead of the queue runs until it stops by itself and the queue then continues
  from its top entry; a free pickup started that way runs until Stop or an add.
  Stop on a running entry pauses the queue at Bankstanding. A queue change
  shows no dialog: an entry that cannot start is skipped with a log line and a
  Review HUD line. Only a Clear, or an empty queue, ends at Bankstanding. Avoid:
  "loop", "task list".
- **Bankstanding** — the neutral action every ended session lands on. An
  automatic switch to Bankstanding notifies the player; a manual Stop does not.
- **Bank run** — the trip from an action to the bank and back. It takes a fixed
  amount of 2012 play time at every game speed, so its cost in cards follows the
  speed. Agility shortens the walking part. A bank run always completes its
  bank transaction.
- **Supply step** — one quest card in which the quest makes, picks up or buys
  an item it needs, as the player would during the 2012 quest (asking Aggie for
  a dye, mixing it, dyeing goblin mail). It pays the period price, gives the
  period XP and never starts a fight. A supply step whose product the player
  already holds is skipped; one the player lacks the coins, level or equipment
  for stops the quest and names what is missing.
- **Quest wear** — the quest card puts on an item its step needs. The old item
  returns at the first bank run after the quest stops needing the slot, or at
  once if the quest ends or stops first. A change of that slot by hand cancels
  the return.
- **Free pickup** — an action that gives an item and needs no input item and no
  tool, such as picking bananas or searching the Goblin Village crates.
- **Coming soon** — the state of a quest that a player cannot finish from a new
  save yet, and of content that needs such a quest. It cannot be started.
- **Review HUD** — the compact box under each card in the reviewer that shows
  the current action, its progress and its buttons. Avoid: "activity widget".
- **Encounter** — one fight against one enemy that persists between reviews:
  the enemy's remaining life points and the attack countdowns carry from card
  to card. An encounter lives only while the action stays combat against the
  same target. A kill, a death, a flee, a bank run, or any action change ends
  it, and the next fight starts a fresh enemy. Nothing is locked while an
  encounter is alive.
- **XP lamp** — a Bank Claim that pays XP. A fixed-skill lamp pays its one
  skill when claimed; a choice lamp opens the skill grid first. Destroying a
  lamp forfeits it for good.
- **XP drop** — the line that shows the XP one review gained, per skill, as
  the popup and in the event log. It shows the change in each skill's
  whole-number total, so tenths carry forward: four 4.5 XP burials read +4,
  +5, +4, +5. A skill whose whole number did not change is left out.

- **Game speed** — the amount of 2012 play time that one answered card buys, relative to the base pace.
- **World day** — the game’s daily calendar span, expressed in answered cards, with active play inside it and logged-out time between days.
- **Period source** — a record made before the 20 November 2012 cutoff: a RuneScape Wiki revision, an archived guide page, or an official update post. A wiki revision up to 20 November 2013 also counts for a passage that no later update changed. Current wiki pages and Darkan are not period sources.
- **Darkan** — the owner's high-fidelity restoration of the November 2012 game server. Its behavior stands in where the period sources are silent, as a placeholder. Avoid: "reconstruction", "restoration", "modern server".
- **Placeholder** — a value or behavior that the 2012 game had and that AnkiScape could not recover, shipped with a marker so that a later source find replaces it. It never stands for content that the period record does not attest.
