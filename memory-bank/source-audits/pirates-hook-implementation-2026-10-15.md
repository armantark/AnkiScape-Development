# Pirate’s hook implementation — 2026-10-15

Pirate’s hook now enters the ordinary Grand Exchange (GE) catalog after the existing 800-ticket reward.
Backend changes: tradeability, source item ID 2997, and one exact period row in the source and generated GE maps.
Frontend changes: none. Existing equipment statistics, ticket rules, and all unrelated GE rows remain unchanged.
Pins: item oldid 5508301; Exchange oldid 6112017; global limits oldid 6457777; dated cache revisions 727 and 742.
The game-main bytes have no verified upstream commit. The wiki pages share one lineage. Source review ACCEPT (round 2); Kimi ACCEPT.
Base: `a955e94685e391fede232d10d4eaf27d762e01af`.
Evidence: `/Users/armantarkhanian/Documents/ankiscape-goal-evidence-2026-10-14/pirates-hook-implementation-2026-10-15`.
Before data edits, the real runtime refused the earned reward with `reason: unknown_item`; the original run exited 1.
The product proof passed one collected test, exit 0, with 801 real Brimhaven reducer calls and no catalog stub.
The proof covers exchange and offer Undo, escrow, settlement, collection, and JSON save/reload through existing storage.
The focused neighbor run collected 138 tests and exited 1: `AssertionError: 1443 != 1442`.
Blocker: the fixed test expects 1442 prices and 1837 limits; the authorized new row produces 1443 and 1838.
Do not change this instrument without Root resolution of the explicit fixed-baseline prohibition.
Test-quality, reachability, worktree-layout and diff-check audits exited 0.
The docs audit exceeds the fixed startup budget after required papercut records. The original error and repaired-format rerun remain external.
The fixed-count contract is resolved below. Native PASS and independent native review ACCEPT (round 2); the exact merged gate and official land are pending.
The manual lane continues independently. Historical capture failures do not create a current global unblock question.
File SHA-256 values:
- `data/agility_data.py`: `88e1d67c607dca928ed79f950bfebd8c142fa7ba03a857fc1ccaff7ea0c96f03`
- `data/grand_exchange_period_source.json`: `2592afde9976702fe9ee77b151a108225bc99cd3ee80ac113a491ba54b560361`
- `generated/grand_exchange_period_generated.py`: `8b2b01c1369b899cc5e2e268f4ed7d922b36eecb5256be85b13a8c1fde4f9c1d`
- `tests/item_tradeability/test_pirates_hook_tradeability.py`: `9337ee041216789047255b00a0a12296d5ac588f46097c477dcde1203809a8f7`

## Integration resolution — 2026-10-17

Root authorized the intended Pirate’s hook data addition and resolved the exact-count blocker: `tests/test_grand_exchange_data.py` now requires exactly 1443 prices and exactly 1838 limits, replacing exactly 1442 and 1837. The single new Pirate’s hook row accounts for each increment. Both assertions remain exact equality assertions; no other instrument or product data changes in this integration.
Main `8749ddc60555a5c62f64d8dfbcc04f64f207bcc1` merged normally without conflicts. The exact merged promotion gate with both full lanes and official land are pending.
Integration evidence: `/Users/armantarkhanian/Documents/ankiscape-goal-evidence-2026-10-17/pirates-hook-integration`.

## Acceptance — 2026-10-17
Native PASS on frozen `632ae7c9f023b28b2802df730b6b019424d30980`: `/Users/armantarkhanian/Documents/ankiscape-goal-evidence-2026-10-17/native-lane-2/pirates-hook/`.
Independent native review ACCEPT round 2: `/Users/armantarkhanian/Documents/ankiscape-goal-evidence-2026-10-17/pirates-native-review/report-round2.md`.
Source review ACCEPT round 2: `/Users/armantarkhanian/Documents/ankiscape-goal-evidence-2026-10-17/pirates-hook-source-review/report-round2.md`.
Kimi ACCEPT: `/Users/armantarkhanian/Documents/ankiscape-goal-evidence-2026-10-17/pirates-hook-kimi-vote/kimi-vote-2.md`; exact merged promotion gate and official land are pending.
