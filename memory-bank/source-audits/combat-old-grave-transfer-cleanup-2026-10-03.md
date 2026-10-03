# Old grave transfer cleanup — 2026-10-03

Status: source authoring; root-owned behavior and native acceptance remain pending.

## Scope and authority

Fixed base `0bbf4aa494c3bff9ab5dc78f95b2595f6ec2d088`; branch `goal/death-grave-transfer-2026-10-03`. Leaf 10 in `/Users/ArmanTarkhanian1/Library/Application Support/Anki2/ankiscape_worktrees/.orchestrator/contracts-2026-10-03-codex-resume.md` owns this boundary. Only the old-grave transfer in `_combat_apply_pvm_death`, baseline transfer lines 847–863, under the guard at line 846, moves to a helper. Existing helpers retain sanitation, fee and loadout policy. No gameplay ruling changes.

## Failure modes recorded before editing

1. A gravestone-free death transfers or replaces an existing grave: retain the caller's `if not no_grave` guard.
2. An empty or malformed old grave changes the office: retain `_combat_grave_items` and its truthy-item gate; do not read the office when this gate is false.
3. Existing office items disappear, reorder, or deduplicate: concatenate sanitized office items before old grave items and preserve duplicate units.
4. A duplicate equipment slot changes ownership: unpack old grave loadout first and existing office loadout second.
5. Fee or source changes: retain `_set_combat_death_office_items` and exact `combat_stacked_grave` source.
6. Mutation or exception order changes: keep raw-state reads, sanitizer calls, loadout reads, item concatenation and setter in the original order; retain outer and nested aliases.
7. The new grave loses current equipment/carried units or resets change: call only after `_combat_settle_carried_death` and before equipment/new-grave writes; all other caller statements stay equal AST.
8. RNG, callbacks, follower loss, protection, discharge, active/dormant packs, wilderness, safe death or equipment sanitation change: leave these responsibilities untouched.
9. An oversized module grows or a new helper exceeds installed complexity limits: final source must stay at most 2,788 physical lines; measure the installed instruments without changing rails.

## Evidence

Raw source and check evidence is outside the tracked tree at `/Users/ArmanTarkhanian1/Library/Application Support/Anki2/ankiscape_worktrees/.orchestrator/tasks-2026-10-03-codex-resume/death-transfer-evidence`.

## Pending root acceptance

Root owns before/after full death behavior comparison; die with an old grave and existing office items, create and reclaim the new grave, then pay/reclaim office items with occupied equipment retaining newer gear; save/reload and genuine Undo; fresh test inventory, focused/shared-neighbor execution, full branch plain lane, exact merged plain/Qt gate, and native Anki acceptance. No product code runs on Studio. Branch Qt is omitted under the explicit promotion-gate exception. Source inspection alone does not prove runtime behavior.

## Static source result

The helper `_combat_transfer_old_grave_to_office` occupies lines 802–815. Its guarded caller site remains after carried settlement and before equipment/new-grave writes. The source stays exactly 2,788 physical lines; the helper maximum line width is 84 characters. The original two-line rationale is retained. Only the final transfer call is shortened: item concatenation is assigned after both loadout reads, then passed to the existing setter. No unrelated source compression funds the helper.

- Baseline source SHA-256: `25b799fb3bf81fec10fa6af3010685b3543d2eda83d75089be01e6c70533afb1`.
- Candidate source SHA-256: `7271110fbfe3f2ece3c5ef21487d9ca3caf3532f613dd959a40f7cea2df0a95e`.
- All 170 other top-level declarations compare equal AST. After resolving the helper call and its two local dataflow bindings, the caller compares equal AST. This is a static scope/dataflow proof, not executed behavior evidence.
- Installed limits: CCN 15, cognitive 15, Halstead difficulty 80. Caller before: 19 / 20 / 3.6. Caller after: 16 / 16 / 3.3333333333333335. Helper: 4 / 3 / 1.0, with no violations. Both measurement commands exit 1 because inherited caller complexity remains over its limits; every inherited metric decreases.
- `python3 tools/audit_docs.py`: exit 0; `Audited 890 Markdown and 454 HTML files.`; `Documentation audit passed.` Both pre-commit and committed checks include the new source-audit record: the instrument inventories cached and untracked documentation with `git ls-files --cached --others --exclude-standard`. The committed check also passes with the same exact counts.
- `python3 tools/audit_test_quality.py`: exit 0; `5169 tests across 331 files`; `hard issues: 0`; `structural clone candidates: 32 groups`; the exact full output is retained in `quality.log` and the check summary in `checks.json`.
- `python3 tools/worktree_guard.py audit`: exit 0; `Worktree layout safe: /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork`; `Linked worktree root: /Users/ArmanTarkhanian1/Library/Application Support/Anki2/ankiscape_worktrees`.
- `git diff --check`: exit 0, no output.

`python3 tools/audit_item_reachability.py --check` remains required and pending with root. The instrument imports product modules, so running it on Studio would violate the leaf contract. Root explicitly confirmed this ownership; it is not an audit waiver. No existing test inventory, behavior differential, branch plain, merged plain/Qt or native check has been run by this author.

## Friction and preserved incident text

The two timestamped lines in `memory-bank/papercuts.md` retain the exact missing-path errors from authority/static-check discovery. No historic incident was removed or rewritten.
