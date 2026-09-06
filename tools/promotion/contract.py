"""Shared promotion-gate records and fixed bounds."""

from __future__ import annotations

import json
from dataclasses import dataclass


LAND_LOCK_NAME = "ankiscape-promotion-land.lock"


ACTIVE_GATE_DIR_NAME = "ankiscape-promotion-gates"


EVIDENCE_DIR_NAME = "ankiscape-promotion-evidence"


PLAIN_GATE_CHECKS = (
    "plain lane",
    "audit_docs",
    "audit_test_quality",
    "reachability",
    "worktree_guard",
    "worktree clean",
    "diff check",
)


FULL_GATE_CHECKS = ("plain lane", "Qt lane", *PLAIN_GATE_CHECKS[1:])


PLAIN_LANE_TIMEOUT = 1000.0


QT_LANE_TIMEOUT = 1300.0


LONGEST_LANE_TIMEOUT = max(PLAIN_LANE_TIMEOUT, QT_LANE_TIMEOUT)


class GateError(RuntimeError):
    """A promotion gate or landing precondition failed."""


@dataclass(frozen=True)
class LockRecord:
    pid: int
    operation: str
    worktree: str
    commit: str
    started_at: str
    token: str
    heartbeat_at: str = ""

    @classmethod
    def from_json(cls, text: str) -> "LockRecord":
        try:
            payload = json.loads(text)
            return cls(
                pid=int(payload["pid"]),
                operation=str(payload["operation"]),
                worktree=str(payload["worktree"]),
                commit=str(payload["commit"]),
                started_at=str(payload["started_at"]),
                token=str(payload["token"]),
                heartbeat_at=str(payload.get("heartbeat_at", payload["started_at"])),
            )
        except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
            raise GateError(f"Promotion lock is unreadable: {exc}") from exc


@dataclass(frozen=True)
class GateEvidence:
    schema_version: int
    commit: str
    worktree: str
    plain_only: bool
    remote_lanes: bool
    passed_checks: tuple[str, ...]
    completed_at: str

    @classmethod
    def from_json(cls, text: str) -> "GateEvidence":
        try:
            payload = json.loads(text)
            passed_checks = payload["passed_checks"]
            if not isinstance(passed_checks, list) or not all(
                isinstance(label, str) for label in passed_checks
            ):
                raise TypeError("passed_checks must be a list of strings")
            plain_only = payload["plain_only"]
            if not isinstance(plain_only, bool):
                raise TypeError("plain_only must be a boolean")
            remote_lanes = payload.get("remote_lanes", False)
            if not isinstance(remote_lanes, bool):
                raise TypeError("remote_lanes must be a boolean")
            return cls(
                schema_version=int(payload["schema_version"]),
                commit=str(payload["commit"]),
                worktree=str(payload["worktree"]),
                plain_only=plain_only,
                remote_lanes=remote_lanes,
                passed_checks=tuple(passed_checks),
                completed_at=str(payload["completed_at"]),
            )
        except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
            raise GateError(f"Promotion evidence is unreadable: {exc}") from exc


_PUBLIC_MODULE = f"{__package__.rsplit('.', 1)[0]}.promotion_gate"
GateError.__module__ = _PUBLIC_MODULE
LockRecord.__module__ = _PUBLIC_MODULE
GateEvidence.__module__ = _PUBLIC_MODULE
