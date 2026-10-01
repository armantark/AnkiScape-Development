import fcntl
import json
import os
import resource
import signal
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
FIRST = "- 2026-09-20T09:00:00-07:00 — first"
SECOND = "- 2026-09-21T09:00:00-07:00 — second"
THIRD = "- 2026-09-22T09:00:00-07:00 — third"
FOURTH = "- 2026-09-23T09:00:00-07:00 — fourth"


class MovePapercutsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.memory_bank = self.root / "memory-bank"
        self.memory_bank.mkdir()
        self.papercuts = self.memory_bank / "papercuts.md"
        self.papercuts.write_text(
            "\n".join(("# Papercuts", "", FIRST, SECOND, THIRD, FOURTH)) + "\n", encoding="utf-8"
        )
        subprocess.run(["git", "init", "-q"], cwd=self.root, check=True)
        subprocess.run(["git", "add", "--", "memory-bank"], cwd=self.root, check=True)
        # A tree id is a valid base, so the fixture needs no commit or hooks.
        self.base = subprocess.run(
            ["git", "write-tree"], cwd=self.root, check=True, capture_output=True, text=True
        ).stdout.strip()

    def _tool(self, *args: str, **kwargs) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(ROOT / "tools" / "memory_bank" / "move_papercuts.py"), "--root", str(self.root), *args],
            check=False,
            capture_output=True,
            text=True,
            **kwargs,
        )

    def _plan(self, destination: str, heading: str, lines: list[str], name: str = "plan.json") -> str:
        plan = self.root / name
        plan.write_text(json.dumps({
            "destination": f"memory-bank/papercuts-fixed-{destination}.md",
            "sections": [{
                "heading": heading,
                "disposition": "fixed",
                "evidence": "commit abc123 repairs the recorded cause",
                "lines": lines,
            }],
        }), encoding="utf-8")
        return str(plan)

    def _snapshot(self) -> dict[str, bytes]:
        return {path.name: path.read_bytes() for path in self.memory_bank.iterdir()}

    def test_move_appends_sections_verbatim_and_passes_the_check(self) -> None:
        plan = self.root / "plan.json"
        plan.write_text(json.dumps({
            "destination": "memory-bank/papercuts-fixed-2026-09-25.md",
            "sections": [
                {
                    "heading": "Cause A — 2 occurrences",
                    "disposition": "fixed",
                    "evidence": "commit abc123 repairs cause A",
                    "lines": [FOURTH, FIRST],
                },
                {
                    "heading": "Cause B — 1 occurrence",
                    "disposition": "duplicate",
                    "evidence": "Cause A remains the retained repair record",
                    "lines": [THIRD],
                },
            ],
        }), encoding="utf-8")

        moved = self._tool("move", str(plan))

        self.assertEqual(moved.returncode, 0, moved.stdout + moved.stderr)
        self.assertEqual(self.papercuts.read_text(encoding="utf-8"), f"# Papercuts\n\n{SECOND}\n")
        self.assertEqual(
            (self.memory_bank / "papercuts-fixed-2026-09-25.md").read_text(encoding="utf-8"),
            "# Papercuts fixed — 2026-09-25\n\n"
            "## Cause A — 2 occurrences\n\nDisposition: fixed.\n\n"
            f"Evidence: commit abc123 repairs cause A\n\n{FIRST}\n{FOURTH}\n\n"
            "## Cause B — 1 occurrence\n\nDisposition: duplicate.\n\n"
            f"Evidence: Cause A remains the retained repair record\n\n{THIRD}\n",
        )
        checked = self._tool("check", self.base)
        self.assertEqual(checked.returncode, 0, checked.stdout + checked.stderr)

    def test_move_refuses_fixed_claim_without_evidence_before_writing(self) -> None:
        plan = self.root / "unsupported.json"
        plan.write_text(json.dumps({
            "destination": "memory-bank/papercuts-fixed-2026-09-25.md",
            "sections": [{
                "heading": "Unsupported closure",
                "disposition": "fixed",
                "lines": [FIRST],
            }],
        }), encoding="utf-8")
        before = self._snapshot()

        moved = self._tool("move", str(plan))

        self.assertNotEqual(moved.returncode, 0)
        self.assertIn("requires non-empty evidence", moved.stderr)
        self.assertEqual(self._snapshot(), before)

    def test_append_constructs_one_bulleted_entry_and_rejects_multiline_incidents(self) -> None:
        appended = self._tool(
            "append",
            "2026-09-29T14:27:05-07:00",
            "Documentation audit rejected an unbulleted record.",
        )
        self.assertEqual(appended.returncode, 0, appended.stdout + appended.stderr)
        self.assertTrue(
            self.papercuts.read_text(encoding="utf-8").endswith(
                "- 2026-09-29T14:27:05-07:00 — "
                "Documentation audit rejected an unbulleted record.\n"
            )
        )
        before = self._snapshot()

        rejected = self._tool("append", "2026-09-29", "first line\nsecond line")

        self.assertNotEqual(rejected.returncode, 0)
        self.assertIn("single-line", rejected.stderr)
        self.assertEqual(self._snapshot(), before)

    def test_check_fails_when_a_move_drops_a_line_or_leaves_a_copy(self) -> None:
        self.papercuts.write_text(f"# Papercuts\n\n{THIRD}\n{FOURTH}\n", encoding="utf-8")
        (self.memory_bank / "papercuts-fixed-2026-09-25.md").write_text(
            f"# Papercuts fixed — 2026-09-25\n\n## Cause A\n\n{FIRST}\n{THIRD}\n", encoding="utf-8"
        )

        checked = self._tool("check", self.base)

        self.assertEqual(checked.returncode, 1)
        self.assertEqual(
            checked.stdout.splitlines()[:2],
            [f"lost: {SECOND.removeprefix('- ')}", f"open and fixed: {THIRD.removeprefix('- ')}"],
        )

    def test_move_refuses_when_an_open_entry_is_already_in_another_fixed_log(self) -> None:
        (self.memory_bank / "papercuts-fixed-2026-09-24.md").write_text(f"## Older\n\n{SECOND}\n", encoding="utf-8")
        before = self._snapshot()

        moved = self._tool("move", self._plan("2026-09-25", "Cause A", [FIRST]))

        self.assertEqual(moved.returncode, 1)
        self.assertIn(f"open and fixed: {SECOND.removeprefix('- ')}", moved.stdout)
        self.assertEqual(self._snapshot(), before)

    def test_a_plan_whose_entry_was_already_moved_is_refused(self) -> None:
        plan = self._plan("2026-09-25", "Cause A", [FIRST])
        self.assertEqual(self._tool("move", plan).returncode, 0)
        before = self._snapshot()

        moved = self._tool("move", plan)

        self.assertNotEqual(moved.returncode, 0)
        self.assertIn(f"not an open entry of memory-bank/papercuts.md, or chosen twice: {FIRST}", moved.stderr)
        self.assertEqual(self._snapshot(), before)

    def test_move_accepts_a_category_heading_shared_with_the_fixed_log(self) -> None:
        self.papercuts.write_text(f"# Papercuts\n\n## Remote test failures\n\n{FIRST}\n{SECOND}\n", encoding="utf-8")
        (self.memory_bank / "papercuts-fixed-2026-09-25.md").write_text(
            f"# Papercuts fixed — 2026-09-25\n\n## Remote test failures\n\nDisposition: fixed.\n\n{THIRD}\n",
            encoding="utf-8",
        )

        moved = self._tool("move", self._plan("2026-09-25", "Remote test failures", [FIRST]))

        self.assertEqual(moved.returncode, 0, moved.stdout + moved.stderr)
        self.assertEqual(
            self.papercuts.read_text(encoding="utf-8"), f"# Papercuts\n\n## Remote test failures\n\n{SECOND}\n"
        )

    def test_a_failed_write_leaves_both_logs_intact(self) -> None:
        archive = self.memory_bank / "papercuts-fixed-2026-09-25.md"
        archive.write_text(
            "# Papercuts fixed — 2026-09-25\n\n## Older\n\n- 2026-09-19T09:00:00-07:00 — archived\n", encoding="utf-8"
        )
        before = self._snapshot()

        def cap_file_size() -> None:
            # Ignoring SIGXFSZ turns the oversized write into EFBIG instead of killing the tool;
            # the cap sits below the archive's size, so an in-place rewrite would truncate it.
            signal.signal(signal.SIGXFSZ, signal.SIG_IGN)
            resource.setrlimit(resource.RLIMIT_FSIZE, (64, 64))

        moved = self._tool("move", self._plan("2026-09-25", "Cause A", [FIRST, SECOND, THIRD, FOURTH]), preexec_fn=cap_file_size)

        self.assertNotEqual(moved.returncode, 0)
        self.assertIn("File too large", moved.stderr)
        self.assertEqual(self._snapshot(), before)

    def test_a_move_waits_for_one_already_under_way_and_both_lose_nothing(self) -> None:
        tool = [sys.executable, str(ROOT / "tools" / "memory_bank" / "move_papercuts.py"), "--root", str(self.root)]
        # Holding the lock stands in for a first move caught between reading and replacing the logs.
        # Each plan was written before either move ran, so the second one's entry has shifted up a line.
        held = os.open(self.memory_bank, os.O_RDONLY)
        fcntl.flock(held, fcntl.LOCK_EX)
        moves = [
            subprocess.Popen([*tool, "move", self._plan("2026-09-25", heading, [entry], f"{heading}.json")], text=True,
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            for heading, entry in (("Cause A", FIRST), ("Cause B", SECOND))
        ]
        before = self._snapshot()
        try:
            with self.assertRaises(subprocess.TimeoutExpired):
                moves[0].wait(timeout=1)
            self.assertEqual(self._snapshot(), before)
        finally:
            os.close(held)
            outputs = [move.communicate(timeout=30)[0] for move in moves]

        self.assertEqual([move.returncode for move in moves], [0, 0], outputs)
        self.assertEqual(self.papercuts.read_text(encoding="utf-8"), f"# Papercuts\n\n{THIRD}\n{FOURTH}\n")
        checked = self._tool("check", self.base)
        self.assertEqual(checked.returncode, 0, checked.stdout + checked.stderr)


if __name__ == "__main__":
    unittest.main()
