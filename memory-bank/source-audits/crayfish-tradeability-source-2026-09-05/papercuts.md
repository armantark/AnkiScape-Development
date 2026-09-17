# Source inquiry papercuts

- 2026-09-05: Initial bounded Darkan probes used src at the umbrella repository and unmatched zsh globs; actual source is darkan-world-server/src. game-main is a non-Git snapshot, so git log returned fatal: not a git repository (or any of the parent directories): .git. Source custody uses exact file bytes and hashes instead.
- 2026-09-05: Latest Crayfish item oldid 6446586 (2012-10-20T03:58:10Z) is marked {{beta}}. The first beta child 5838149 and its unmarked parent 5517594 were retained; direct tradeability comes from the unmarked parent. Initial generated-cache filename guess was wrong; current data live in generated/item_values_generated.py and have no exact dated cache-ID provenance.
- 2026-09-05: Reading the MBP manifest with full query argv produced a truncated tool response because each classpath is long. Subsequent verification reads exact fields and hashes without printing the classpath. The retained raw manifest remains complete.
