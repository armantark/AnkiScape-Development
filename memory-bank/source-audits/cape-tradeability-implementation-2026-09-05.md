# Cape tradeability implementation

## Contract before implementation

Spotted cape `10069` and Spottier cape `10071` must use ordinary Grand Exchange buy, sell, collection, and persistence behavior. Change only their Agility tradeability and source IDs, then add their qualified period prices `406` and `633`, provenance, and separate buy limits `100` through the existing writer. Preserve every other generated entry, the global limit source, equipment identity and metadata, cache values `400` and `800`, assets, and acquisition routes.

The source baseline is `cd6747a62f2295afd6afd77090bf4ec1d8f69dd9`. The source packet and its accepted review remain unchanged. `cape-tradeability-implementation-2026-09-05/owner-snapshot.json` retains the driver's evaluated owner proof; its SHA-256 is `8bd35892bceb93375df2e7a304d52563de32286ee3085d09e842dd800c03b931`. The driver extracted it from complete MacBook snapshots and verified identical product paths between capture `6438d42256236992b10d921d4cca920293b55d93` and this source baseline. It records Agility as the owner of false tradeability and missing source IDs; equipment enrichment preserves those fields.

## Verification boundary

The author will use static parsing, whole-map comparison, documentation audit, and diff checks only. A new cohesive regression module will cover the changed items without inheriting another discoverable TestCase or growing capped modules. The driver owns runtime tests, current module surfaces, census measurements, the full gate, and native manual verification. Focus and discovery results are now retained below; full-gate and native acceptance remain pending. Hash and count pins may change only with measured driver evidence and explicit authorization; the approved changes and their bounds are recorded below.

## Authored change and static evidence

The existing Agility tradeable set now includes both cape names, and its source-ID map includes `10069` and `10071`. `owner-map-delta.json` proves that removal of just those entries restores the complete baseline AST. Equipment definitions, weight-reduction logic, and generated cache values remain byte-identical to the baseline.

The existing period-data writer consumed the retained qualified rows without a product import or network call. `generated-map-delta.json` compares every original and resulting map entry: only the two capes are added to guide prices, buy limits, and price provenance. No prior entry changes or disappears. The global limit source is unchanged. `buy_limit` is excluded from price provenance.

## Direct tradeability consumers

- `data/grand_exchange_data.py:60` admits the capes to the catalog; `logic/grand_exchange_logic.py:438` uses normal offer validation. The new runtime regression drives the existing menu callback through buy and sell escrow, deterministic market fills, collection, and storage reload. It preserves equipped gear throughout. A second test runs the same lifecycle through a real temporary Anki Collection. The fixture installs fresh runtime fakes for each single add-on load; both cape names share that load. It does not substitute completed orders for actual matching.
- The change to `_item_tradeable` in `logic/shop_logic.py` (since moved to `logic/shop/state.py`) removes the registry veto for NPC selling, including temporary general-store stock. The regression checks one sale of each cape at the existing `120` and `240` coin prices.
- `runtime/runtime_actions_magic.py:409` and `ui/ui.py:6792`/`:6809` make owned capes eligible for the existing alchemy picker and target checks. The regression uses the real value-map builder and low/high alchemy actions: Spotted cape yields `160`/`240` coins and Spottier cape yields `320`/`480`, from unchanged values `400`/`800`. These filters do not govern Superheat. Native picker display still needs verification.
- `logic/shattered_heart_logic.py:308` includes tradeable names in its replacement set, but lines 347–354 intersect that set with the current eligible skilling action's actual outputs. Neither cape is a current skilling output; GE collection and NPC sale are direct actions. The existing output-replacement regressions remain applicable; no cape producer or Shattered Heart behavior was added.

## Driver verification queue

The driver completed discovery and focused execution under the new package. The author has run no runtime tests. Exact selectors:

- `tests.item_tradeability.test_cape_tradeability.CapeTradeabilityDataTest.test_registry_and_market_preserve_equipment_identity`
- `tests.item_tradeability.test_cape_tradeability.CapeTradeabilityDataTest.test_existing_shop_and_alchemy_consumers_use_unchanged_values`
- `tests.item_tradeability.test_cape_tradeability.CapeTradeabilityRuntimeTest.test_buy_sell_collection_and_reload`
- `tests.item_tradeability.test_cape_tradeability.CapeTradeabilityRuntimeTest.test_buy_sell_persist_in_real_anki_collection`

The real-Collection test explicitly skips when Anki is unavailable and passed in the driver’s Qt lane with Anki installed. The driver measured discovery and all protected module surfaces, then compared their full bodies as recorded below. The independent Opus evidence review accepted the five proposed hash literals, and the driver explicitly authorized their application. The driver independently compared the complete generated AST and authorized only the existing guide-price and buy-limit count assertions to change from `1_437`/`1_753` to `1_439`/`1_755` in `tests/test_grand_exchange_data.py:192`. All other assertions and cutoff checks remain intact. Only the five approved module hash literals changed, with complete-byte reversal proof. Full-gate and native acceptance remain pending.

Native manual steps, queued for the driver's computer-use owner:

