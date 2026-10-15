# Pirate’s hook implementation — 2026-10-15

Pirate’s hook now enters the ordinary Grand Exchange (GE) catalog after the existing 800-ticket reward.
Backend changes: tradeability, source item ID 2997, and one exact period row in the source and generated GE maps.
Frontend changes: none. Existing equipment statistics, ticket rules, and all unrelated GE rows remain unchanged.
Pins: item oldid 5508301; Exchange oldid 6112017; global limits oldid 6457777; dated cache revisions 727 and 742.
The game-main bytes have no verified upstream commit. The wiki pages share one lineage. Independent source acceptance remains open.
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
Root must resolve the fixed-count contract before a clean neighbor gate. Root also owns independent review, native checks and the exact merged full9 gate.
The manual lane continues independently. Historical capture failures do not create a current global unblock question.
File SHA-256 values:
- `data/agility_data.py`: `88e1d67c607dca928ed79f950bfebd8c142fa7ba03a857fc1ccaff7ea0c96f03`
- `data/grand_exchange_period_source.json`: `2592afde9976702fe9ee77b151a108225bc99cd3ee80ac113a491ba54b560361`
- `generated/grand_exchange_period_generated.py`: `8b2b01c1369b899cc5e2e268f4ed7d922b36eecb5256be85b13a8c1fde4f9c1d`
- `tests/item_tradeability/test_pirates_hook_tradeability.py`: `9337ee041216789047255b00a0a12296d5ac588f46097c477dcde1203809a8f7`
