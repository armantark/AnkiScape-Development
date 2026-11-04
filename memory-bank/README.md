# Memory Bank Index

The Memory Bank separates current project truth from durable historical evidence.
Start with the current entry points below; consult dated contracts and audits when
their owning workstream requires deeper context.

## Current entry points

- [Project Brief](projectbrief.md): product scope and non-negotiable boundaries.
- [Product Context](productContext.md): intended player experience and current surface.
- [Active Context](activeContext.md): present implementation and verification state.
- [System Patterns](systemPatterns.md): architecture and durable engineering conventions.
- [Technical Context](techContext.md): runtime, tooling, evidence, and test environment.
- [Progress](progress.md): chronological completion ledger.
- [Goal priority matrix](goal-priority-matrix.md): selection authority for the implementation goal.
- [October goal pickup](pickup-2026-10-03.md): resume and acceptance boundaries; [Active Context](activeContext.md) and [Progress](progress.md) own later work.
- [Completion Kanban](future-work-kanban.md): product-wide parity and depth backlog.
- [Class rulings](grill-decisions-2026-10-25.md): owner rulings that settle whole classes of contract questions
  (Darkan where the period sources are silent, unsourced values, quest step reviews, text-only panel changes).
- [Class rulings, 2026-10-28](grill-decisions-2026-10-28.md): quest details where sources disagree, the taught
  quest route with no optional danger, and supply-step prices, XP and requirement stops.
- [Roadmap](roadmap.md): dependency-ordered completion strategy.
- [Gap backlog](gap-backlog.json): closed historical record of the existing-skill parity subledger; the Kanban owns its open rows.
- [Public release lineage and license decision](public-release-lineage-and-license-2026-07-17.md):
  settled derivative-release posture, attribution copy, and ordered go-live gates.

The memory bank is the agents' own space; the owner does not read it (2026-10-01), so agents apply staleness-sweep rewrites themselves instead of nominating them.

## Evidence and design directories

- `source-audits/`: authoritative sourced mechanics, conflicts, and verification records.
- `audits/`: durable cross-cutting audit coverage and provenance.
- `codex-briefs/`: active implementation briefs only.
- `status-updates/`: the latest human-facing closure reports plus its archive index.
- `archive/`: completed handoffs, superseded baselines, and resolved queues retained
  for provenance but excluded from current-work discovery.

## Archive rule

Age alone never makes a document obsolete. Move a file to `archive/` only when a
named live successor owns its remaining work, the archived file contains no unique
open decision, and all inbound paths are updated. Source audits and governing
contracts remain in place even after implementation because they continue to own
evidence and design intent.
