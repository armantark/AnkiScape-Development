# Player attack calculations

Base: `5888f215ee1bd6fb6cdc3e003a7dfe57a2f4c56a`. This plan is frozen before implementation. P4 owns this source slice only. The parent owns runtime authorization, independent review, full gates and promotion.

## Contract

Extract the duplicated player attack roll and maximum-hit formulas into one private helper in logic_pure/logic_pure_combat_engine.py. Inputs are current player data, combat class, style ID, melee style type, prepared equipment totals, prepared prayer effects, selected ammo, spell specification and spell ID. Return exactly the attack roll and maximum hit. Preserve expression order, fallback factors and current-level reads within each formula.

Keep ammo selection, enemy defence calculation, initial-only Warriors Guild multiplier, accuracy calculation, drain application and all RNG calls in the caller. Keep initial and post-drain calls. Do not extend this slice into preview, live prayer scaling, protection, damage, encounter scheduling or any UI.

Called formula helpers read their inputs. Equipment totals and enemy totals are prepared values; charged spell calculation sanitizes into a new arena state. No callback, RNG or shared-state mutation occurs within these calculations. The initial caller will prepare ammo and enemy defence before calculating player attack/max hit together. This changes only the ordering of independent reads of prepared values; formula expression order and state sampling remain unchanged. No broader contract is needed.

## Evidence and acceptance

The full baseline engine is retained as baseline-engine.py.gz with decoded SHA256 486a532d00d4e5693894b77a022ef83a32e03f55e841c2ff92ab12fc7e9ad2d4. initial-pins.json binds the baseline, installed static gate and measuring tools before edits. Neither the baseline nor the instrument may change.

Add a few focused whole-burst behavior checks. Prepare a whole-burst differential probe against the frozen engine, including complete returned state/result, input nonmutation, RNG draws and generator state. Assert that the claimed routes occur: melee/ranged/magic initialization and actual stat drains, prayer-blocked drain, independent ranged attack/strength prayer factors, charged spell, and the initial-only Guild multiplier. Use the existing cockatrice, basilisk, spectre and Guild mechanics. Do not create impossible compound enemy mechanics to reach branches.

Prepare negative source and optimized-interpreter canaries that stop before product imports. Parent runtime remains required; static preparation executes no tests, product imports, gameplay, remote commands or test discovery. Run the installed static layout checker before freezing final source hashes. Retain an explicit source inventory, whole-file restorable product diff, raw static measurements and gate ratchet results. Product/test/probe and operational metadata review packets are each at most 25,000 bytes; full machine evidence stays separate. No pre-existing tests or gates change. No commit is authorized during preparation.
