# Overnight content recon — 2026-07-19

Cutoff: RuneScape gameplay available strictly before `2012-11-20T00:00:00Z`.

Purpose: establish the append-only baseline for the live-index overnight recon
promised by `memory-bank/source-audits/recon-coverage-closure-2026-07-18.md:100-105`.
This file tracks discovery only. It does not reopen owner decisions, promote
source leads into period facts, or count already-owned work as a new finding.

Research hard stop: **2026-07-19 07:25 PDT**.

Report finalization deadline: **2026-07-19 07:30 PDT**.

## Operating state

| Field | State |
|---|---|
| Required sweep complete | **No** — Passes 0, 1, and the 2010–2012 update chronology are complete; the implementation-tree inventory is partial, while the archive, cache, local-seam, and convergence passes remain incomplete |
| Current pass | **Deadline closure — honest incomplete checkpoint** |
| New candidates this pass | **0** — the partial final-source pass did not admit a new candidate |
| Cumulative candidates | **4** |
| Consecutive zero-new convergence passes | **0** — an incomplete source pass does not count toward convergence |
| Early-stop reached | **No** — the hard deadline won before convergence |
| Last checkpoint time | **2026-07-19 07:32 PDT** |

## Stop rule

**Complete every required source-family pass once; afterward, stop substantive
recon after three consecutive materially distinct passes find zero new
candidates.**

The deadline overrides convergence: stop research at `07:25 PDT` even if the
three-pass condition has not been reached, then preserve the honest incomplete
state and finalize this report by `07:30 PDT`. Baseline reconciliation, rerunning
the same query, changing capitalization, or re-sorting the same result set does
not count as a materially distinct pass.

## Candidate admission and duplicate lock

A row may enter the ranked candidate list only when all of these are true:

1. Period evidence establishes that the gameplay surface was live before the
   cutoff. A modern RS3 or OSRS page is a lead, never independent proof.
2. The surface has review-native gameplay consequences: requirements, agency,
   risk, rewards, progression, persistent state, or a distinct loop. A name,
   client-side definition, transport-only interaction, cosmetic, or world-map
   affordance is insufficient.
3. The surface is absent from the canonical board and wider family ledger, or it
   is merely named with no owning contract, card, family, implementation, parked
   disposition, exclusion, or source-waiting row.
4. Exact repository searches do not resolve it to an implementation, focused
   audit, settled design, pattern owner, dependency owner, or backlog item.

The following are **not new findings**, even when a later pass rediscovers their
names: shipped/merged work; source-blocked or `WAIT: DARKAN` rows; split-scope
work; owner-settled forks; pattern-determined surfaces; parked sequencing;
explicit exclusions; post-cutoff/OSRS-only content; transport-only systems;
generic multiplayer/social layers; and a variant already owned by a broader
complete family. This follows the canonical label contract and duplicate rule
at `memory-bank/future-work-kanban.md:7-15,156-161`, the settled recon dispositions
at `memory-bank/source-audits/recon-coverage-closure-2026-07-18.md:7-69`, and the
wider-family/exclusion ledgers at
`memory-bank/ankiscape-completion-starter-grill-2026-07-17.md:631-744`.

When documents conflict, use this authority order:

1. current implementation plus its dated focused source/closure audit;
2. `memory-bank/future-work-kanban.md`, the canonical forward board;
3. `memory-bank/gap-backlog.json`, the shipped-skill subledger;
4. the completion starter's wider family ledger;
5. archived baselines and stale prose.

This prevents an old sentence from resurrecting closed work. For example, the
starter packet once called Warriors' Guild unowned
(`memory-bank/ankiscape-completion-starter-grill-2026-07-17.md:704-705`), but the
current board records its executable closure
(`memory-bank/future-work-kanban.md:378-384`) and the focused implementation
audit supplies pinned period citations
(`memory-bank/source-audits/warriors-guild-live-implementation-2026-07-18.md:1-23`).

## Required source-family coverage matrix

Every row below is required once before `Required sweep complete` can become
`Yes`. Later convergence passes must rotate query shape or evidence seam.

| Required pass | What it can establish | Baseline state | Completion evidence required |
|---|---|---|---|
| Canonical local ledger and ownership reconciliation | Existing ownership, status, exclusions, duplicate names | **Complete (Pass 0)** | Full current Kanban, gap subledger, wider family ledger, closure audit, and exact repo grep reconciled |
| Darkan content tree | Candidate server loops, hidden state, tables, rewards, and local restoration ownership | Pending | Enumerated gameplay entry points and content registries diffed by normalized surface name; exact path and commit recorded |
| OpenRS2 rev 727 | Client identities/config paired with Darkan | Pending | Candidate NPC/object/item/interface names and options checked; never treated as independent Darkan corroboration |
| 2011Scape/game-main rev 667 | Independent runtime-bound gameplay families and mechanics | Pending | Plugin/action bindings and data families enumerated; metadata without a binding rejected |
| OpenRS2 revs 728, 729, 736, 741, and 742 | Near-cutoff client identities, introductions, removals, and option changes | Pending | Cross-build identity/options diff with rev 742 preferred and November 8–19 limitation recorded |
| Pinned RuneScape Wiki indices and literal historical wikitext | Pre-cutoff existence, named mechanics, gates, rewards, and stated values | **Complete (Pass 1)** | Minigames/activity, D&D, miniquest, boss, members/F2P/P2P, skill, task/diary, Treasure Trails, reward-shop, random-event, and repeatable-system indices enumerated; redirects, period dependencies, and talk seams checked sequentially |
| Dated Wayback/official guide and update indices | Missing/moved history, official releases/removals, and wiki dependency gaps | **Partial (Pass 2A)** — the complete 2010–2012 update chronology through 2012-11-19 and every linked period update page are closed; unrelated official-guide/Wayback gaps remain pending | Dated captures recorded only where they add or resolve a candidate |
| Local implementation and audit seam diff | Whether a period surface is absent, named-only, implemented, or owned elsewhere | Pending | Exact `rg` evidence across code, tests, assets, audits, contracts, Kanban, and backlog for every admitted candidate |

