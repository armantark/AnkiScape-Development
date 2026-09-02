"""Process-tree and lock-age utilities for promotion tooling."""

from __future__ import annotations

import os
import signal
import subprocess
import time


def pid_is_alive(pid: int) -> bool:
    if pid <= 0:
        return False
    try:
        os.kill(pid, 0)
    except (ProcessLookupError, PermissionError):
        return False
    return True


def format_age(seconds: float) -> str:
    if seconds < 60:
        return f"{seconds:.0f}s"
    minutes, remainder = divmod(int(seconds), 60)
    if minutes < 60:
        return f"{minutes}m {remainder}s"
    hours, minutes = divmod(minutes, 60)
    return f"{hours}h {minutes}m"


def _process_children() -> dict[int, tuple[int, ...]]:
    result = subprocess.run(
        ("ps", "-axo", "pid=,ppid="),
        check=False,
        text=True,
        capture_output=True,
    )
    children: dict[int, list[int]] = {}
    for line in result.stdout.splitlines():
        fields = line.split()
        if len(fields) != 2:
            continue
        try:
            pid, parent = (int(field) for field in fields)
        except ValueError:
            continue
        children.setdefault(parent, []).append(pid)
    return {parent: tuple(pids) for parent, pids in children.items()}


def _descendants(pid: int) -> tuple[int, ...]:
    children = _process_children()
    found: list[int] = []
    pending = list(children.get(pid, ()))
    while pending:
        child = pending.pop()
        found.append(child)
        pending.extend(children.get(child, ()))
    return tuple(reversed(found))


def _signal_processes(pids: tuple[int, ...], signum: signal.Signals) -> None:
    for pid in pids:
        try:
            os.kill(pid, signum)
        except (ProcessLookupError, PermissionError):
            pass


def _signal_group(pid: int, signum: signal.Signals) -> bool:
    try:
        if os.getpgid(pid) != pid:
            return False
        os.killpg(pid, signum)
    except (OSError, ProcessLookupError):
        return False
    return True


def kill_process_tree(pid: int, *, process_group: bool = False) -> None:
    if pid <= 0:
        return
    if process_group and _signal_group(pid, signal.SIGTERM):
        time.sleep(0.1)
        _signal_group(pid, signal.SIGKILL)
        return
    descendants = _descendants(pid)
    targets = descendants if pid == os.getpid() else (*descendants, pid)
    _signal_processes(targets, signal.SIGTERM)
    time.sleep(0.1)
    _signal_processes(targets, signal.SIGKILL)
