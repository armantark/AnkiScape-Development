# Priority matrix — 2026-08-30

This file stores the ranked work census for AnkiScape.

- Date: `2026-08-30`.
- Main commit: `3a93e0ad5cc2a7e4c09e54515557b488085eebe6`.
- The orchestrator must select each future slice from this file.
- Source rows use the repository state at that commit.

## Census

Each command runs from the repository root.
Each Markdown command uses `grep -c` or `grep -Ec` with the shown unit pattern.
The JSON command parses every status field.

| source registry | command result | source units | matrix rows | treatment |
| --- | ---: | ---: | ---: | --- |
| `memory-bank/design-thread-queue.md` | 58 section `3.x` or `5.x` headings | 58 | 58 | Keep all headings. Keep closed headings as `complete`. |
| `memory-bank/future-work-kanban.md` | 53 card headings | 53 | 21 | Keep 21 active or residual cards. Exclude 31 complete-only cards. Merge the diary card into `DT-5.21`. |
| `memory-bank/gap-backlog.json` | 45 status rows | 45 | 45 | Keep every status row. |
| `memory-bank/placeholder-values.md` | 179 register rows | 179 | 179 | Keep every registered placeholder. |
| `memory-bank/loop-queue.md` | 69 checklist records | 69 | 2 | Exclude 66 checked records. Merge one unchecked parent with its unchecked child. |
| `memory-bank/breadth-next-tranche.md` | 10 struck table rows | 10 | 0 | All ten rows are complete. |
| `memory-bank/encounter-gap-ranking-2026-08-26.md` | 14 table rows | 14 | 13 | Carry 13 rows forward. Merge the diary row into `DT-5.21`. |
| `memory-bank/diary-curation-ledger/README.md` | 2 gate records | 2 | 0 | Attach both gates to `DT-5.21`. |
| `memory-bank/papercuts.md` | 768 bullet entries | 1 | 1 | Treat the full corpus as one work unit. |
| Papercut branch state | 3 named branches | 3 | 3 | Keep two landed branches as `complete`. Keep one rebase as `integration-blocked`. |
| **Total** |  | **434** | **322** | Consolidation removes 112 duplicate or complete-only source records. |

The source census has 434 unit references.
The final matrix has 322 distinct rows.
The arithmetic is `58 + 53 + 45 + 179 + 69 + 10 + 14 + 2 + 1 + 3 = 434`.
The matrix arithmetic is `58 + 21 + 45 + 179 + 2 + 0 + 13 + 0 + 1 + 3 = 322`.

### Reproducible count commands

1. Count the design queue units.

```sh
grep -Ec '^### (3|5)\.[0-9]+' memory-bank/design-thread-queue.md
```

Expected result: `58`.

2. Count the forward Kanban cards.

```sh
grep -cE '^### ' memory-bank/future-work-kanban.md
```

Expected result: `53`.

3. Count the gap rows and print the status histogram.

```sh
python3 - <<'PY'
import collections
import json
from pathlib import Path

items = json.loads(Path("memory-bank/gap-backlog.json").read_text())["items"]
histogram = collections.Counter(item["status"] for item in items)
print("total", len(items))
for status in sorted(histogram):
    print(status, histogram[status])
PY
```

Expected result:

```text
total 45
design_partial_waiting_source 1
design_settled 1
design_settled_waiting_source 3
implemented 1
implemented_verified 1
mechanic_complete_split 1
merged 24
parked_farming_seed 1
rejected_out_of_period 1
rejected_product_scope 1
source_blocked_after_darkan_reconciliation 2
source_blocked_waiting_darkan 1
source_harvested_dependency_blocked 1
split_scope 5
verified 1
```

4. Count the registered placeholders.

```sh
grep -c '^| `' memory-bank/placeholder-values.md
```

Expected result: `179`.

5. Count all loop checklist records.

```sh
grep -cE '^[[:space:]]*[-0-9.]+[[:space:]]+\[[ xX]\]' memory-bank/loop-queue.md
```

Expected result: `69`.

6. Count the complete breadth rows.

```sh
grep -cE '^\| ~~.+~~ \|' memory-bank/breadth-next-tranche.md
```

Expected result: `10`.

7. Count the encounter matrix rows.

```sh
grep -cE '^\| ([0-9]+|—) \|' memory-bank/encounter-gap-ranking-2026-08-26.md
```

Expected result: `14`.

8. Count the diary gate records.

```sh
grep -cE '^[0-9]+\. \*\*.*gate:' memory-bank/diary-curation-ledger/README.md
```

Expected result: `2`.

9. Count the papercut entries.

```sh
grep -c '^-' memory-bank/papercuts.md
```

Expected result: `768`.
The matrix treats these entries as one unit.

10. Count the named papercut branches.

```sh
for branch in \
  goal/papercut-test-cwd-2026-08-30 \
  goal/papercut-worktree-bootstrap-2026-08-30 \
  goal/papercut-reachability-check-2026-08-30
do
  git show-ref --verify --quiet "refs/heads/$branch" && printf '%s\n' "$branch"
done | wc -l
```

Expected result: `3`.

### Gap status census

| status | count |
| --- | ---: |
| `design_partial_waiting_source` | 1 |
| `design_settled` | 1 |
| `design_settled_waiting_source` | 3 |
| `implemented` | 1 |
| `implemented_verified` | 1 |
| `mechanic_complete_split` | 1 |
| `merged` | 24 |
| `parked_farming_seed` | 1 |
| `rejected_out_of_period` | 1 |
| `rejected_product_scope` | 1 |
| `source_blocked_after_darkan_reconciliation` | 2 |
| `source_blocked_waiting_darkan` | 1 |
| `source_harvested_dependency_blocked` | 1 |
| `split_scope` | 5 |
| `verified` | 1 |
| **Total** | **45** |

### Blocker census checkpoint

The full row classification will replace this checkpoint.
The final blocker counts must total 322.