1. Use a reversible canary profile and find both complete cape names in the ordinary Grand Exchange catalog. Check prices `406`/`633`, buy limits `100`, icons, and untruncated labels.
2. Buy and collect one of each, then sell and collect it through the ordinary flow. Reload the profile between escrow and collection and verify balances, item counts, and saved order state.
3. Equip each cape and verify the existing identity, bonuses, and weight reduction remain unchanged; trading an inventory copy must preserve the equipped copy.
4. With owned copies, verify both alchemy picker labels and low/high values, plus normal general-store sale behavior. Check visible text for clipping or ellipses.

## Author checks

Static parsing passed for the two edited product modules and the new regression module. Whole-owner and whole-generated-map comparisons passed. All 54 original source manifest bindings and the original source manifest hash remain unchanged. The owner snapshot copy is byte-exact. Documentation and diff checks passed. These are author-side static checks. The historical failure and passing revised focus results are recorded below; full-gate and native acceptance remain pending.

The driver's complete generated-AST comparison also verified unchanged scalar/global fields: removal of only the six cape entries restores the baseline AST. The count-only test edit was checked by exact reversal of its two replacements; the original file is otherwise identical.

## Historical focus failure and revised fixture

The original test hash `2419373b5f545e4804c5c0a6044637c9a418754a67e222aebf517ace256e459a` ran on the MacBook at its former `tests/test_cape_tradeability.py` path. The retained plain result ran 18 tests with 4 failures and 1 skip; Qt ran 18 tests with 8 failures. The data/identity and shop/alchemy tests passed in both lanes. The first lifecycle failure was the full-inventory comparison at line 127 during the Spotted cape buy reload; the rendered diff reported `Diff is 87117 characters long. Set self.maxDiff to None to see it.` The expected default inventory contained `'Pot': 0`, while the loaded inventory omitted that legacy key. Later sell failures cascaded because the preceding buy had not reached fill and collection.

An empty Collection loads defaults through `core/storage.py:43–47`; a saved Collection uses `migrate_loaded_data`. The loader applies `_migrate_legacy_crafting_inventory` at `core/storage_pure.py:1983`, which removes the legacy key according to `data/crafting_data.py:422` (`Pot` to `Empty pot`). The fixture now performs one actual save/reload before seeding Coins and equipment. It retains every complete inventory, order, limit, and equipment equality and every cape/coin assertion. The sequential lifecycle remains intact, with no seeded sell item.

All six original focus files are retained as byte-exact gzip payloads in `focus-2419373b/`, with original and compressed hashes in `focus-2419373b-binding.json`. The historical bytes are not rewritten for the new module location. The raw Opus review and finding-by-finding resolution are retained beside them. The revised module adds the exact two-name snapshot assertion and a one-order assertion before indexing. It resides in `tests/item_tradeability/` with an empty initializer to respect the enforced file-count cap. The driver then ran these revisions successfully in both lanes, as recorded below.


## Passing revised focus and measured pin proposal

The driver ran test SHA `42165b1d09052c6a6001587f788c5c0062b71379587d4c6c94f3f77e09b3a4a7` on the MacBook. Plain ran 18 tests in `0.498s` and returned `OK (skipped=1)`; the sole skip was `Anki runtime is not installed`. Qt ran 18 tests in `1.087s` and returned `OK`, including the real temporary Anki Collection lifecycle. Discovery increased from `5562` to `5566` in each lane: each of the four packaged cape test IDs appeared exactly once and no ID disappeared. These are focused execution and discovery results, not full-suite acceptance.

All 13 supplied repair files are retained as byte-exact deterministic gzip payloads in `repair-42165b1d/`. The binding file records original and compressed byte lengths and SHA-256 values. The author rehashed all seven bound source files, including the unchanged surface tool and pin file, against the tested revision.

The driver validated every module footer against its complete body, then compared all 23 protected payloads. Nine changed and 14 were byte-identical. For constants, shop logic, and the two action modules, reversal of only the two cape `tradeable`/`source_item_id` fields restored each complete baseline public surface. The root Qt surface gained only the two qualified GE catalog rows (`1772` to `1774`); reversal restored its complete baseline. Every other public name, value, and sequence order was preserved. The driver also verified that the baseline-to-source commit comparison changed no product, surface-tool, or pin path.

This complete-body validation and reversal was performed by the driver. The author retained and checked the compact proof rather than independently replaying its remote bodies. The immutable raw files remain in `/Users/armantarkhanian/ankiscape-remote-test-host/reports/cape-repair-42165b1d` and `/Users/armantarkhanian/ankiscape-remote-test-host/reports/cut-gem-baseline-6438d422`. The retained `whole-surface-proof.json.gz` identifies every raw filename and both baseline/candidate body and whole-file hashes.

`module-pin-proposal.json` derives five distinct literal replacements from that proof and verifies their old values against the unchanged `tests/test_module_surface.py`. The four first-wave replacements apply equally in plain and Qt; the fifth is the root Qt digest. The Qt shop override remains unchanged. The frozen proposal remains the reviewed input. The independent Opus evidence review accepted all five replacements, and the parent driver explicitly authorized their application. `module-pin-application.json` proves that reversal of only those five literals restores the complete prior file byte for byte. The raw review and its authorization limits are retained. No other pin, surface tool, threshold, product field, or test behavior changed. The full branch gate must execute these applied pins; full-gate and native acceptance remain pending.
