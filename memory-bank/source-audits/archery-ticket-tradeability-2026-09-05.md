# Archery ticket tradeability and non-pouch cohort

Date: 2026-09-05. Author branch: `goal/archery-ticket-tradeability-2026-09-05`. Baseline: `ffb846d6631e4b73731f6573dd8d7c0e77e439db`.

## Result and scope

Archery ticket, item `1464`, has an explicit incorrect `tradeable=False` declaration. The pinned pre-EOC item page states `tradeable = Yes` separately from `exchange = gemw`. Correct that declaration and add the qualified `5,000` buy limit through the existing curated data writer. This allows both GE offer sides without adding an unresolved-limit exemption.

The bounded non-pouch cohort contains 37 storage keys whose baseline registry flag is false while their names occur in the committed cache exchangeability set. One row is source-ready; 36 remain unresolved. None of those 36 was established as legitimately untradeable by this bounded source read. Their flags remain unchanged. The 80 familiar pouches are excluded and belong to their separate source slice. The generic Summoning ingredient `Pouch`, item `12155`, remains in this cohort.

This is not a uniform default-value defect. The cohort includes explicit Crafting and Agility declarations, Fist of Guthix equipment metadata, and generated shop stock or currency declarations. Name membership alone does not authorize any correction.

## Pinned evidence

The [retained source manifest](archery-ticket-tradeability-2026-09-05/SUMMARY.md) records the exact source paths, byte counts, and remeasured SHA-256 hashes. These are copies of existing local records; no new source harvest ran.