The source roles above come directly from
`memory-bank/pre-eoc-source-verification-standard.md:90-132,145-178,181-209`.
In particular, rev 727 and Darkan are one source layer, caches prove client
identity rather than server mechanics, and modern pages may locate questions
but cannot independently close parity.

## Gameplay-surface coverage matrix

This matrix prevents a source pass from over-sampling familiar skill pages while
missing a whole kind of gameplay. `Ledger baseline` means the existing corpus
has an owner or disposition; it does **not** mean historical completeness.

| Surface family | Existing ledger anchor | Ledger baseline | Historical source sweep |
|---|---|---:|---:|
| Ordinary skill methods, special methods, boosts, and equipment effects | Kanban existing-skill ledger and `gap-backlog.json` | Reconciled | Wiki Pass 1 and 2010–2012 update chronology complete; other source families pending |
| Skill-owned activities | Artisan's Workshop through Gnome Restaurant in the wider family ledger | Named/owned | Wiki Pass 1 complete; other source families pending |
| Cooperative or simulated-population activities | Pest Control, Barbarian Assault, Fishing Trawler, Trouble Brewing, Shades of Mort'ton, Temple Trekking | Settled family scope | Wiki Pass 1 complete; other source families pending |
| Competitive activities | FoG, GOP, Stealing Creation, Castle Wars, Soul Wars, Conquest, Clan Wars, Duel Arena, Mobilising Armies | Settled family scope | Wiki Pass 1 complete; other source families pending |
| Recurring D&Ds and world events | Tears through Jade Vine, plus Daily Challenges and Goblin Raids | Named/owned or owner-settled | Wiki Pass 1 complete; other source families pending |
| Combat instances, bosses, encounter contexts, and bestiary | Barrows/Fight Caves/God Wars family plus boss-instance contract and bestiary program | Named/owned or pattern-determined | Wiki Pass 1 complete; other source families pending |
| Quests, miniquests, quest-boss replay, and unlock promises | 167-definition program, 27-fidelity program, representative-breadth ledger | Owned program | Wiki Pass 1 complete; other source families pending |
| Management, delivery/task loops, services, and economy | Miscellania, Daily Challenges, WOM/Keldagrim/Dorgesh-Kaan tasks, shops/GE programs | Named/owned or owner-settled | Wiki Pass 1 and 2010–2012 update chronology complete; other source families pending |
| Diaries, clues, collections, museums, kudos, and one-time finds | Diary/clue/collection Kanban card plus Museum and Enchanted-key dispositions | Named/owned or owner-settled | Wiki Pass 1 complete; other source families pending |
| Acquisition, transformations, charges, degradation, repair, and item effects | Reachability/equipment program and shared charged-equipment dependency | Owned program | Wiki Pass 1 complete; other source families pending |
| Random events and removed content | Random/timed-world Kanban card and exclusion ledger | Owned audit/exclusion | Wiki Pass 1 complete; exact removal boundary verified |
| Transport, world-map, social, cosmetic, post-cutoff, and inert-preview boundaries | Explicit exclusion ledgers | Excluded/parked | Wiki Pass 1 exclusion check complete; other source families pending |

The named family anchors are at
`memory-bank/ankiscape-completion-starter-grill-2026-07-17.md:631-680,682-744`.
The canonical forward cards for special methods, activities, bosses,
diaries/collections, random content, and exclusions are at
`memory-bank/future-work-kanban.md:682-794,925-930`.

## Baseline ledger reconciliation

The shipped-skill subledger contains 45 cards. Its current status distribution
is:

| Count | Status | Baseline disposition |
|---:|---|---|
| 22 | `merged` | Shipped; duplicate |
| 13 | `design_settled_waiting_source` | Owned source wait; duplicate |
| 4 | `split_scope` | Child owners already assigned; duplicate |
| 1 | `source_blocked_waiting_darkan` | Owned source wait; duplicate |
| 1 | `parked_farming_seed` | Parked/owned; duplicate |
| 1 | `design_partial_waiting_source` | Owned source wait; duplicate |
| 1 | `design_settled` | Parent decision; duplicate |
| 1 | `rejected_out_of_period` | Excluded; duplicate |
| 1 | `rejected_product_scope` | Excluded; duplicate |

