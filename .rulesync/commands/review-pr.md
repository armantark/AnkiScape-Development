---
description: 'Review a pull request'
targets: ["*"]
---

target_pr = $ARGUMENTS

If target_pr is not provided, use the PR of the current branch.

Execute the following in parallel:

1. Check code quality and style consistency
2. Review test coverage
3. Verify documentation updates
4. Check for potential bugs or security issues
5. Run `/opt/homebrew/bin/python3 tools/maintenance/slop_gate_preflight.py --base <merge-base-commit>` on the exact reviewed checkout

Do not approve unless the preflight exits 0. If the reviewed tree changes, rerun it before providing the summary of findings and suggestions for improvement.
