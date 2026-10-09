# Papercuts fixed — 2026-10-08

## Observatory source lookup assumptions

Disposition: record_only.

Evidence: No source path is missing. rg --files located reorganized data, runtime and test modules; preserve the exact lookup errors.

- 2026-10-08 — Observatory opening startup reads used stale root paths: cat: AGENTS.md: No such file or directory; tests/test_fenkenstrain_opening.py: No such file or directory; quest_data.py: No such file or directory; runtime/runtime_actions_quest.py: No such file or directory; tools/generation/README.md: No such file or directory. Source now lives in data/quest/, runtime/runtime_actions_production.py and tests/runtime_actions/test_fenkenstrain_opening.py; use rg --files before reads.

## Observatory schema lookup assumptions

Disposition: record_only.

Evidence: Inspected the real catalog/default schema and located renamed modules before any focused proof. Preserve these author lookup mistakes; no product repair is needed.

- 2026-10-08 — Observatory schema probe indexed journal_stages as a sequence and raised KeyError: 0; live journals are stage-keyed. Additional assumed paths were absent: tests/test_quest_data.py; data/utility_data.py; data/npc_shop_data.py; core/constants_parts/gathering.py; data/npc_shop*. Locate files with rg --files before targeted reads; pending XP key is pending_skill_exp_rewards.
- 2026-10-08 — Observatory static-route probe assumed UTILITY_TARGETS was exported and raised ImportError: cannot import name 'UTILITY_TARGETS' from 'ankiscape.core.constants' (/Users/ArmanTarkhanian1/Library/Application Support/Anki2/ankiscape_worktrees/promote-2026-10-03b/core/constants.py); context lookup also reported runtime/runtime_action_context.py: No such file or directory. rg located UTILITY_ACTIVITY_DATA in core/constants_parts/activity_updates.py and runtime/runtime_actions_context.py. No product or live state changed.

## Observatory provenance lookup assumption

Disposition: record_only.

Evidence: The existing music log source files were located before the static and pure-model route check. No product source was missing; preserve the exact author lookup error.

- 2026-10-08 — Observatory provenance review lookup assumed core/music* existed; rg reported core/music*: No such file or directory. rg --files located logic/music_log_logic.py and data/music_log_data.py before the generic music-route check.
