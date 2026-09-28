"""Land the exact commit authorized by promotion evidence."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import TextIO

from .contract import FULL_GATE_CHECKS, GateError, GateEvidence
from .locking import active_gate_records, claim_landing_lock
from .repository import _git, commit_at, evidence_path_for, main_worktree, tracked_changes


def _load_landing_evidence(worktree: Path, commit: str) -> GateEvidence:
    path = evidence_path_for(worktree, commit)
    try:
        evidence = GateEvidence.from_json(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise GateError(
            f"Landing refused: no passed full-gate evidence for exact commit {commit} at {path}"
        ) from None
    except OSError as exc:
        raise GateError(f"Landing refused: cannot read gate evidence {path}: {exc}") from exc
    except GateError as exc:
        raise GateError(f"Landing refused: {exc} at {path}") from exc

    if evidence.schema_version != 1:
        raise GateError(
            f"Landing refused: unsupported gate evidence schema {evidence.schema_version} at {path}"
        )
    if evidence.commit != commit:
        raise GateError(
            f"Landing refused: gate evidence at {path} names {evidence.commit}, not {commit}"
        )
    if evidence.plain_only or evidence.passed_checks != FULL_GATE_CHECKS:
        raise GateError(
            f"Landing refused: evidence for {commit} did not pass every full-gate check; "
            f"recorded {evidence.passed_checks}"
        )
    return evidence


def is_ancestor(repo: Path, ancestor: str, descendant: str) -> bool:
    return _git(
        repo,
        "merge-base",
        "--is-ancestor",
        ancestor,
        descendant,
        check=False,
    ).returncode == 0


def land(
    worktree: Path,
    *,
    stdout: TextIO = sys.stdout,
    stderr: TextIO = sys.stderr,
) -> str:
    worktree = worktree.resolve()
    target_commit = commit_at(worktree)
    landing_lock = claim_landing_lock(
        worktree,
        operation="landing",
        worktree=worktree,
        commit=target_commit,
    )
    try:
        active_gates = active_gate_records(worktree, stderr=stderr)
        for gate in active_gates:
            if gate.commit != target_commit:
                raise GateError(
                    f"Landing refused: running gate PID {gate.pid} has held {gate.commit} in "
                    f"{gate.worktree} since {gate.started_at}; requested {target_commit} in "
                    f"{worktree} is a different tree"
                )
        if active_gates:
            gate = active_gates[0]
            raise GateError(
                f"Landing refused: gate PID {gate.pid} is still running for exact commit "
                f"{target_commit} in {gate.worktree} since {gate.started_at}"
            )

        _load_landing_evidence(worktree, target_commit)
        main_path = main_worktree(worktree)
        main_commit = _git(main_path, "rev-parse", "refs/heads/main").stdout.strip()
        if not is_ancestor(worktree, main_commit, target_commit):
            raise GateError(
                f"Landing refused: {target_commit} in {worktree} is not a descendant "
                f"of current main {main_commit}"
            )

        # A fast-forward keeps edits to files the candidate does not touch, so
        # the live add-on would run bytes the gate never tested.
        canonical_changes = tracked_changes(main_path)
        if canonical_changes:
            raise GateError(
                "Landing refused: canonical checkout has uncommitted tracked changes:\n"
                + "\n".join(canonical_changes)
            )
        merge = _git(
            main_path,
            "merge",
            "--ff-only",
            target_commit,
            check=False,
        )
        if merge.returncode != 0:
            current_main = _git(main_path, "rev-parse", "refs/heads/main").stdout.strip()
            if not is_ancestor(worktree, current_main, target_commit):
                raise GateError(
                    f"Landing refused: {target_commit} is no longer a descendant of current main "
                    f"{current_main}; main moved during landing"
                )
            detail = (merge.stderr or merge.stdout).strip()
            raise GateError(f"Landing failed for {target_commit}: {detail}")
        if merge.stdout:
            print(merge.stdout.rstrip(), file=stdout)
        canonical_changes = tracked_changes(main_path)
        if canonical_changes:
            raise GateError(
                f"Landing of {target_commit} moved main, but canonical checkout {main_path} "
                "gained uncommitted tracked changes during the merge:\n"
                + "\n".join(canonical_changes)
            )
        print(f"Landed {target_commit} from {worktree} onto main in {main_path}", file=stdout)
        return target_commit
    finally:
        landing_lock.release()


_PUBLIC_MODULE = f"{__package__.rsplit('.', 1)[0]}.promotion_gate"
_load_landing_evidence.__module__ = _PUBLIC_MODULE
is_ancestor.__module__ = _PUBLIC_MODULE
land.__module__ = _PUBLIC_MODULE
