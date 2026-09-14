"""Run the Pass 14 focused suites and sequential remote verification lanes."""
from __future__ import annotations

import argparse
import ast
import fcntl
import os
from pathlib import Path
import shlex
import subprocess
import sys


FOCUSED = {
    "s1": (
        "tests.test_integration_smoke",
        "tests.test_cadence_kernel",
        "tests.runtime_actions.test_bankstanding_notice",
        "tests.test_direct_action_undo_seam",
        "tests.test_combat_logic",
        "tests.test_main_menu_widget",
        "tests.ui.test_activity_one_click",
        "tests.test_review_strip_logic",
        "tests.test_storage_pure",
        "tests.combat.test_encounter_lifecycle",
        "tests.ui.test_encounter_transitions",
    ),
    "s2": (
        "tests.test_runtime_actions",
        "tests.runtime_actions.test_slayer_completion",
        "tests.test_slayer_logic",
        "tests.ui.test_slayer_progress",
        "tests.test_main_menu_widget",
        "tests.test_dialog_lifecycle",
        "tests.test_achievement_diaries",
        "tests.test_achievement_diaries_integration",
        "tests.test_achievement_diary_ledger_wiring",
        "tests.runtime_actions.test_dispatcher_state",
        "tests.test_direct_action_undo_seam",
        "tests.test_integration_smoke",
    ),
}


def measure_surfaces(root: Path, slice_name: str, logs: Path) -> None:
    sys.path.insert(0, str(root / "tools"))
    import run_remote_tests as remote

    pins_tree = ast.parse((root / "tests/test_module_surface.py").read_text())
    pinned_modules = next(
        ast.literal_eval(node.value)
        for node in pins_tree.body
        if isinstance(node, ast.Assign)
        and any(
            isinstance(target, ast.Name) and target.id == "FIRST_WAVE_DIGESTS"
            for target in node.targets
        )
    )
    modules = (*pinned_modules, "ui/ui.py")
    remote._preflight("qt")
    remote.LOCAL_MIRROR_LOCK_PATH.parent.mkdir(parents=True, exist_ok=True)
    with remote.LOCAL_MIRROR_LOCK_PATH.open("a+") as lock:
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
        remote._sync(root)
        for lane, interpreter, modules in (
            ("plain", "/opt/homebrew/bin/python3", modules),
            ("qt", str(remote.REMOTE_VENV / "bin/python"), ("__init__.py", *modules)),
        ):
            environment = "QT_QPA_PLATFORM=offscreen "
            if lane == "plain":
                environment += f"PYTHONPATH={shlex.quote(str(remote.REMOTE_PLAIN_SITE))} "
            command = (
                f"cd {shlex.quote(str(remote.REMOTE_REPO))} && "
                f"{environment}"
                f"{shlex.quote(interpreter)} tools/module_surface.py --digest-only "
                + shlex.join(modules)
            )
            output = remote._ssh(command, label=f"{lane} module surfaces", repeat_safe=True)
            with (logs / f"{slice_name}-{lane}-surfaces.log").open("x") as log:
                log.write(output + "\n")
            print(output, flush=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("slice", choices=FOCUSED)
    parser.add_argument("--logs", type=Path, required=True)
    parser.add_argument("--focused-only", action="store_true")
    parser.add_argument("--lanes-only", action="store_true")
    parser.add_argument("--surfaces-only", action="store_true")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[2]
    args.logs.mkdir(parents=True, exist_ok=True)
    if args.surfaces_only:
        measure_surfaces(root, args.slice, args.logs)
        return 0
    commands = [] if args.lanes_only else [
        ("focused", [str(root / ".venv-qt/bin/python"), "-m", "unittest", *FOCUSED[args.slice]]),
    ]
    if not args.focused_only:
        commands.extend(
            (lane, [sys.executable, "tools/run_remote_tests.py", str(root), lane])
            for lane in ("plain", "qt")
        )
    for lane, command in commands:
        log = args.logs / f"{args.slice}-{lane}.log"
        print(f"START {lane}: {log}", flush=True)
        with log.open("x") as output:
            output.write(f"COMMAND: {command!r}\n")
            output.flush()
            result = subprocess.run(
                command, cwd=root, stdout=output, stderr=subprocess.STDOUT,
                env={**os.environ, "QT_QPA_PLATFORM": "offscreen"},
            )
        print(f"EXIT {lane}: {result.returncode}", flush=True)
        if result.returncode:
            return result.returncode
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
