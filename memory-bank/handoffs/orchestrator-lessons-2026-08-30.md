# Orchestrator Lessons — 2026-08-30

## Read this before new fan-out

Low model cost is not orchestration efficiency. Measure total requests, prompt volume, cache volume, retries, tool calls, wall time, and useful accepted output.

Large GLM fan-out is valid when each token buys distinct useful coverage. The objective is maximum accepted value per total provider token, not minimum model use or minimum agent count.

Do not repeat workflow run `wf_6d69103c-870` or reuse its script shape. Its script is at:

`/Users/ArmanTarkhanian1/.claude-claudex/projects/-Users-ArmanTarkhanian1-Library-Application-Support-Anki2-addons21-ankiscape-fork/56d8d23a-e661-4318-8e28-30eaf1999572/workflows/scripts/ankiscape-papercut-triage-wf_6d69103c-870.js`

## What the dashboard showed

The owner's 48-hour OpenRouter dashboard showed:

- 573 million tokens.
- 6,000 requests.
- $14.90 total spend.
- A 95.9% cache-hit rate.
- A blended rate of $0.03 per million tokens.

The dashboard covers this thread and the Darkan thread. The steep traffic drop when this thread stopped makes this workflow the main likely source. Exact per-thread attribution was not measured.

The high cache-hit rate reduced cost. It did not make the request or token volume efficient.

## Exact GLM workflow result

The papercut workflow dispatched four GLM 5.3 Flash range agents.

- Two agents completed.
- Two agents failed after six attempts each.
- Completed agents produced 191,430 workflow-reported tokens and made 120 tool calls.
- Failed agents made 1,665 tool calls without a result.
- The lines 761-1140 agent made 788 tool calls and recorded `9541634` duration milliseconds.
- The lines 1141-end agent made 877 tool calls and recorded `9543528` duration milliseconds.
- The lines 1-380 agent needed three attempts, produced 86,194 tokens, and made 51 tool calls.
- The lines 381-760 agent completed once, produced 105,236 tokens, and made 69 tool calls.

These are harness measurements. They do not include the dashboard's full prompt and cache accounting.

## Root cause

The model choice was not the primary error. The orchestration design was the error.

Each GLM agent received a 380-line historical range plus repository-wide verification duties. The prompt asked one intern model to discover, group, inspect current source, decide status, propose fixes, and preserve detailed evidence.

The retry policy then allowed six attempts after progress stalls. Each retry replayed a large context and repeated repository discovery. The workflow converted cheap model tokens into excessive requests, cached prompt traffic, tool calls, and wall time.

The orchestrator measured returned tokens and useful findings. It did not measure total provider traffic before judging efficiency.

## Required process for large ledgers

1. Read the ledger once with a deterministic script when that costs fewer tokens than repeated agent discovery.
2. Extract timestamp, exact error, path, command, and proposed remedy.
3. Normalize repeated errors and paths into cause clusters.
4. Write shared frozen evidence packets before agent dispatch.
5. Start ledger-triage packets at or below 32,768 bytes. Increase a packet only when the added context has clear expected value.
6. Partition fan-out by non-overlapping causes, files, or evidence ranges so each leaf buys new coverage.
7. Use GLM across a large fleet when each leaf has a distinct scope and a compact shared context.
8. Retry a stalled leaf only after identifying a likely failure cause and changing its scope, packet, or prompt.
9. Stop a leaf when the expected value of another retry is lower than its token and wall-time cost. Keep productive leaves running.
10. Deduplicate all findings before expensive verification, then send only survivors to Terra or Opus when factual stakes need it.

Do not make every GLM leaf repeat open-ended discovery and full verification when one shared discovery pass can feed many bounded checks.

## GLM 5.3 Flash lane

Use GLM for:

- Bulk classification over frozen packets.
- Easy bounded code with a complete specification.
- Vision reads.
- Mechanical repository sweeps with explicit paths.
- A cheap extra cross-lineage vote.

Large GLM workflows are appropriate when fan-out increases distinct coverage faster than it increases repeated context.

Use GLM with these limits:

- Do not use it as the sole reviewer for high-stakes claims.
- Do not make many leaves repeat the same repository-wide search.
- Do not replay an unchanged stalled prompt through six attempts.
- Do not replace a cheaper deterministic transform with repeated model discovery.
- Do not ask broad design questions when the specification can first narrow the decision space.

Judge GLM output quality separately from orchestration efficiency. Two useful results do not justify thousands of failed tool calls, but large useful fleets remain valid.

## Workflow design rules

- Use a deterministic transform before a model barrier.
- Use `pipeline()` when each item can advance independently.
- Use a barrier only for real cross-item deduplication.
- Pass frozen evidence into verification agents.
- Keep discovery and verification in different stages.
- Log every omitted class and every coverage cap.
- Compare the expected value of each retry with its full prompt, cache, tool, and wall-time cost.
- Preserve large productive fan-out; stop only duplicate or low-yield leaves.
- Inspect provider-wide request and prompt volume when available.
- Track accepted findings, accepted fixes, and distinct coverage per total provider token.
- Do not infer efficiency from spend alone.

## Scope rules learned in this session

Papercut remediation came from a separate owner request. It was not part of the original active goal. Do not fold a side request into goal completion accounting without an explicit link.

The active goal says to stop and record an another-writer collision on main. That blocks repair, merge, and promotion on main. It does not block independent authoring in guarded worktrees from the last stable commit.

Do not stop all useful work when only main promotion is blocked.

## User-interface boundary

Do not change an existing user interface without explicit owner approval. A clipping, reachability, or accessibility defect does not authorize a redesign.

A new interface can belong to approved implementation work. Before promotion, send it to a model with demonstrated frontend taste.

Do not add replacement style rules when the owner asks for a revert. Restore the last owner-settled behavior exactly.

## Current clean-break state

The exact current state is in:

- `memory-bank/activeContext.md`.
- `memory-bank/progress.md`.
- `memory-bank/loop-queue.md`.
- `memory-bank/GOAL-BLOCKED.md`.

Three papercut branches are preserved and unmerged:

- `goal/papercut-test-cwd-2026-08-30` at `63a3409c0dd3b45f87548fdbcd74056bbc758e19`.
- `goal/papercut-worktree-bootstrap-2026-08-30` at `b861cdecf96d729e1f46b200e6e9313fd0730cb8`.
- `goal/papercut-reachability-check-2026-08-30` at `8f1092db1b6355fe83a02eeb32b0715c36cb9d99`.

The first branch passed the MacBook plain lane with `Ran 4526 tests in 251.013s` and `OK (skipped=513)`. Its Qt lane and both later branch gates remain unrun.

Canonical `main` remains blocked by an another-writer change to `memory-bank/source-audits/post-cutoff-asset-revisions-2026-08-21.json`. Do not stage, revert, repair, or commit that foreign change.
