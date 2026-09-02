# Ghosts Ahoy source harvest — 2026-09-01

## Scope and evidence boundary

This is the source record for replacing Ghosts Ahoy's seven generated stage
sentinels. The cutoff is immediately before EOC:
`2012-11-20T00:00:00Z`.

The period articles establish the ordered deeds below, but their two revisions
are one RuneScape Wiki lineage. They do **not** independently close a concrete
value merely by agreeing with one another. The narrow Level-2 runtime proof in
the 2012scape quest ledger is separately authorized fact only for the claims
listed in [Proven](#proven). It is not a frozen contract, creates no claim
ceiling, and silence in it is not exclusion.

The period sources contain no numbered seven-stage quest model. The mapping is
an AnkiScape grouping of the seven ordered walkthrough sections; it is not
presented as a historical stage numbering scheme.

## Pinned inputs

| Key | Dated identifier and immutable source | Role in this audit |
| --- | --- | --- |
| B | [Ghosts Ahoy — oldid 5981551](https://runescape.wiki/w/Special:PermanentLink/5981551), `2012-07-23T21:11:55Z` UTC; `/Users/ArmanTarkhanian1/Documents/2012scape with bots/memory-bank/audit/sources/ghosts-ahoy-build727-oldid-5981551.json`, `query.pages["7205"].revisions[0].slots.main["*"]` | Build-727-era pre-cutoff walkthrough, requirements, rewards, and music list. |
| F | [Ghosts Ahoy — oldid 6575527](https://runescape.wiki/w/Special:PermanentLink/6575527), `2012-11-18T10:48:16Z` UTC; `/Users/ArmanTarkhanian1/Documents/2012scape with bots/memory-bank/audit/sources/ghosts-ahoy-final-pre-eoc-oldid-6575527.json`, same JSON path | Nearest pinned pre-EOC walkthrough. |
| Q | [Template:Questreq — oldid 5981134](https://runescape.wiki/w/Special:PermanentLink/5981134), `2012-07-23T14:16:09Z` UTC; `/Users/ArmanTarkhanian1/Documents/2012scape with bots/memory-bank/audit/sources/template-questreq-ghosts-ahoy-build727-oldid-5981134.json`, Ghosts Ahoy `#switch` entry | Explicitly names both prerequisite quests. |
| L | `/Users/ArmanTarkhanian1/Documents/2012scape with bots/memory-bank/audit/ledgers/quests.jsonl:66`, row `quests-ghosts-ahoy`, evidence entries E1/E2 dated `2026-07-10`, iteration 85 | Independently observed, cold-world runtime proof. Only the owner-authorized narrow claims in the Proven section are carried forward. |
| R7 | rev `727`, `2012-07-24`, OpenRS2 archive `309`; `/Users/ArmanTarkhanian1/Library/Caches/codex/2012scape-openrs2/extracted/727-2012-07-24/cache/` | Client item, NPC, and object identity/options, queried with `tools/query_openrs2_cache*.sh`. It proves no server transition, quantity, reward, or gate. |
| R42 | rev `742`, `2012-11-07`, OpenRS2 archive `544`, SHA-256 `9f5fdba0d22cdc1b4ad86c984cc0ba4bcd4b3c22039f3290ba48f5083bc100b8`; `/Users/ArmanTarkhanian1/Library/Caches/codex/2012scape-openrs2/extracted/742-2012-11-07/cache/` | Later pre-cutoff client check: it agrees with R7 for the Ghosts Ahoy item and interaction identities cited below. |
| G | `/Users/ArmanTarkhanian1/Downloads/game-main/data/cfg/items.yml:45927-45999,46103-46179` | Independent rev-667 client configuration corroborating the listed Ghosts Ahoy item identities. This checkout is not a Git repository, so it has no commit identifier. |
| D | Darkan Ghosts Ahoy restoration commit `4d95090a80e020c71c90ce0b59b52662d1da7abf`, `2026-07-11` | Inspected first under the evidence order. It is a modern restoration, not independent historical proof; R7/R42/G can corroborate only its client-facing IDs/options. |
| T | `/Users/ArmanTarkhanian1/Documents/2012scape with bots/memory-bank/audit/sources/ghosts-ahoy-transcript-history.json` | Excluded as period dialogue proof: its earliest `Transcript:Ghosts Ahoy` revision is oldid `12172235`, `2014-12-27T03:16:59Z`; `Ghosts Ahoy/Transcript` begins at oldid `16472909`, `2016-04-05T21:48:55Z`. Both are after cutoff. |

B, F, and Q are useful temporal records, but are a single wiki lineage. The
Darkan/build-727 pairing is likewise not counted twice: rev 727 is Darkan's
cache base. D was inspected before R7, G, and R42; no current-restoration
behavior is counted as historical proof. No mutable wiki URL is used.

## Current generated sentinels

`data/quest_data.py:9` imports `PRE_EOC_QUEST_CATALOG`; the active Ghosts Ahoy
entries are generated rather than literal quest rows. Their current source is
`generated/quest_catalog_generated.py:9106-9155` (`ghosts_ahoy`), where each
stage has `source_kind: 'source_page_checkpoint'` and source oldid `6575527`.
The generator's Long-quest fallback creates seven stages in
`tools/build_pre_eoc_quest_catalog.py:732-745,2503-2514`.

**Adjacent catalog discrepancy, not changed here:** the generated
`required_quests` row names only The Restless Ghost at
`generated/quest_catalog_generated.py:9125`. Q and L prove that Priest in
Peril is also a prerequisite. This harvest reports the discrepancy; it does not
modify catalog data.

| Stage | Exact current objective text |
| ---: | --- |
| 1 | `Complete Ghosts Ahoy stage 1 objective using the pinned source guide.` |
| 2 | `Complete Ghosts Ahoy stage 2 objective using the pinned source guide.` |
| 3 | `Complete Ghosts Ahoy stage 3 objective using the pinned source guide.` |
| 4 | `Complete Ghosts Ahoy stage 4 objective using the pinned source guide.` |
| 5 | `Complete Ghosts Ahoy stage 5 objective using the pinned source guide.` |
| 6 | `Complete Ghosts Ahoy stage 6 objective using the pinned source guide.` |
| 7 | `Complete Ghosts Ahoy stage 7 objective using the pinned source guide.` |

The generated completion line `Quest complete!` follows stage 7. The generated
catalog currently places the Giant lobster encounter on stage 6
(`generated/quest_catalog_generated.py:9216-9237`), although B/F place it in
`====The Book of Haricanto====`, which is stage 4 in the mapping below.

## Replacement deeds, in period order

Every deed headline below is attested in both B and F at the named section.
“Verified” identifies the parts that the authorized Level-2 runtime proof also
covers. The nonnumeric action target is fully sourced for all seven stages;
concrete quantities, combat values, and extra effects are deliberately bounded
in [Not recovered](#not-recovered).

| Stage | Real period deed replacing the sentinel | Pinned source and status |
| ---: | --- | --- |
| 1 | Worship the Ectofuntus with bonemeal and slime, then collect ecto-tokens from a ghost disciple for Port Phasmatys access. | B/F, `=== Preliminary to the Quest ===`. Period deed pinned; exact token yield, required total, and supplies are unrecovered. |
| 2 | Speak to Velorina, ask Necrovarus to release the ghosts, receive his refusal, and return to Velorina. | B/F, `===Begin the Quest: Visit Velorina===`. Period deed pinned; exact dialogue and conditions are unrecovered. |
| 3 | Give the Old Crone nettle tea in her special cup with milk, then learn that the amulet enchantment requires the Book of Haricanto, Necrovarus's robes, and a translation manual. | B/F, `===The Old Woman and Nettle Tea===` and `===Enchanting the Amulet===`; verified for the ordered tea handoff and three-item enchantment route by L E2. |
| 4 | Make the model-ship flag, exchange it for the chest key, obtain and assemble the map scraps, defeat the Giant lobster on that route, travel to Dragontooth Island, and dig up the Book of Haricanto. | B/F, `====The Book of Haricanto====`; verified at the model-ship/map/book-route level by L E2. The generated lobster placement must move from stage 6 to this stage. |
| 5 | Dip the bedsheet in ectoplasm, obtain Gravingas's petition signatures, present the petition to Necrovarus, take the dropped bone key, and search his coffin for the mystical robes. | B/F, `====The Robes====`; verified at the petition/robe-route level by L E2. Exact signature count and recovery rules remain unrecovered. |
| 6 | Beat Robin at Rune-Draw, receive his signed oak longbow, and exchange it with Ak-Haranu for the translation manual. | B/F, `====The Manual====`. Period deed pinned; the exact number of hands, debt, and game mechanics are unrecovered. |
| 7 | Return to the Old Crone with the three items and the Amulet of Ghostspeak, receive the enchantment, command Necrovarus to release the ghosts, and report success to Velorina. | B/F, `===Using the Spell===`; the three-item enchantment handoff is verified by L E2. Command charge/use semantics and exact dialogue are unrecovered. |

## Proven

These are the complete positive boundary. Each is either a direct
owner-authorized Level-2 fact or a nonnumeric period deed stated in B/F and
needed to name a sentinel replacement.

| Proven item | Source |
| --- | --- |
| The exact seven sentinel texts and their numbers. | `data/quest_data.py:9`; `generated/quest_catalog_generated.py:9106-9155`. |
| The seven ordered replacement-deed headlines in the preceding table. | B/F, the ordered walkthrough sections stated in that table. |
| Client-visible quest-item identities: `Mystical robes` **4247**, `Book of haricanto` **4248**, `Translation manual` **4249**, `Ghostspeak amulet` **4250**, `Ectophial` **4251**, model-ship states **4253/4254**, map scraps **4274–4276**, treasure map **4277**, petition form **4283**, and bedsheet **4284**. | R7 and R42 item definitions; G independently agrees on the IDs/names. This proves item identity/options only, never hand-in, transformation, reward, or availability behavior. |
| Client-visible interaction identities: Velorina **1683**, Necrovarus **1684**, Gravingas **1685**, Giant lobster **1693**, Old crone **1695**, Old man **1696**; coffin **5278/5279** and Ectofuntus **5282/5283**. | R7/R42 definitions: the named NPC/object labels expose `Talk-To`, `Attack`, `Open`/`Search`, or `Worship` as appropriate. G's NPC constants independently agree on 1683–1685 and the Old-man association. These are client labels, not server quest-state proof. |
| Prerequisites: **Priest in Peril** and **The Restless Ghost**. | Q's Ghosts Ahoy entry; L E2's observed target prerequisite matrix, within the owner-authorized scope. |
| **Agility 25**, with boosts allowed; **Cooking 20**, base/unboosted. | B/F `Quest details → requirements`; L E1/E2, within the owner-authorized scope. |
| The ordered nettle-tea handoff. | F `===The Old Woman and Nettle Tea===`; L E2's observed transactional tea handoff. |
| The Book of Haricanto, Necrovarus's robes, and translation manual as the three-item enchantment route. | F `===Enchanting the Amulet===` and `===Using the Spell===`; L E2's observed transactional enchantment handoff. |
| Transactional quest-item handoffs and recovery at the authorized category level. | L E2: transactional handoffs and recoverable quest items. It does not close each item's individual loss, bank, replacement, or quantity rule. |
| The model-ship → map → book route. | F `====The Book of Haricanto====`; L E2's observed model-ship/map/book route. |
| The petition → robe route. | F `====The Robes====`; L E2's observed petition/robe route. |

## Not recovered

The table is deliberately exhaustive for concrete requirements, rewards, and
unlocks exposed by B/F or the ledger within this quest slice. A row marked
unrecovered may be described by B/F, but has no permitted independent layer
that closes it. It must not become an implementation value or player-facing
claim. The final column names the kind of evidence that would settle it.

### Requirements and route values

| Item | Status and current evidence | What would settle it |
| --- | --- | --- |
| Members-only status. | **Unrecovered.** B/F infobox and Quest details say `members=Yes`; no independent period layer was recovered. | Dated official quest guide or update post, Wayback capture, or independently sourced implementation plus a period record. |
| Giant lobster level **32** and the stated vampyre (**69–71**) and leech (**52**) combat advisories. | **Unrecovered as hard gates.** F lists them in the walkthrough requirements, but does not prove server gating; no independent gate evidence was recovered. | Period server implementation corroborated by a dated guide, or a pinned official/Wayback source that identifies these as mandatory gates. |
| Exact supply ownership, consumption, and quantities: coins; ecto-tokens; bones; pots; buckets; ectoplasm; spade; milk; needle; thread; silk; knife; nettle-tea ingredients; oak longbow; and dyes. | **Unrecovered except for the broad transactional/recoverable-item category above.** B/F's item list is one wiki lineage. R7/R42/G prove the explicit quest-item identities listed in Proven, not these acquisition, consumption, or quantity rules. | Runtime proof or separate implementation corroborated by a dated period guide; dated cache data can corroborate identities/options but not consumption or quantity. |
| Exact Ectofuntus token result and route totals, including **45** received, **35** needed, **33/16** token alternatives, the Ring-of-charos variant, and all fare alternatives. | **Unrecovered.** These values appear in B/F only. | Dated official guide/Wayback capture or independently reconstructed server behavior corroborated by period evidence. |
| Exact Nettle-tea materials/counts, exact dye count/colour rules, exact map-scrap count, exact petition-signature count, and exact Rune-Draw rule of **four** hands / **100** coins. | **Unrecovered.** B/F mention the values, but L E2 authorizes only the broader route categories. | Independent dated period guide/Wayback source, or an independently verified server implementation plus period corroboration. |
| **58** Agility shortcut and toolbelt eligibility/restrictions. | **Unrecovered.** F describes both in walkthrough prose only. | Pinned client interaction/config evidence plus a dated period guide, or period server evidence where applicable. |
| Exact dialogue, dialogue conditions, and player choice wording. | **Unrecovered.** T has no pre-cutoff transcript revision. | A pre-cutoff transcript capture, dated Wayback archive, or official dialogue archive. |

### Rewards and unlocks

| Item | Status and current evidence | What would settle it |
| --- | --- | --- |
| **2 Quest Points**. | **Unrecovered.** B/F `==Rewards==` lists it, but that is one lineage. The owner-authorized E2 scope for this harvest does not include reward amounts. | Independent pinned period reward record: official guide/update, dated Wayback capture, or a separately sourced implementation plus period corroboration. |
| **2,400 Prayer XP**. | **Unrecovered.** B/F `==Rewards==` lists it; no independent value is authorized here. | The same independent period reward record. |
| Free passage to Port Phasmatys. | **Unrecovered.** B/F `==Rewards==` lists it. | A dated official/Wayback reward or access record, or independent implementation plus period corroboration. |
| Ectophial grant; its one-click Ectofuntus teleport, automatic refill, one-at-a-time possession limit, and free re-obtainment. | **Unrecovered.** B/F `==Rewards==` describes all of these. R7/R42 identify item **4251** and its client `Empty` option; G independently identifies the item and Velorina-associated replacement wording. Neither closes the grant, destination, refill, limit, or replacement rule. | A dated official quest/item guide or update, plus independent period implementation evidence for behavior. |
| **2** Squeal of Fortune spins. | **Unrecovered.** B/F `==Rewards==` lists it only. | An independent pinned period reward record. |
| Music tracks **Shipwrecked** and **Dragontooth Island**. | **Unrecovered.** B/F `==Music unlocked==` lists them only. | Pinned cache music-unlock configuration corroborated by a dated period guide or official release record. |
| Downstream quest unlocks, including ledger-listed Animal Magnetism and Cabin Fever, and Morytania-task dependencies. | **Unrecovered.** The ledger's `downstream_unlocks` is not dated period evidence; B/F's `==Required for completing==` is a downstream requirement list, not a quest-unlock record. | Pinned pre-cutoff prerequisite revisions for each named dependent quest, cross-checked with an independent dated source. |
| One-use Necrovarus command / one-charge enchanted-amulet behavior and terminal-state value. | **Unrecovered.** B/F says the amulet has one charge, but this is server behavior; the narrow owner-authorized E2 scope does not close it. | Independently sourced server implementation corroborated by a pinned pre-cutoff guide or dialogue capture. |

## Handoff boundary

All seven stage *deed headlines* are sufficiently pinned to replace generated
sentinels. Stages 3, 4, and 5 additionally have an owner-authorized independent
runtime proof for their key route category; stage 7 has that proof only for the
three-item handoff. Stages 1, 2, and 6 are period-pinned but not independently
closed beyond their nonnumeric objective. No stage is fully closed for every
concrete quantity, item rule, combat threshold, reward, or unlock.

No values outside the Proven and Not recovered tables are asserted by this
harvest. In particular, the absence of a frozen Ghosts Ahoy contract is not a
license to promote a plausible reward, item count, route fee, combat gate, or
side unlock.
