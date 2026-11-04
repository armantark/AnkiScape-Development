# Pass 20 missing equipment registrations

Date: 2026-11-04. Scope: ticket 11; cutoff `2012-11-20T00:00:00Z`.

The base equipment catalog already contained these 21 records and their drop routes. Registration now makes them ordinary held items, with the existing equipment metadata. Twenty are tradeable; Shade robe is not. No equipment stats, drop rates, recipes or shops change. The owner's approvals are "9. Yes obviously" and "Ok" to the settled design.

## Sources and identity

Both shared harvest ledgers were checked. Black mask's pre-beta pin is reused from the Darkan ledger; Adamant boots and Adamant spear reuse the supplied saved pages. The supplied Adamant boots page is oldid 6007790, timestamp 2012-07-28T12:28:54Z. Its beta marker is why the table below also uses the older non-beta item facts. Other beta-marked or redirect-only cutoff pages likewise have a non-beta parent corroboration; all raw API packets, literal bodies and hashes remain in `/Users/ArmanTarkhanian1/Documents/ankiscape-pass20/evidence/11/sources/qualified.json` and that directory's referenced files.

The exact-ID rev-742 cache probe is `/Users/ArmanTarkhanian1/Documents/ankiscape-pass20/evidence/11/sources/cache742.txt`, using `tools/OpenRs2CacheItemSearch.java` from commit bffcef6c76dc81b32cb015ea11c70b25e823707f and the existing local `world-server-2.0.11-all.jar` classpath. Cache 742 is dated 2012-11-07. It corroborates the IDs, equip options, stackability and exchange flags; the existing generated Darkan value table continues to supply guide-value fallbacks. No new server mechanics are inferred.

Black robe is cache item 581, Black robe top; the alias preserves the drop/equipment storage identity and supplies its existing cache value 13 and exchange flag. Black mask (10) is exactly 8901; its period page explicitly permits exchanging masks with zero or ten charges. Ogre arrows use singular cache item 2866.