This matches the canonical prose summary at
`memory-bank/future-work-kanban.md:156-161`. No backlog card is eligible to become
a new overnight candidate merely because it is not yet implemented.

The two prior Sol recon passes are also closed against duplication. Daily
Challenges, The Crucible, Court Cases, Varrock Museum Kudos, Enchanted key, and
Goblin Raids are owner-settled forks. Bosses, competitive duels, skill-owned
activities, delivery loops, Stronghold of Player Safety, Ancient Effigies, and
Oo'glog spa buffs are pattern-determined under named owners
(`memory-bank/source-audits/recon-coverage-closure-2026-07-18.md:15-62`).

## Pass 1 — pinned RuneScape Wiki gameplay indices

All API fetches in this pass were issued sequentially. Each row uses the nearest
useful revision strictly before the cutoff and was read as literal wikitext,
not as a modern render. Index aliases, nav/data dependencies, and the nearest
pre-cutoff talk revision were checked separately.

| Requested family | Pinned period evidence | Redirect/dependency/talk disposition | Coverage result |
|---|---|---|---|
| Minigames and activity | [`Minigames` oldid 6457342, 2012-10-23](https://runescape.wiki/w/Minigames?oldid=6457342) literally enumerates PvP/monster, skill, combat-skilling, and miscellaneous tables; [`Template:Minigames` oldid 6288458, 2012-09-24](https://runescape.wiki/w/Template:Minigames?oldid=6288458) independently enumerates team, solo, PvP, and former groups. | Period [`Activity` oldid 4670379](https://runescape.wiki/w/Activity?oldid=4670379) and [`Activities` oldid 4664942](https://runescape.wiki/w/Activities?oldid=4664942) both redirect to `Minigames`. [`Talk:Minigames` oldid 5574573, 2012-05-06](https://runescape.wiki/w/Talk:Minigames?oldid=5574573) was read through its missing-content/classification threads. | Complete for this source family; the talk seam produced the Chimp ice candidate below. |
| Distractions and Diversions | [`Distractions and Diversions` oldid 6566832, 2012-11-17](https://runescape.wiki/w/Distractions_and_Diversions?oldid=6566832) has literal sections from Ancient effigies through Big Chinchompa. | The page calls `{{Dnd}}`; the period dependency survives as [`Template:Distractions and Diversions` oldid 6155878, 2012-08-28](https://runescape.wiki/w/Template:Distractions_and_Diversions?oldid=6155878), while the current short-title template has no pre-cutoff history. [`Talk:Distractions and Diversions` oldid 5667161](https://runescape.wiki/w/Talk:Distractions_and_Diversions?oldid=5667161) was checked. | Complete. Existing D&D owners cover the live list. Shattered Heart's classification dispute changes no gameplay ownership; Chase the Monkey is rejected below. |
| Miniquests | [`Miniquests` oldid 6020341, 2012-07-31](https://runescape.wiki/w/Miniquests?oldid=6020341) literally lists requirements, rewards, start points, and membership for the period rows. | Period [`Miniquest` oldid 3630562](https://runescape.wiki/w/Miniquest?oldid=3630562) redirects to the plural title. [`Talk:Miniquests` oldid 3727652](https://runescape.wiki/w/Talk:Miniquests?oldid=3727652) was checked for Mage Arena/Phoenix and classification omissions. | Complete. Rows resolve to the existing miniquest/quest, activity, skill-unlock, or exclusion families. |
| Bosses | [`Bosses` oldid 6550006, 2012-11-12](https://runescape.wiki/w/Bosses?oldid=6550006) literally separates common PvM, God Wars generals, minigame, quest, Dominion Tower, and Dungeoneering bosses. | The current singular `Boss` resolves to `Bosses`, but neither `Talk:Boss` nor `Talk:Bosses` exposes a pre-cutoff revision under the present titles. | Complete. Every row is already under the boss-instance, bestiary, activity, quest-boss, or Dungeoneering owner. |
| Members and pay-to-play | [`Members` oldid 6269516, 2012-09-20](https://runescape.wiki/w/Members?oldid=6269516) literally inventories extra skills, activities, D&Ds, equipment, quests, bosses, pets, houses, task system, and other benefits. | Period [`Pay-to-play` oldid 666131](https://runescape.wiki/w/Pay-to-play?oldid=666131) redirects to `Members`; [`Talk:Members` oldid 5987265](https://runescape.wiki/w/Talk:Members?oldid=5987265) was checked. | Complete. Gameplay-bearing rows map to existing owners; transport/social/cosmetic/subscription-only rows retain their exclusions or parked dispositions. |
| Free-to-play | [`Free-to-play` oldid 6447227, 2012-10-20](https://runescape.wiki/w/Free-to-play?oldid=6447227) supplies the period overview and the literal free-update list. | [`Talk:Free-to-play` oldid 5152661](https://runescape.wiki/w/Talk:Free-to-play?oldid=5152661) was checked for scope/count disputes. | Complete; no new gameplay surface. |
| Skills | [`Skills` oldid 6579775, 2012-11-19](https://runescape.wiki/w/Skills?oldid=6579775) is the nearest pre-cutoff index; [`Template:Skills` oldid 6011690](https://runescape.wiki/w/Template:Skills?oldid=6011690) supplies the period navigation dependency. | Period [`Skill` oldid 15066](https://runescape.wiki/w/Skill?oldid=15066) redirects to `Skills`; [`Talk:Skills` oldid 6559494](https://runescape.wiki/w/Talk:Skills?oldid=6559494) was checked. | Complete. The White tree fruit omission below emerged only by crossing the repeatable-system talk history back into the ordinary-method surface. |
| Tasks and achievement diaries | Period [`Tasks` oldid 6268612, 2012-09-19](https://runescape.wiki/w/Tasks?oldid=6268612) is a literal redirect to `Achievements`; [`Achievements` oldid 6579331, 2012-11-18](https://runescape.wiki/w/Achievements?oldid=6579331) contains the nine area sets, requirement tables, rewards, miscellaneous tasks, Taskmaster, and lamp rules. | The page's inline `{{Task}}` formatter has no recoverable pre-cutoff revision under the current `Template:Task` title, but the row values are literal arguments in the pinned page. [`Talk:Achievements` oldid 6268613](https://runescape.wiki/w/Talk:Achievements?oldid=6268613) was checked for requirements, rewards, and incompleteness disputes. | Complete for index discovery; the established diary contract owns the harvested rows. |
| Treasure Trails | [`Treasure Trails` oldid 6473708, 2012-10-26](https://runescape.wiki/w/Treasure_Trails?oldid=6473708) literally separates tier rewards and clue types. | Period dependencies [`Template:Treasure trails rewards` oldid 6547726](https://runescape.wiki/w/Template:Treasure_trails_rewards?oldid=6547726) and [`Template:Clue item` oldid 3956588](https://runescape.wiki/w/Template:Clue_item?oldid=3956588) were read; [`Talk:Treasure Trails` oldid 5603675](https://runescape.wiki/w/Talk:Treasure_Trails?oldid=5603675) was checked for reward-list and clue-ownership gaps. | Complete. The 2026-07-19 Treasure Trails contract owns the per-tier harvest. |
| Reward shops | No pre-cutoff umbrella index exists under `Reward shop`: its first revision is [`oldid 16238606, 2016-03-11`](https://runescape.wiki/w/Reward_shop?oldid=16238606), and `Talk:Reward shop` begins in 2026. | Period coverage therefore comes from the literal Minigames/D&D pages and their nav dependencies, which point to the individual activity and currency surfaces rather than a later synthesized shop list. | Complete with a documented dependency gap; every period reward-shop lead resolves to the existing cross-program reward-currency/shop owner. No modern umbrella row was promoted as period proof. |
| Random events | [`Random events` oldid 6550007, 2012-11-12](https://runescape.wiki/w/Random_events?oldid=6550007) literally states that random events were removed on 24 October 2012 and labels the former set "Active Random Events until 24 October, 2012." | [`Talk:Random events` oldid 6343324](https://runescape.wiki/w/Talk:Random_events?oldid=6343324) was checked through its removal thread. | Complete. The whole interrupting-event system is absent immediately before EOC and remains an explicit exclusion, not a candidate. |
| Recurring systems | [`Repeatable events` oldid 6484427, 2012-10-27](https://runescape.wiki/w/Repeatable_events?oldid=6484427) literally separates daily, weekly, and monthly events and records reset/cap/reward rows. | [`Talk:Repeatable events` oldid 5147379, 2012-01-14](https://runescape.wiki/w/Talk:Repeatable_events?oldid=5147379) defines the index boundary and preserves suggestions omitted from the final table, including White tree fruit. | Complete. Most rows resolve to D&D, diary, shop, quest reward, Runespan, management, acquisition, or explicit social/lootbox exclusions; White tree fruit is admitted below. |

Talk-history follow-through rejected two tempting false positives rather than
padding the ranking. [`Chase the Monkey` oldid 6097207, 2012-08-16](https://runescape.wiki/w/Chase_the_Monkey?oldid=6097207)
is marked `{{Gone}}` and says it ran only from 26–28 May 2012, so it was not live
at the target snapshot. The period random-event page independently fixes the
whole random-event removal at 24 October 2012, before the target snapshot.

## Pass 2A — 2010–2012 update chronology

This pass walked the complete period update index rather than sampling release
names. [`Game updates` oldid 6563982, 2012-11-16](https://runescape.wiki/w/Game_updates?oldid=6563982)
contains 69 literal `Update:` links for 2010, 61 for 2011, and 76 for 2012
through 16 November. The three later pre-cutoff dated pages —
[`Evolution of Combat: Economic Impact`](https://runescape.wiki/w/Update:Evolution_of_Combat:_Economic_Impact),
[`Evolution of Combat: Melee`](https://runescape.wiki/w/Update:Evolution_of_Combat:_Melee),
and [`Evolution of Combat: Slayer & Prayer`](https://runescape.wiki/w/Update:Evolution_of_Combat:_Slayer_%26_Prayer) —
were then read through 19 November. That is 209 link occurrences resolving to
208 distinct pages.

Every linked page was read as literal wikitext, including its `In other news`
tail rather than only its title or lead. As a defensive completeness check, the
current `Category:<year> updates` membership was intersected with
`Category:Game updates`, date-limited to the cutoff, and all 241 resulting pages
were also read. The union of the period index and the defensive category pass is
**261 distinct update pages**. This deliberately includes pages whose present
category changed after the period: 20 period-index pages no longer in the
current year/game intersection, and 53 current-category pages absent from the
pinned index. The imported `Update:` page revision timestamp was never treated
as period proof; its original-date template and its link from the pinned index
establish the chronology, while candidate mechanics below are independently
confirmed by pre-cutoff article and talk oldids.

| Chronology slice | Literal pages walked | Durable-addition reconciliation |
|---|---:|---|
| 2010 period index | 69 | Quests, Dungeoneering floors/rewards, activities, diaries/clues, Combat changes, Slayer methods, Herblore Habitat, Warriors' Guild, and item/service changes all resolve to implementations or named programs. The cheese-wheel method below is absent. |
| 2011 period index | 61 | Quests, Nex/God Wars, urns/ashes, Artisan's Workshop, Livid Farm, Lava Flow Mine, Jadinko Lair, Temple Trekking, Dominion Tower, Polypore Dungeon, Flash Powder Factory, reward shops, equipment effects, and recurring systems resolve to existing owners. |
| 2012 period index through 16 November | 76 | Quests/sagas, flasks, Fight Kiln, Morytania tasks, Runespan, Bonfires, Queen Black Dragon, Crucible, Fish Flingers, Big Chinchompa, Daily Challenges, God Wars/KBD reworks, Goblin Raids, Tears of Guthix, and Dungeoneering changes resolve to existing owners. |
| 17–19 November addendum | 3 | All three pages describe the not-yet-live 20 November EOC system. They add no gameplay to the strict pre-cutoff snapshot. |
| Defensive current-category intersection | 241 | The 261-page union was fully read. Extra rows are patch-adjacent notices, beta/previews, temporary bonus events, Squeal/Solomon promotions, account/security rewards, social/clan systems, cosmetics, graphics/audio/UI, or duplicate release coverage, except for the Doric/Boric task finding below. |

The durable-delta diff used the authority order already fixed above. Quest
releases map to the 194-quest/167-missing-definition program; ordinary skill
changes map to the shipped-skill ledger; activities, bosses, diaries, shops,
item effects, acquisition routes, and reward currencies map to their named
cross-system owners. Temporary holiday/bonus weekends and membership/game-card
promotions do not create durable snapshot systems. Squeal of Fortune and
Solomon's Store remain explicit commerce exclusions; clans and intrinsically
social layers remain excluded; graphics, audio, chat, login, world-list, and
client-control changes carry no review-native gameplay loop. EOC beta and
preview pages describe future or separate-beta behavior and cannot prove live
pre-cutoff gameplay.

The full chronology produced **two** admissions. It also independently
rediscovered many already-owned items — including Daily Challenges, The
Crucible, Court Cases, Ancient Effigies, Queen Black Dragon, Goblin Raids,
Warriors' Guild, Runespan, Bonfires, Fish Flingers, Familiarisation, Shattered
Heart, and the activity/reward-shop trees — without counting them again.

## Ranked new candidates

### 1. Post-quest Chimp ice deliveries

- **Canonical surface and aliases:** post-quest Chimp ice deliveries; Chimp ice
  activity; King Awowogei delivery loop.
- **Gameplay consequence:** after `Do No Evil`, the player buys one Chimp ice,
  repeatedly freezes it with Ancient Magicks while completing a constrained
  delivery route, and receives 30–50 death runes, 30–50 blood runes, a banana,
  or a rare dragon scimitar. Every fifth delivery melts twice as fast; there is
  no post-quest checkpoint. Deliveries 5, 10, and 15 add monkey statues, delivery
  25 replaces the camp guards with red monkey knife fighters, the king retains
  a persistent delivery count, and 25 deliveries feed the Completionist cape.
- **Period proof:** [`Chimp ice` oldid 6105414, 2012-08-18](https://runescape.wiki/w/Chimp_ice?oldid=6105414)
  contains the literal post-quest activity, route, timing, reward, milestone,
  and completionist text. [`Talk:Chimp ice` oldid 3727642, 2011-01-12](https://runescape.wiki/w/Talk:Chimp_ice?oldid=3727642)
  contemporaneously records the delivery counter, exact half-time fifth runs,
  5/10/15 statues, 25-delivery endpoint, and no checkpoint. The discovery seam
  was the `Chimp ice` omission proposed in [`Talk:Minigames` oldid 5574573](https://runescape.wiki/w/Talk:Minigames?oldid=5574573).
- **Repository disposition:** the base `Do No Evil` quest exists, but neither
  the activity name, inputs/state, delivery count, melt cycle, nor rewards occur
  anywhere else in the repository. It has no Kanban, gap-ledger, wider-ledger,
  closure-audit, code, test, asset, or focused-audit owner.
- **Proposed owner:** quest continuations / recurring activities. This is an
  ownership proposal, not a design decision.

### 2. White tree fruit harvest

- **Canonical surface and aliases:** harvest White tree fruit; post-`Garden of
  Tranquillity` White Tree.
- **Gameplay consequence:** the last White Tree is the sole acquisition route;
  four fruits regrow quickly, each harvest awards 12 Farming XP, and each fruit
  heals 30 life points and restores 17 run energy. The fruit also supplies
  supercompost, a medium Varrock task, and Ube's Beacon Network tending service.
- **Period proof:** [`White tree fruit` oldid 5838367, 2012-06-26](https://runescape.wiki/w/White_tree_fruit?oldid=5838367)
  contains those literal output, XP, item-effect, diary, and beacon facts. The
  candidate was recovered from the period suggestion in
  [`Talk:Repeatable events` oldid 5147379](https://runescape.wiki/w/Talk:Repeatable_events?oldid=5147379);
  there is no separate pre-cutoff `Talk:White tree fruit` revision.
- **Repository disposition:** only the generated item-value universe names the
  item. No Farming target, runtime action, quest unlock, acquisition path,
  effect, task/beacon dependency, test, focused audit, or forward-work row does.
- **Proposed owner:** Farming special harvest plus acquisition/item effects,
  with diary and Beacon Network dependencies recorded rather than duplicated.

### 3. Doric and Boric post-quest task series

- **Canonical surface and aliases:** Doric and Boric tasks; Doric's tasks;
  Boric's tasks; Gofannon amulet task charges.
- **Gameplay consequence:** after `What's Mine is Yours`, members can complete
  distinct Mining and Smithing task chains for direct XP and up to 183,500
  bonus XP stored in the Gofannon amulet. The release post says the tasks span
  requirements through 60 Mining and 75 Smithing; the pinned article records
  up to 13,000 Mining XP and 48,000 Smithing XP in addition to the amulet pool.
- **Period proof:** [`What's Mine is Yours` oldid 6553815, 2012-11-14](https://runescape.wiki/w/What's_Mine_is_Yours?oldid=6553815)
  literally identifies `Doric and Boric tasks` as additional post-quest rewards
  and gives the 183,500/13,000/48,000 XP totals. The contemporaneous
  [`Talk:What's Mine is Yours` oldid 6487452, 2012-10-27](https://runescape.wiki/w/Talk:What's_Mine_is_Yours?oldid=6487452)
  independently distinguishes Doric's Smithing XP, Boric's Mining XP, and the
  shared amulet bonus XP. The discovery seam was the literal
  [`What's Mine is Yours` update page](https://runescape.wiki/w/Update:What's_Mine_is_Yours),
  which describes the post-quest task ladder and its rewards.
- **Repository disposition:** the base quest is present only in generated quest
  metadata. No Doric/Boric task catalog, persistent task state, Mining or
  Smithing action, Gofannon charge pool, XP delivery, test, focused audit,
  Kanban row, gap row, or wider-family owner exists.
- **Proposed owner:** quest continuations / finite task loops, with Mining,
  Smithing, and pending-XP delivery dependencies recorded rather than copied.

### 4. Cheese-wheel churning and slicing

- **Canonical surface and aliases:** churn cheese wheel; slice cheese wheel;
  cheese-wheel Cooking method.
- **Gameplay consequence:** at 48 Cooking, churning milk or butter creates an
  untradeable cheese wheel for the former cheese-making XP. Slicing the wheel
  awards 4 Cooking XP per slice and produces a level-influenced random output
  of at least five tradeable cheese pieces. This is a durable repeatable
  Cooking/transformation loop, not the similarly named temporary Gielinor Games
  contest.
- **Period proof:** [`Cheese wheel` oldid 6288901, 2012-09-24](https://runescape.wiki/w/Cheese_wheel?oldid=6288901)
  literally gives the 24 June 2010 release, level 48 gate, milk/butter inputs,
  wheel output, 4 XP per slice, minimum-five yield, and level-shaped roll. The
  period [`Talk:Cheese wheel` oldid 5942573, 2012-07-16](https://runescape.wiki/w/Talk:Cheese_wheel?oldid=5942573)
  preserves contemporaneous yield testing and the level/distribution dispute.
  The discovery seam was the `In other news` tail of
  [`Quiet Before the Swarm`](https://runescape.wiki/w/Update:Quiet_Before_the_Swarm),
  itself linked from the pinned period update index.
- **Repository disposition:** `Cheese wheel` survives as generated item/value
  and shop identity only. There is no Cooking target, churning utility, slicing
  action, XP/yield roll, runtime mutation, test, focused audit, Kanban row, gap
  row, or wider-family owner.
- **Proposed owner:** Cooking ordinary methods plus the shared transformation/
  acquisition layer.

Pass 0 remains a zero-candidate baseline and does not count toward convergence.
Pass 1 found two candidates and Pass 2A found two more, so the zero-new streak
remains zero. Previously
named, settled, pattern-determined, parked, excluded, split, source-blocked, or
implemented surfaces were still rejected as duplicates rather than padded into
the ranking.

Future candidates must be appended here in rank order with:

- canonical surface name and normalized aliases;
- the gameplay consequence that makes it a genuine surface;
- pinned pre-cutoff citation (title, oldid/capture, timestamp, literal evidence);
- source-family/pass that found it;
- exact repository `rg` command and output proving absence or named-only,
  unowned status;
- duplicate checks against the Kanban, gap subledger, wider family ledger,
  closure audit, code, tests, and focused audits; and
- proposed owning family only — no design reopening during recon.

## Exact baseline grep evidence

These commands were run from the repository root. Their outputs are preserved
verbatim enough to reproduce the baseline decisions.

```text
$ rg -n "Status:|Label contract|Existing-skill parity ledger|Large special methods and activities|Activities, minigames|Bosses and instanced|Achievement diaries|Random events and timed|Explicitly excluded" memory-bank/future-work-kanban.md
3:Status: reconciled 2026-07-16. This is the canonical forward-work board. The 2026-07-10 completion audit is archived baseline evidence; the shipped-skill subledger remains `memory-bank/gap-backlog.json`.
5:## Label contract
45:### Existing-skill parity ledger
643:### Large special methods and activities
687:### Activities, minigames, D&Ds, and reward shops
695:### Bosses and instanced Combat
725:### Achievement diaries, clues, collections, and one-time content
744:### Random events and timed world content
875:## Explicitly excluded
```

```text
$ rg -n "Wider family ledger|Deliberate exclusion or parked ledger|Must close|Representative-breadth trees|2026-07-18 recon passes added and settled|Warriors' Guild and defenders" memory-bank/ankiscape-completion-starter-grill-2026-07-17.md
625:### Wider family ledger
662:The 2026-07-18 recon passes added and settled: Daily Challenges &
678:### Must close
698:7. **Warriors' Guild and defenders.** This is a core melee equipment progression
708:### Representative-breadth trees
720:### Deliberate exclusion or parked ledger
```

```text
$ rg -n "Owner-settled forks|Pattern-determined|Follow-through|overnight exhaustive recon|Status:" memory-bank/source-audits/recon-coverage-closure-2026-07-18.md
7:Status: **owner-settled dispositions for every surface found by the two Sol
15:## Owner-settled forks (walked singly, 2026-07-18)
45:## Pattern-determined (recorded, no fork; owning contract named)
64:## Follow-through
67:- The overnight exhaustive recon (live pre-cutoff wiki indices diffed against
```

```text
$ jq -r '.items | group_by(.status)[] | "\(length)\t\(.[0].status)"' memory-bank/gap-backlog.json | sort -nr
22  merged
13  design_settled_waiting_source
4   split_scope
1   source_blocked_waiting_darkan
1   rejected_product_scope
1   rejected_out_of_period
1   parked_farming_seed
1   design_settled
1   design_partial_waiting_source
```

```text
$ rg -n "Current detailed state|Continue from.*gap-backlog|Do not reconstruct|PARKED|EXCLUDED" memory-bank/future-work-kanban.md
12:- `PARKED`: deliberately sequenced later, not forgotten.
13:- `EXCLUDED`: outside the product/cutoff boundary.
49:- Continue from `memory-bank/gap-backlog.json`; do not reconstruct merged cards or re-grill settled branches.
50:- Current detailed state: 22 merged, 13 design/source-blocked waits (including Grenwall), four split-scope, one Farming seed, one partially reopened/source-waiting, two exclusions, one design-partial/source-waiting card, and one design-settled parent-decision card.
```

## Exact Pass 1 repository evidence

The first command proves that neither candidate name nor the Chimp ice failure
state exists anywhere in code, tests, assets, audits, contracts, or ledgers.

```text
$ rg -l -i "chimp[ _-]?ice|chocolatey goop" . --glob '!memory-bank/audits/overnight-content-recon-2026-07-19.md' | sort
(no output)
```

The ownership-ledger check independently produced no candidate-specific owner.

```text
$ rg -n -i "chimp[ _-]?ice|chocolatey goop|king awowogei|do no evil" memory-bank/future-work-kanban.md memory-bank/gap-backlog.json memory-bank/ankiscape-completion-starter-grill-2026-07-17.md memory-bank/source-audits/recon-coverage-closure-2026-07-18.md
(no output)
```

The base quest is catalogued, which prevents the absence claim from being
overstated: the missing surface is specifically the post-quest repeatable loop.

```text
$ rg -n -i "do no evil|do_no_evil" quest_data.py quest_catalog_generated.py tests memory-bank/future-work-kanban.md memory-bank/gap-backlog.json | head -3
quest_data.py:8049:    "do_no_evil": (
quest_catalog_generated.py:30257: {'id': 'do_no_evil',
quest_catalog_generated.py:30258:  'display_name': 'Do No Evil',
```

White tree fruit is present only as generated item identity, not gameplay.

```text
$ rg -l -i "white tree fruit|white_tree_fruit" . --glob '!memory-bank/audits/overnight-content-recon-2026-07-19.md' | sort
./item_values_generated.py
```

Removing generated identity/value catalogs leaves no implementation, test,
audit, contract, or ledger occurrence.

```text
$ rg -n -i "white tree fruit|white_tree_fruit|last remaining white tree" --glob '*.py' --glob '*.md' --glob '*.json' --glob '!quest_catalog_generated.py' --glob '!item_values_generated.py' --glob '!shop_data.py' --glob '!assets_provenance.json' --glob '!memory-bank/audits/overnight-content-recon-2026-07-19.md' .
(no output)
```

## Exact Pass 2A coverage and repository evidence

The pinned chronology resolved to the last pre-cutoff revision available before
the 17–19 November addendum:

```text
$ python3 tools/wiki_parity.py resolve "Game updates"
title=Game updates
revid=6563982
timestamp=2012-11-16T17:08:37Z
url=https://runescape.wiki/w/Game_updates?oldid=6563982
```

Literal link extraction from that oldid returned 69 `Update:` links for 2010,
61 for 2011, and 76 for 2012. Adding the three dated pages from 17–19 November
produced 209 link occurrences / 208 resolved pages. The independent
year-category intersection produced 71 pages for 2010, 62 for 2011, and 108 for
2012 through 19 November. Resolving redirects and taking the union produced the
261 pages reported above; every page's literal wikitext was read.

Cheese-wheel identity exists, but removing generated identity/shop data leaves
no gameplay owner:

```text
$ rg -l -i "cheese wheel|wheels of cheese|slice-all" . --glob '!memory-bank/audits/overnight-content-recon-2026-07-19.md' | sort
./item_values_generated.py
./shop_data.py
```

```text
$ rg -n -i "cheese wheel|wheels of cheese|slice-all" --glob '*.py' --glob '*.md' --glob '*.json' --glob '!item_values_generated.py' --glob '!shop_data.py' --glob '!assets_provenance.json' --glob '!memory-bank/audits/overnight-content-recon-2026-07-19.md' .
(no output)
```

The Doric/Boric task family appears only inside generated quest metadata:

```text
$ rg -l -i "doric and boric|doric.?s tasks|boric.?s tasks|gofannon|183,?500" . --glob '!memory-bank/audits/overnight-content-recon-2026-07-19.md' | sort
./quest_catalog_generated.py
```

Removing generated catalogs and identity data leaves no implementation,
focused audit, test, or ownership row:

```text
$ rg -n -i "doric and boric|doric.?s tasks|boric.?s tasks|gofannon|183,?500" --glob '*.py' --glob '*.md' --glob '*.json' --glob '!quest_catalog_generated.py' --glob '!item_values_generated.py' --glob '!shop_data.py' --glob '!assets_provenance.json' --glob '!memory-bank/audits/overnight-content-recon-2026-07-19.md' .
(no output)
```

The generated base quest prevents the absence claim from being overstated:

```text
$ rg -n -i "what.?s mine is yours|what_s_mine_is_yours" quest_data.py quest_catalog_generated.py tests memory-bank/future-work-kanban.md memory-bank/gap-backlog.json | head -3
quest_catalog_generated.py:13826:  'requirements': ('Recruitment Drive', "What's Mine is Yours", 'Fletching 50', 'Runecrafting 50', 'Smithing 65'),
quest_catalog_generated.py:13828:                      {'quest_id': 'whats_mine_is_yours', 'display_name': "What's Mine is Yours"}),
quest_catalog_generated.py:27315:                   "What's Mine is Yours",
```

## Deadline closure — incomplete source coverage

The final recovery worker reached the hard deadline before it could write its
own checkpoint. Its bounded partial artifact is still useful, but it does **not**
close the promised source sweep:

- The live 2011Scape snapshot was enumerated at 1,205 bound plugin files plus
  metadata. The live Darkan gameplay tree was enumerated at 1,835 files across
  achievements, bosses, D&Ds, minigames, miniquests, quests, skills, items, and
  world areas.
- None of the four admitted candidates had an implemented mechanic in either
  tree. Chimp ice, White tree fruit, cheese-wheel, and Gofannon/Doric-Boric
  names appeared only in static identity, spawn, or item-config records.
- The local cache inventory confirmed extracted builds 727, 728, 729, 736, 741,
  and 742. The cross-build item/object/NPC query had only begun on build 727
  when the deadline canceled it, so it cannot be represented as a completed
  cache pass.
- The dated Wayback/official-Jagex pass, full local implementation/audit seam,
  and materially distinct convergence passes were not completed.

No fifth candidate is admitted from this partial work. The four ranked rows
above remain source-backed findings, but this report is a productive checkpoint,
not an exhaustive-coverage closure. A later continuation must resume from the
unfinished source families rather than repeating Passes 0, 1, or the update
chronology.

## Checkpoint log

| Time (PDT) | Pass | New | Cumulative | Zero-new streak | Required sweep complete | Note |
|---|---:|---:|---:|---:|---:|---|
| 2026-07-19 00:17:46 | 0 | 0 | 0 | 0 | No | Baseline authority, coverage matrices, duplicate lock, and stop rule established. |
| 2026-07-19 02:18:13 | 1 | 2 | 2 | 0 | No | Pinned Wiki gameplay indices, literal wikitext, period dependencies, redirects, and talk-history seams complete; two candidates admitted, post-cutoff/removed and owned rows rejected. |
| 2026-07-19 07:32 | deadline | 0 | 4 | 0 | No | Implementation trees partially reconciled; archive, full cache, local-seam, and convergence coverage remain unfinished. |
| 2026-07-19 06:01 | 2A | 2 | 4 | 0 | No | All 2010–2012 period-index updates through 19 November, every linked page, every `In other news` tail, and the broader current-category union were diffed; Doric/Boric tasks and cheese-wheel Cooking admitted. |