- [Ranging Guild dated sources](archery-ticket-tradeability-2026-09-05/SUMMARY.md): SHA-256 `1b255c788421892ea8956b426c75afa5a04c99a5df2a4b4e1a66c62cdd7b0ff8`. Revision entry 3 is [Archery ticket oldid 6534408](https://runescape.wiki/w/Archery_ticket?oldid=6534408), timestamp `2012-11-04T20:38:51Z`. Its literal wikitext lines 8, 11, and 15 state `tradeable = Yes`, `stackable = Yes`, and `exchange = gemw`. This is a non-beta item page, not a familiar redirect. Player tradeability comes from the explicit tradeable field, not from the Exchange field.
- [Frozen item identity records](archery-ticket-tradeability-2026-09-05/SUMMARY.md): SHA-256 `33dd8e58dcbf610d5cc648fa2fac06a6101525dad97d153253a20283b8a9d3fc`. The item-full row for `1464` is named `Archery ticket` in both selected row sets, covering builds `727, 728, 729` and `736, 741, 742`. Both give value `25`, inventory option `drop`, and certificate/lent IDs and templates `-1`. These records bind the item identity and value; they do not supply an independent tradeability predicate.
- [Global buying limits](archery-ticket-tradeability-2026-09-05/SUMMARY.md): SHA-256 `58e29b65573b61f0bc772f0764e2ea04fa65254f631976fbf39b5239215a4199`. [Calculator:Grand Exchange buying limits oldid 6457777](https://runescape.wiki/w/Calculator:Grand_Exchange_buying_limits?oldid=6457777), timestamp `2012-10-23T03:28:03Z`, has `|[[Exchange:Archery ticket|Archery ticket]]` on literal line 716 followed by `|5000` on line 717.

The existing Ranging Guild contract is Darkan audit iteration `387`, unit `minigames-ranging-guild`. It already identifies the dated-source and item-cache files above. The local search did not recover a pinned per-item `Exchange:Archery ticket` response in the existing GE cache. No per-item Exchange oldid, guide price, or per-item limit field is claimed. The non-beta item page's explicit tradeability and exchange fields, cache identity, and exact global-limit row provide the bounded qualification used here.

## Consumer effects

| Surface | Baseline | Corrected behavior |
|---|---|---|
| Registered item | Item `1464`, stackable, explicitly non-tradeable | Same identity and stacking; tradeable |
| GE catalog | Excluded by the registry flag despite existing cache-name membership | Eligible with guide price `25` from the unchanged cache-value fallback |
| GE buy offer | Item absent; a flag-only correction would leave its limit unresolved | Buy limit `5,000` from the pinned global table |
| GE sell offer | Item absent | Earned tickets can enter sell escrow and collection |
| Magic alchemy picker and runtime | Excluded by the tradeability flag | Eligible with High Alchemy `15` and Low Alchemy `10`, matching the pinned item infobox |
| Ranging Guild earnings | Score divided by 10, claimed once | Unchanged |
| Ranging Guild rewards | Ticket costs and reward quantities in the dedicated exchange | Unchanged |
| Ordinary NPC shop sale | Rejected by the registry's false flag | The existing general-store path can accept it at the existing generated sell price `7`, subject to normal access and stock-capacity checks |

`core/item_registry.py` carries the explicit declaration into the registry. `data/grand_exchange_data.py` checks that flag, exact storage-key membership, a positive period price or cache value, and the buy-limit mapping. The existing cache-name set already contains `Archery ticket`, with cache value `25`; there is no current period guide price for the item.

`logic/shop_logic.py` checks shop visibility, access, currency identity, and specialist stock before the item tradeability gate. Archery ticket occurs in no current shop stock row, service input/output, or vendor action input/output. The only ordinary-shop behavior change is removal of the incorrect registry veto; specialist restrictions, prices, and stock definitions are unchanged. The dedicated Ranging Guild claim and reward functions operate on ticket inventory and do not read this flag. `runtime/runtime_actions_magic.py:409` and `ui/ui.py:6754` also filter alchemy items by the registry tradeability flag and the shop buy-value map. The correction admits Archery ticket to both surfaces, with High Alchemy `15` and Low Alchemy `10` derived from the unchanged value `25`. These outputs match the pinned item infobox lines 9 and 10. No UI code changes are needed.

## Generated-data custody

The author used `tools.generate_ge_period_data.write_generated` with the existing guide prices, existing price provenance, existing global buy-limit source, and the existing limit mapping plus only `Archery ticket: 5000`. No harvesting command ran.

[The AST mapping comparison](archery-ticket-tradeability-2026-09-05/SUMMARY.md) records that the guide-price map and price-provenance map each retain all 1,437 entries, and the global-source mapping remains identical. The buy-limit mapping changes from 1,753 to 1,754 entries, with only `Archery ticket` added. The simultaneous pouch slice must merge its separately qualified additions into this mapping without replacing either slice's entries.

## Cohort dispositions

[The structured cohort](archery-ticket-tradeability-2026-09-05/SUMMARY.md) records each storage key, current registry source, registry ID, candidate IDs, baseline and corrected flags, cache value, period guide price, and current buy limit. IDs in parentheses below are candidate joins recovered from existing source metadata where the registry itself omits the ID. They are not qualified tradeability proof. `Yak-hide armour` collapses recipe variants `10824` and `10822` into one storage key, so the 37-row cohort is not a 37-distinct-source-ID claim.

| Storage key | Item identity | Disposition |
|---|---|---|
| Jade | (1611; registry ID absent) | Unresolved; preserve current flag. |
| Red topaz | (1613; registry ID absent) | Unresolved; preserve current flag. |
| Yak-hide armour | 10824, 10822 | Unresolved variant identity; preserve current flag. |
| Pouch | 12155 | Unresolved; preserve current flag. |
| Pirate's hook | (2997; registry ID absent) | Unresolved; preserve current flag. |
| Spotted cape | (10069; registry ID absent) | Unresolved; preserve current flag. |
| Spottier cape | (10071; registry ID absent) | Unresolved; preserve current flag. |
| Crayfish | 13433 | Unresolved; preserve current flag. |
| Worn-out bronze gauntlets | 12986 | Unresolved condition-specific source conflict; preserve current flag. |
| Archery ticket | 1464 | Correct explicit false flag; add qualified GE limit. |
| Blue boots | 630 | Unresolved; preserve current flag. |
| Blue hat | 660 | Unresolved; preserve current flag. |
| Blue robe bottoms | 650 | Unresolved; preserve current flag. |
| Bone dagger | 8872 | Unresolved; preserve current flag. |
| Boots | 2894 | Unresolved; preserve current flag. |
| Cream boots | 632 | Unresolved; preserve current flag. |
| Cream hat | 662 | Unresolved; preserve current flag. |
| Cream robe bottoms | 652 | Unresolved; preserve current flag. |
| Gloves | 2902 | Unresolved; preserve current flag. |
| Green boots | 628 | Unresolved; preserve current flag. |
| Green hat | 658 | Unresolved; preserve current flag. |
| Green robe bottoms | 648 | Unresolved; preserve current flag. |
| Hat | 2900 | Unresolved; preserve current flag. |
| Pink boots | 626 | Unresolved; preserve current flag. |
| Pink hat | 656 | Unresolved; preserve current flag. |
| Pink robe bottoms | 646 | Unresolved; preserve current flag. |
| Robe bottoms | 2898 | Unresolved; preserve current flag. |
| Rock climbing boots | 3105 | Unresolved; preserve current flag. |
| Shirt | 5030 | Unresolved; preserve current flag. |
| Shorts | 5042 | Unresolved; preserve current flag. |
| Skewered chompy | 7230 | Unresolved; preserve current flag. |
| Skirt | 5048 | Unresolved; preserve current flag. |
| Trading sticks | (6306; registry ID absent) | Unresolved; preserve current flag. |
| Trousers | 5036 | Unresolved; preserve current flag. |
| Turquoise boots | 634 | Unresolved; preserve current flag. |
| Turquoise hat | 664 | Unresolved; preserve current flag. |
| Turquoise robe bottoms | 654 | Unresolved; preserve current flag. |

The Worn-out bronze gauntlets record must be reconciled to item `12986` and its worn-out condition before a change. A tradeability statement for a different charged or combat form cannot clear that gate. The remaining unresolved rows need their own exact period source reconciliation. No broader cohort repair is authorized by this record.

## Verification status and required MacBook checks

The focused regression in `tests/test_ranging_guild.py` uses the real registered GE catalog. It earns 100 tickets through ten reviews and one claim, sells one ticket, buys one ticket, advances and collects each offer, then purchases a Coif for 12 tickets. Collection checks positive sale proceeds and the exact credited coin balance on both offer sides. It also checks item `1464`, the `5,000` limit, and the unchanged cache-value guide source. The pre-existing registry assertion is corrected from false to true. `tests/test_grand_exchange_data.py` retains its exact count assertion and updates the expected count from `1_753` to `1_754` for the one qualified addition. Its catalog-subset assertion and unresolved-identity guard are unchanged.

No product test, full lane, or native UI check has run on the author's Studio. These remain orchestrator-owned MacBook gates. Run `tests.test_ranging_guild`, `tests.test_grand_exchange_data`, `tests.test_grand_exchange_logic`, and the existing shop suites before the full plain and offscreen Qt lanes. Keep `test_only_audited_unresolved_identities_remain_buy_limit_blocked` unchanged; Archery ticket must not enter its exception set.

Native verification must use the proven disposable profile: earn and claim tickets, place and collect a sell offer, place and collect a buy offer, and spend tickets through the Ranging Guild reward exchange. Confirm the GE shows the item and its limit and rewards retain their costs. Open the Magic panel and confirm the alchemy picker lists Archery ticket with `H 15 / L 10`. Check all visible text for truncation. Existing access gates and ordinary shop prices must remain intact. Review, commit, full gates, and native acceptance are pending.

## Independent review resolution

The bounded Opus review on 2026-09-05 found the source-qualified correction minimal and correct, with no blocking defect. It read the product and test diff and traced the deterministic GE regression; it ran no product tests, full lanes, or native checks, and did not independently re-fetch or re-hash the retained sources. The author's retained-file hash checks and AST mapping comparison are separate evidence.

- F1: Added the alchemy runtime and picker to the consumer table and native checklist. Their `H 15 / L 10` outputs match the literal source infobox; no UI code changed.
- F2: Strengthened the existing regression to require positive sale proceeds and an exact inventory coin credit when an offer is collected. No separate test or product logic was added.
- F3: Retained the explicit qualification that `25` is the pre-existing cache-value fallback, not a recovered period Exchange guide price.
- F4: The review accepted the preserved-map proof: one limit key is added, with the other maps unchanged.

This resolves the review findings for a draft author commit. Focused MacBook execution, both full lanes, native acceptance, and promotion remain pending.


## Driver capture and semantic verification retained on 2026-09-06 UTC

The driver captured the frozen branch `7f3adcdeb6448b3127386ecc995c39f41a535368` on the MacBook from `2026-09-05T23:57:34.165390+00:00` through `2026-09-05T23:57:57.291866+00:00`. [The retained manifest](archery-ticket-tradeability-2026-09-05/SUMMARY.md) binds all seven product, test, and instrument files before and after capture. The author rehashed those same seven current branch files during retention; each still matches the historical capture. This section supersedes the earlier pending focused-execution statements. It does not change the full-gate or native-acceptance requirements.

Both focused lanes passed the three exact selectors in `capture.json`, with no skipped tests. The raw summaries report `Ran 3 tests in 0.021s` for plain and `Ran 3 tests in 0.020s` for Qt. These checks cover the changed ticket registration, the new earned-ticket sell/buy/collection and guild-reward path, and the unchanged unresolved-buy-limit boundary. The full stdout and stderr are retained as deterministic gzip files. The generated-count assertions and full suites were not selected by this focused probe.

The driver reviewed and ran [the semantic proof](archery-ticket-tradeability-2026-09-05/SUMMARY.md), SHA256 `5aa8b7a86dbd7beb42677f518fd43b306c135891995fd3d414498403b66d96ca`. The proof passed for the required 11 plain and 12 Qt payloads. It checked every complete body against its footer, retained each whole-file hash, and reconstructed the baseline bodies byte for byte after reversing only the qualified Archery ticket changes. Nine payloads changed and fourteen were byte-identical. The separate empty plain-root baseline control is preserved and excluded from the required payload set.

The observed existing-record delta is only `tradeable=False` to `tradeable=True` for item `1464` in the Ranging Guild metadata, merged extra-item metadata, and unique `material_archery_ticket` definition. The Qt root adds only the qualified Archery ticket GE row. All prior catalog rows, export names, metadata, and retained ordering remain unchanged. Raw ticket metadata uses `source_item_id`, and the proof checks that exact field. The full catalog-row assertion preserves the cache-value guide source, empty guide-price provenance, qualified limit, and existing alchemy values. No runtime field, surface pin, count assertion, or exception set was changed during evidence retention.

The complete discovery lists preserve every baseline test ID and its order. Each lane adds only `test_ranging_guild.RangingGuildPureMechanicsTests.test_earned_tickets_can_be_traded_and_spent_on_guild_rewards`, once. The proof records the existing retained baseline discovery files and hashes; the candidate lists and empty stderr files are retained here without trimming.

Full surface bodies remain at the exact local and MacBook report directories in the manifest. `semantic-proof.json` binds each basename, complete-body digest, and whole-file digest. They were not copied into Git. The capture probe, guarded local driver, and semantic-proof script are retained as gzip records of their exact reviewed bytes. The original report and baseline files remain unchanged.

Independent measurement review session `38477` is pending at this retention checkpoint. Instrument reconciliation requires the driver's review decision. Both full MacBook lanes, repository checks, native acceptance, and the exact merged-tree gate remain pending. The earlier source and implementation review resolution remains valid; source closure alone does not certify these remaining stages.

Current checkpoint: Independent measurement review session `38477` accepted the proof, and the five measured surface digests are applied. The existing limit-count assertion remains `1_754` and was verified unchanged. Full MacBook and repository checks, native acceptance, and the exact merged-tree gate remain pending.