The existing pinned [Calculator:Grand Exchange buying limits oldid 6457777](https://runescape.wiki/w/Calculator%3AGrand_Exchange_buying_limits?oldid=6457777), 2012-10-23T03:28:03Z, supplies all 20 limits. Its retained original packet was read from the canonical tooling cache and copied to `/Users/ArmanTarkhanian1/Documents/ankiscape-pass20/evidence/11/sources/buy-limits-6457777.json`; no new fetch was needed. The mappings are exact except Black robe → Black robe top, Dragon med helm → Dragon helm and Ogre arrows → Ogre arrow. The source snapshot adds only these limits; no new GE price is claimed. Regenerate with `python3 tools/generate_ge_period_data.py generated/grand_exchange_period_generated.py`.

## Item evidence

| Item | Period page / oldid | UTC timestamp | Trade / buy limit | Art result |
|---|---|---|---|---|
| Abyssal whip | [Abyssal whip 5674950](https://runescape.wiki/w/Abyssal_whip?oldid=5674950) | 2012-05-29T12:17:27Z | Yes / 10 | combatitems/abyssal_whip.png (2010-11-02T03:16:58Z) |
| Adamant boots | [Adamant armoured boots 5588920](https://runescape.wiki/w/Adamant_armoured_boots?oldid=5588920) | 2012-05-10T07:21:55Z | Yes / 100 | combatitems/adamant_boots.png (2012-03-09T17:42:04Z) |
| Adamant dart (p) | [Adamant dart 5588897](https://runescape.wiki/w/Adamant_dart?oldid=5588897) | 2012-05-10T07:19:33Z | Yes / 1000 | Absent: no verified pre-cutoff file for the poisoned variant |
| Adamant spear | [Adamant spear 5588923](https://runescape.wiki/w/Adamant_spear?oldid=5588923) | 2012-05-10T07:21:56Z | Yes / 100 | combatitems/adamant_spear.png (2012-11-19T22:38:33Z) |
| Black knife | [Black knife 5287092](https://runescape.wiki/w/Black_knife?oldid=5287092) | 2012-02-25T12:35:15Z | Yes / 10000 | combatitems/black_knife.png (2012-11-19T22:38:46Z) |
| Black mask (10) | [Black mask 5393767](https://runescape.wiki/w/Black_mask?oldid=5393767) | 2012-03-17T15:03:20Z | Yes / 10 | combatitems/black_mask_10.png (2011-11-18T02:53:25Z) |
| Black robe | [Black wizard robe top 5512171](https://runescape.wiki/w/Black_wizard_robe_top?oldid=5512171) | 2012-04-19T11:57:29Z | Yes / 100 | combatitems/black_robe.png (2012-02-01T03:22:04Z) |
| Bronze boots | [Bronze armoured boots 5607829](https://runescape.wiki/w/Bronze_armoured_boots?oldid=5607829) | 2012-05-13T18:58:36Z | Yes / 100 | combatitems/bronze_boots.png (2012-02-21T02:52:11Z) |
| Dragon chainbody | [Dragon chainbody 5515483](https://runescape.wiki/w/Dragon_chainbody?oldid=5515483) | 2012-04-20T12:43:48Z | Yes / 10 | combatitems/dragon_chainbody.png (2012-03-19T20:42:32Z) |
| Dragon med helm | [Dragon helm 5680469](https://runescape.wiki/w/Dragon_helm?oldid=5680469) | 2012-05-29T23:56:11Z | Yes / 100 | combatitems/dragon_med_helm.png (2012-03-06T19:04:47Z) |
| Dragon platelegs | [Dragon platelegs 5687263](https://runescape.wiki/w/Dragon_platelegs?oldid=5687263) | 2012-05-31T08:56:20Z | Yes / 10 | combatitems/dragon_platelegs.png (2012-03-06T19:18:48Z) |
| Dragon plateskirt | [Dragon plateskirt 5687250](https://runescape.wiki/w/Dragon_plateskirt?oldid=5687250) | 2012-05-31T08:55:00Z | Yes / 10 | combatitems/dragon_plateskirt.png (2012-03-08T04:55:39Z) |
| Granite maul | [Granite maul 5574210](https://runescape.wiki/w/Granite_maul?oldid=5574210) | 2012-05-06T20:44:08Z | Yes / 10 | combatitems/granite_maul.png (2010-08-06T15:51:14Z) |
| Iron boots | [Iron armoured boots 5298555](https://runescape.wiki/w/Iron_armoured_boots?oldid=5298555) | 2012-02-28T18:53:43Z | Yes / 100 | combatitems/iron_boots.png (2012-02-21T02:52:40Z) |
| Mystic fire staff | [Mystic fire staff 5167551](https://runescape.wiki/w/Mystic_fire_staff?oldid=5167551) | 2012-01-20T01:22:37Z | Yes / 100 | combatitems/mystic_fire_staff.png (2010-11-03T05:23:56Z) |
| Ogre arrows | [Ogre arrow 5385773](https://runescape.wiki/w/Ogre_arrow?oldid=5385773) | 2012-03-15T19:28:54Z | Yes / 1000 | combatitems/ogre_arrows.png (2010-08-08T06:51:01Z) |
| Rune boots | [Rune armoured boots 5395499](https://runescape.wiki/w/Rune_armoured_boots?oldid=5395499) | 2012-03-18T15:33:17Z | Yes / 100 | combatitems/rune_boots.png (2012-04-25T01:12:22Z) |
| Rune dart | [Rune dart 5503278](https://runescape.wiki/w/Rune_dart?oldid=5503278) | 2012-04-17T12:54:14Z | Yes / 1000 | combatitems/rune_dart.png (2011-11-27T23:44:49Z) |
| Rune dart (p) | [Rune dart 5503278](https://runescape.wiki/w/Rune_dart?oldid=5503278) | 2012-04-17T12:54:14Z | Yes / 1000 | combatitems/rune_dart_p.png (2011-11-27T23:42:39Z) |
| Shade robe | [Shade robes 5504443](https://runescape.wiki/w/Shade_robes?oldid=5504443) | 2012-04-17T21:31:17Z | No / — | combatitems/shade_robe.png (2011-11-28T12:48:02Z) |
| Steel arrow (p) | [Steel arrow 5199763](https://runescape.wiki/w/Steel_arrow?oldid=5199763) | 2012-01-30T07:56:00Z | Yes / 1000 | Absent: no verified pre-cutoff file for the poisoned variant |

## Art

All art is downloaded through `tools/fetch_assets.py`, `tools/reresearch_period_art.py` or `tools/historical_assets/fetch_resolved_assets.py`, with source SHA-1 checks. The move-aware tool follows renamed File pages. The latest Iron armoured boots and Staff of fire archive URLs returned bytes inconsistent with their API SHA-1; earlier authenticated period revisions were used instead. Mystic fire staff's period page states that its appearance is identical to Staff of fire.

Adamant dart (p) and Steel arrow (p) stay text-only. Their ordinary unpoisoned icons are not substituted. The exact poisoned histories checked are retained in `/Users/ArmanTarkhanian1/Documents/ankiscape-pass20/evidence/11/poison-art.jsonl`: Adamant dart (p).png starts 2012-12-16T22:32:46Z; Steel arrow (p).png resolves to Steel arrow (p) 5.png, whose retained history starts 2025-02-14T04:59:58Z. Rune dart (p) has its own authenticated 2011-11-27T23:42:39Z image. No art is generated.

## Verification and limits

`tests/equipment/test_missing_items.py` checks every base equipment definition against the registry, every new item's period trade verdict and real buy-offer preview, source-backed art, and a real Gargoyle review finishing with an Adamant boots drop. That same boots item can be held, worn, returned to Bank and escrowed in a real sell offer at 1920. The existing GE data tests retain their unresolved-identity set; the buy-limit count increases by exactly 20.

The offscreen menu evidence covers Bank and Grand Exchange, light and Fusion dark, 720×540 default and 720×560. `/Users/ArmanTarkhanian1/Documents/ankiscape-pass20/evidence/11/visual-check.json` records geometry checks and Bank hover text. Native verification belongs to the orchestrator.

Mutated bloodveld and Giant frog Adamant-boots drop routes remain absent by the settled scope. Existing unrelated equipment discrepancies were observed but not changed: Black mask (10) requires Defence 20 / Strength 10 in the catalog, versus Defence 10 / Strength 20 / Combat 40 in its period page; Shade robe item 546 has Prayer 9 in the catalog versus 5 in rev 742 (the period set page's 9 covers top and bottom together).
