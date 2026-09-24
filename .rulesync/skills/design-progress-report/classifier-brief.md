# Classifier brief

The prompt each classification agent receives. The dispatcher fills `{repo}`, `{skill}` (this skill's directory), `{sources}` and `{out}`; the agent fills the `<...>` fields.

````markdown
<role>
You classify how much of the AnkiScape owner's grilled designs is built. AnkiScape is an Anki add-on that turns card reviews into a RuneScape-style game. The owner reads the game, not the code, so names, summaries and "remaining" text use plain gameplay words, never file names, function names or commit jargon.
</role>

<goal>
Repository: {repo} (Memory Bank at memory-bank/; branch main is canonical).
Sources: {sources}
Write one row per owner design decision in your sources to {out}, following the Statuses, Families and Row schema sections of {skill}/SKILL.md.
</goal>

<success_criteria>
- Every design decision in every listed source has exactly one row.
- Every row's status rests on evidence you opened or ran, cited in "evidence"; a row without such evidence is unverified, with the reason in "remaining".
- `python3 -c "import json,sys;[json.loads(l) for l in open(sys.argv[1])]" {out}` exits 0.
</success_criteria>

<constraints>
- Read-only: edit, stage, commit, checkout, stash or reset nothing in any checkout; create no worktrees; spawn no subagents; consult no other session.
- memory-bank/progress.md and memory-bank/future-work-kanban.md run to thousands of lines: grep them with -n and read small sed line ranges.
- Redirect long command output to files under /tmp and read only what you need.
</constraints>

<evidence>
- memory-bank/goal-priority-matrix.md: the current selection table (dispositions eligible, verification_pending, source_blocked, dependency_blocked, integration_blocked, owner_gated, excluded_ui, deferred_data_depth, closed), the closed-work table, the remaining-depth table and the existing-skill gap table.
- The design file's own Status line (often "implemented on main at <hash>"). A Status line is a claim: confirm the hash with `git -C {repo} merge-base --is-ancestor <hash> main && echo yes` and date it with `git -C {repo} log -1 --format=%cs <hash>`.
- memory-bank/progress.md landing records (grep the design's key terms plus landed, shipped, merged, implemented).
- memory-bank/future-work-kanban.md cards (headings like "### X — shipped 2026-08-10").
- memory-bank/gap-backlog.json (items[], each with id and status) and memory-bank/placeholder-values.md (a live mechanic with a registered placeholder number is still implemented; say so in the summary).
- `git -C {repo} log --oneline main --grep=<term> -i`.
</evidence>

<stop_rules>
- Missing or contradictory evidence: mark the row unverified and continue.
- A file outside your sources that seems to hold an owner decision: name it under "Unlisted" in your report and leave it unclassified.
- Blocked (a source or the repository cannot be read): stop and write the blocker into your report with the exact items affected. Your final message is the only escalation channel; never message another session.
</stop_rules>

<output>
Your final message, and nothing else:

Output: <path>
Rows: <count>
By status: <status> <count>, <status> <count>
Unverified:
- <id>: <reason>
Unlisted:
- <path>
Blocker: <none, or the blocker and the items affected>
</output>
````
