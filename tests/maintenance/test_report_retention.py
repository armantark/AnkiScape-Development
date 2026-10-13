import io
import json
import os
import tempfile
import unittest
from contextlib import redirect_stdout
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch

from tools.maintenance import report_retention as retention


class ReportRetentionTest(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name).resolve() / "reports"
        self.root.mkdir()
        (self.root / ".retained.json").write_text("[]\n")
        self.now = 1_800_000_000
        self.open_files = retention._open_files
        self.enterContext(patch.object(retention, "_open_files", return_value=set()))

    def group(self, number, *, age=1, report="0\n", size=8):
        name = f"qt-{self.now - age * 86400}-{number:08x}"
        for suffix, contents in (("log", "x" * size), ("report", report), ("pid", "1234\n")):
            path = self.root / f"{name}.{suffix}"
            path.write_text(contents)
            os.utime(path, (self.now - age * 86400,) * 2)
        return name

    def plan(self, **options):
        return retention.plan_retention(self.root, now=self.now, **options)

    def test_old_success_expires_but_failures_unresolved_and_unknown_survive(self):
        old = self.group(1, age=8)
        failed = self.group(2, age=9, report="1\n")
        unresolved = self.group(3, age=10)
        (self.root / f"{unresolved}.report").unlink()
        malformed = self.group(4, age=11, report="not a result\n")
        unknown = self.group(5, age=12)
        (self.root / f"{unknown}.report.tmp").write_text("0\n")
        (self.root / "owner.log").write_text("unknown retained")
        before = set(self.root.iterdir())
        plan = self.plan()
        self.assertEqual([group.run_id for group in plan.remove], [old])
        self.assertEqual(set(plan.protected), {failed, unresolved, malformed, unknown})
        self.assertEqual(set(self.root.iterdir()), before)
        retention.apply_retention(plan)
        self.assertFalse((self.root / f"{old}.log").exists())
        self.assertTrue(all((self.root / f"{name}.log").exists()
                            for name in (failed, unresolved, malformed, unknown)))
        self.assertEqual((self.root / "owner.log").read_text(), "unknown retained")

    def test_count_and_bytes_keep_newest_success_groups_deterministically(self):
        newest = self.group(1, age=1, size=20)
        middle = self.group(2, age=2, size=20)
        oldest = self.group(3, age=3, size=20)
        count_plan = self.plan(max_groups=2)
        self.assertEqual(count_plan.kept, (newest, middle))
        self.assertEqual([group.run_id for group in count_plan.remove], [oldest])
        byte_plan = self.plan(max_bytes=27)
        self.assertEqual(byte_plan.kept, (newest,))
        self.assertEqual([group.run_id for group in byte_plan.remove], [middle, oldest])
        self.assertEqual(self.plan(max_bytes=27), byte_plan)

    def test_default_count_and_byte_bounds_use_real_group_metadata(self):
        names = [self.group(number) for number in range(1, 130)]
        count_plan = self.plan()
        self.assertEqual(count_plan.kept, tuple(names[:128]))
        self.assertEqual([group.run_id for group in count_plan.remove], names[128:])
        newest = self.group(0, age=0)
        with (self.root / f"{newest}.log").open("r+b") as stream:
            stream.truncate(64 * 1024 * 1024 - 7)
        os.utime(self.root / f"{newest}.log", (self.now,) * 2)
        byte_plan = self.plan()
        self.assertEqual(byte_plan.kept, (newest,))
        self.assertEqual({group.run_id for group in byte_plan.remove}, set(names))

    def test_pins_open_readers_and_symlinks_protect_the_whole_group(self):
        pinned = self.group(1, age=8)
        opened = self.group(2, age=9)
        linked = self.group(3, age=10)
        (self.root / ".retained.json").write_text(json.dumps([pinned]))
        sentinel = self.root.parent / "owner-sentinel"
        sentinel.write_bytes(b"do not touch")
        (self.root / f"{linked}.log").unlink()
        (self.root / f"{linked}.log").symlink_to(sentinel)
        with patch.object(retention, "_open_files", return_value={self.root / f"{opened}.log"}):
            plan = self.plan(max_groups=0, max_bytes=0)
        self.assertEqual(plan.remove, ())
        self.assertEqual(set(plan.protected), {pinned, opened, linked})
        retention.apply_retention(plan)
        self.assertEqual(sentinel.read_bytes(), b"do not touch")

    def test_missing_bad_or_linked_pins_refuse_and_leave_all_reports(self):
        old = self.group(1, age=9)
        pins = self.root / ".retained.json"
        for contents in (None, "{broken", "{}", '["not-a-run"]'):
            with self.subTest(contents=contents):
                if pins.exists():
                    pins.unlink()
                if contents is not None:
                    pins.write_text(contents)
                with self.assertRaises((OSError, ValueError)):
                    self.plan()
                self.assertTrue((self.root / f"{old}.log").exists())
        pins.unlink()
        target = self.root.parent / "pins.json"
        target.write_text("[]")
        pins.symlink_to(target)
        with self.assertRaises(ValueError):
            self.plan()

    def test_apply_rechecks_files_pins_and_open_files_before_any_group_unlink(self):
        old = self.group(1, age=9)
        plan = self.plan()
        (self.root / f"{old}.pid").write_text("different pid\n")
        with self.assertRaises(RuntimeError):
            retention.apply_retention(plan)
        self.assertTrue((self.root / f"{old}.log").exists())
        plan = self.plan()
        (self.root / ".retained.json").write_text(json.dumps([old]))
        with self.assertRaises(RuntimeError):
            retention.apply_retention(plan)
        self.assertTrue((self.root / f"{old}.log").exists())
        (self.root / ".retained.json").write_text("[]")
        (self.root / f"{old}.pid").write_text("1234\n")
        os.utime(self.root / f"{old}.pid", (self.now - 9 * 86400,) * 2)
        plan = self.plan()
        with patch.object(retention, "_open_files", return_value={self.root / f"{old}.report"}):
            with self.assertRaises(RuntimeError):
                retention.apply_retention(plan)
        self.assertTrue((self.root / f"{old}.log").exists())

    def test_bad_root_and_symlink_ancestor_refuse(self):
        alias = self.root.parent / "alias"
        alias.symlink_to(self.root.parent, target_is_directory=True)
        for root in (Path("/"), Path.home(), alias / "reports", self.root.parent):
            with self.subTest(root=root), self.assertRaises(ValueError):
                retention.plan_retention(root, now=self.now)

    def test_new_unknown_member_or_replaced_root_vetoes_a_planned_unlink(self):
        old = self.group(1, age=9)
        plan = self.plan()
        (self.root / f"{old}.receipt").write_text("unrecognized evidence")
        with self.assertRaises(RuntimeError):
            retention.apply_retention(plan)
        self.assertTrue((self.root / f"{old}.log").exists())
        (self.root / f"{old}.receipt").unlink()
        plan = self.plan()
        preserved = self.root.rename(self.root.with_name("preserved-reports"))
        self.root.mkdir()
        (self.root / ".retained.json").write_text("[]")
        with self.assertRaises(RuntimeError):
            retention.apply_retention(plan)
        self.assertTrue((preserved / f"{old}.log").exists())

    def test_live_reader_vetoes_success_even_after_completion(self):
        old = self.group(1, age=9)
        source = self.root / f"{old}.log"
        alias = self.root.parent / "reader-alias.log"
        alias.symlink_to(source)
        for reader in (source, alias):
            with self.subTest(reader=reader), reader.open(), \
                    patch.object(retention, "_open_files", wraps=self.open_files):
                plan = self.plan(max_groups=0, max_bytes=0)
            self.assertEqual(plan.remove, ())
            self.assertIn(old, plan.protected)
        self.assertTrue((self.root / f"{old}.log").exists())

    def test_apply_refuses_a_member_outside_the_admitted_root(self):
        self.group(1, age=9)
        plan = self.plan()
        outside = self.root.parent / "owner.log"
        outside.write_text("owner unchanged")
        group = replace(plan.remove[0], files=((outside, retention._identity(outside)),))
        with self.assertRaises(ValueError):
            retention.apply_retention(replace(plan, remove=(group,)))
        self.assertEqual(outside.read_text(), "owner unchanged")

    def test_cli_defaults_to_dry_run_and_requires_explicit_apply(self):
        old = self.group(1, age=9)
        with patch.object(retention.time, "time", return_value=self.now), \
                redirect_stdout(io.StringIO()) as output:
            self.assertEqual(retention.main([str(self.root)]), 0)
            self.assertTrue((self.root / f"{old}.log").exists())
            dry = json.loads(output.getvalue())
            self.assertFalse(dry["applied"])
            self.assertEqual(dry["remove_groups"], 1)
            self.assertEqual(dry["remove_files"], 3)
            self.assertEqual(dry["remove_bytes"], 15)
            self.assertNotIn(old, output.getvalue())
        with patch.object(retention.time, "time", return_value=self.now), \
                redirect_stdout(io.StringIO()):
            self.assertEqual(retention.main([str(self.root), "--apply"]), 0)
        self.assertFalse((self.root / f"{old}.log").exists())

    def test_lsof_failure_refuses_and_reader_paths_are_reported(self):
        self.group(1, age=9)
        self._open_patch = self.enterContext(patch.object(retention.subprocess, "run"))
        self._open_patch.return_value.returncode = 0
        self._open_patch.return_value.stderr = ""
        witnesses = f"p123\nn{self.root}\nn{self.root}/reader.log\nn{self.root}/.retained.json\n"
        self._open_patch.return_value.stdout = witnesses
        self.assertEqual(self.open_files(self.root),
                         {self.root, self.root / "reader.log", self.root / ".retained.json"})
        for returncode, stderr, stdout in (
            (1, "", witnesses),
            (0, "", witnesses.replace(f"n{self.root}\n", "")),
            (0, "", witnesses.replace(f"n{self.root}/.retained.json\n", "")),
            (0, "partial scan", witnesses),
        ):
            with self.subTest(returncode=returncode, stderr=stderr, stdout=stdout):
                self._open_patch.return_value.returncode = returncode
                self._open_patch.return_value.stderr = stderr
                self._open_patch.return_value.stdout = stdout
                with self.assertRaises(RuntimeError) as failure:
                    self.open_files(self.root)
                self.assertIn(f"returncode={returncode}", str(failure.exception))
                self.assertIn("missing_witnesses=", str(failure.exception))
                if f"n{self.root}\n" not in stdout:
                    self.assertIn(str(self.root), str(failure.exception))
        self._open_patch.return_value.returncode = 1
        self._open_patch.return_value.stderr = "lsof: denied"
        with self.assertRaises(RuntimeError):
            self.open_files(self.root)
