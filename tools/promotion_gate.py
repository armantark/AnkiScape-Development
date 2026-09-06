#!/usr/bin/env python3
"""Run promotion checks and land only the exact commit that passed them."""

from __future__ import annotations

import argparse
import ast
import fcntl
import json
import os
import re
import subprocess
import sys
import tempfile
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Callable, IO, Sequence, TextIO

if __package__:
    from .promotion.cli import install_hook, main
    from .promotion.contract import (
        ACTIVE_GATE_DIR_NAME,
        EVIDENCE_DIR_NAME,
        FULL_GATE_CHECKS,
        LAND_LOCK_NAME,
        LONGEST_LANE_TIMEOUT,
        PLAIN_GATE_CHECKS,
        PLAIN_LANE_TIMEOUT,
        QT_LANE_TIMEOUT,
        GateError,
        GateEvidence,
        LockRecord,
    )
    from .promotion.landing import _load_landing_evidence, is_ancestor, land
    from .promotion.lane_execution import (
        PROGRESS_LINE,
        REACHABILITY_PIN_FIELDS,
        REACHABILITY_PIN_METHOD,
        ResultValidator,
        _reachability_log_lines,
        _reachability_result_matches_pins,
        _read_reachability_pins,
        _read_reachability_report,
        _run_bounded,
        _run_check,
        _run_gate_checks,
        _run_reachability_check,
        _tail_without_progress,
        _worktree_is_clean,
        _write_evidence,
        run_gate,
    )
    from .promotion.locking import (
        HeldLock,
        _invalidate_evidence,
        _new_lock_record,
        _read_record_path,
        _reclaim_stale_lock,
        _record_age,
        _write_record,
        active_gate_dir_for,
        active_gate_records,
        claim_gate_marker,
        claim_landing_lock,
        landing_lock_path_for,
        register_gate,
    )
    from tools.promotion.promotion_process import (
        format_age,
        kill_process_tree,
        open_locked_file,
        pid_is_alive,
    )
    from .promotion.repository import (
        _git,
        _worktree_rows,
        commit_at,
        evidence_path_for,
        git_common_dir,
        main_worktree,
        safe_log_root,
    )
else:  # direct execution from tools/
    from promotion.cli import install_hook, main
    from promotion.contract import (
        ACTIVE_GATE_DIR_NAME,
        EVIDENCE_DIR_NAME,
        FULL_GATE_CHECKS,
        LAND_LOCK_NAME,
        LONGEST_LANE_TIMEOUT,
        PLAIN_GATE_CHECKS,
        PLAIN_LANE_TIMEOUT,
        QT_LANE_TIMEOUT,
        GateError,
        GateEvidence,
        LockRecord,
    )
    from promotion.landing import _load_landing_evidence, is_ancestor, land
    from promotion.lane_execution import (
        PROGRESS_LINE,
        REACHABILITY_PIN_FIELDS,
        REACHABILITY_PIN_METHOD,
        ResultValidator,
        _reachability_log_lines,
        _reachability_result_matches_pins,
        _read_reachability_pins,
        _read_reachability_report,
        _run_bounded,
        _run_check,
        _run_gate_checks,
        _run_reachability_check,
        _tail_without_progress,
        _worktree_is_clean,
        _write_evidence,
        run_gate,
    )
    from promotion.locking import (
        HeldLock,
        _invalidate_evidence,
        _new_lock_record,
        _read_record_path,
        _reclaim_stale_lock,
        _record_age,
        _write_record,
        active_gate_dir_for,
        active_gate_records,
        claim_gate_marker,
        claim_landing_lock,
        landing_lock_path_for,
        register_gate,
    )
    from promotion.promotion_process import (
        format_age,
        kill_process_tree,
        open_locked_file,
        pid_is_alive,
    )
    from promotion.repository import (
        _git,
        _worktree_rows,
        commit_at,
        evidence_path_for,
        git_common_dir,
        main_worktree,
        safe_log_root,
    )

__all__ = (
    "ACTIVE_GATE_DIR_NAME",
    "Callable",
    "EVIDENCE_DIR_NAME",
    "FULL_GATE_CHECKS",
    "GateError",
    "GateEvidence",
    "HeldLock",
    "IO",
    "LAND_LOCK_NAME",
    "LONGEST_LANE_TIMEOUT",
    "LockRecord",
    "PLAIN_GATE_CHECKS",
    "PLAIN_LANE_TIMEOUT",
    "PROGRESS_LINE",
    "Path",
    "QT_LANE_TIMEOUT",
    "REACHABILITY_PIN_FIELDS",
    "REACHABILITY_PIN_METHOD",
    "ResultValidator",
    "Sequence",
    "TextIO",
    "active_gate_dir_for",
    "active_gate_records",
    "annotations",
    "argparse",
    "asdict",
    "ast",
    "claim_gate_marker",
    "claim_landing_lock",
    "commit_at",
    "dataclass",
    "datetime",
    "evidence_path_for",
    "fcntl",
    "format_age",
    "git_common_dir",
    "install_hook",
    "is_ancestor",
    "json",
    "kill_process_tree",
    "land",
    "landing_lock_path_for",
    "main",
    "main_worktree",
    "open_locked_file",
    "os",
    "pid_is_alive",
    "re",
    "register_gate",
    "run_gate",
    "safe_log_root",
    "subprocess",
    "sys",
    "tempfile",
    "uuid",
)


if __name__ == "__main__":
    raise SystemExit(main())
