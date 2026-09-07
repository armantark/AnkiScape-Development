# Complexity recovery papercuts

- 2026-09-06T05:27Z: The parent attempted a read-only progress snapshot as remote Qt completed; the pending record was already removed and `read_text` raised `FileNotFoundError: [Errno 2] No such file or directory: '/Users/ArmanTarkhanian1/Library/Caches/ankiscape-remote-test-host.pending.json'`. Reconcile the completion log when the pending record disappears; do not assume it persists between observations. No remote command ran or retry was needed.
- 2026-09-06T05:29Z: The first scoped move-history query used `git log --all`, which included hundreds of `refs/t3/checkpoints` entries and truncated the output. Restrict this audit to `--branches` or immutable accepted commits.

- 2026-09-07: Reconciliation initially included below-threshold Lizard rows; its duplicated nested name `_on_main_menu._on_main_menu._apply_achievement_diary_command._change` did not uniquely match the AST. Restored the retained audit's above-threshold raw-row scope; no metrics rerun or evidence replacement.

- 2026-09-07: Parent evidence verifier checked all 56 snapshot rows, then raised `KeyError: 'ast_sha256'` because the 5 provisional rows lacked that field. Added the same AST identity and retained raw metric rows to provisional evidence; original compressed measurements remain unchanged.
- 2026-09-07: After the interrupted run, root attempted to resume stale process 2951 and received `Unknown process id`; reconcile persisted outputs before assuming a process remains resumable.
