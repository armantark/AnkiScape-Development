import io
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tests.test_promotion_gate import PromotionRepo
from tools import run_remote_tests
from tools.maintenance import retain_evidence
from tools.promotion.lane_execution import _run_bounded
from tools.promotion.snapshot import commit_snapshot
from tools.promotion_gate import GateError, evidence_path_for, run_gate


PROBE = """\
from pathlib import Path
import sys
value = (Path(sys.argv[1]) / 'state.txt').read_text()
print('consumed: ' + value.strip())
raise SystemExit(0 if value == 'passing\\n' else 1)
"""


class CommitSnapshotTest(unittest.TestCase):
    def run_with_transient_edit(self, repo, *, remote_lanes):
        source = repo.target / "state.txt"
        committed = source.read_text(encoding="utf-8")
        self.checked_roots = []

        def execute(command, **options):
            if command[0] == "git":
                return _run_bounded(command, **options)
            if "worktree_guard.py" in command[1]:
                return subprocess.CompletedProcess(command, 0, "layout checked\n", ""), False
            root = command[2] if "run_remote_tests.py" in command[1] else options["worktree"]
            self.checked_roots.append(Path(root))
            source.write_text("passing\n", encoding="utf-8")
            try:
                return _run_bounded((sys.executable, "-c", PROBE, str(root)), **options)
            finally:
                source.write_text(committed, encoding="utf-8")

        # Replace expensive workloads, retaining real gate dispatch, subprocess reads,
        # source restoration, final Git checks and receipt creation.
        with (
            patch("tools.promotion.lane_execution._run_bounded", side_effect=execute),
            patch("tools.promotion.lane_execution._run_reachability_check", return_value=0),
            patch.object(run_remote_tests, "LOCAL_MIRROR_LOCK_PATH", repo.root / "mirror.lock"),
        ):
            return run_gate(
                repo.target, plain_only=False, remote_lanes=remote_lanes, stdout=io.StringIO(),
            )

    def test_transient_live_edit_cannot_certify_a_failing_commit(self):
        for remote_lanes in (False, True):
            with self.subTest(remote_lanes=remote_lanes), tempfile.TemporaryDirectory() as temp:
                repo = PromotionRepo(Path(temp))
                with self.assertRaisesRegex(GateError, r"plain lane \(exit 1\)"):
                    self.run_with_transient_edit(repo, remote_lanes=remote_lanes)
                self.assertFalse(evidence_path_for(repo.target, repo.target_commit).exists())
                self.assertEqual(repo.git(repo.target, "status", "--porcelain").stdout, "")
                self.assertEqual(repo.head(repo.target), repo.target_commit)
                self.assertEqual(len(set(self.checked_roots)), 1)
                self.assertNotEqual(self.checked_roots[0], repo.target)
                self.assertFalse(self.checked_roots[0].exists())

    def passing_repo(self, root):
        repo = PromotionRepo(root)
        (repo.target / "state.txt").write_text("passing\n", encoding="utf-8")
        repo.git(repo.target, "add", "state.txt")
        repo.git(repo.target, "commit", "-qm", "passing fixture")
        repo.target_commit = repo.head(repo.target)
        return repo

    def test_snapshot_pass_writes_receipt_for_original_commit_and_cleans_up(self):
        with tempfile.TemporaryDirectory() as temp:
            repo = self.passing_repo(Path(temp))
            self.run_with_transient_edit(repo, remote_lanes=True)
            self.assertTrue(evidence_path_for(repo.target, repo.target_commit).exists())
            self.assertEqual(len(set(self.checked_roots)), 1)
            self.assertNotEqual(self.checked_roots[0], repo.target)
            self.assertFalse(self.checked_roots[0].exists())

    def test_original_untracked_file_still_refuses_a_passing_snapshot(self):
        with tempfile.TemporaryDirectory() as temp:
            repo = self.passing_repo(Path(temp))
            (repo.target / "untracked.txt").write_text("not committed\n", encoding="utf-8")
            with self.assertRaisesRegex(GateError, r"worktree clean \(exit 1\)"):
                self.run_with_transient_edit(repo, remote_lanes=False)
            self.assertFalse(evidence_path_for(repo.target, repo.target_commit).exists())

    def test_snapshot_ignores_staged_and_untracked_edits(self):
        with tempfile.TemporaryDirectory() as temp:
            repo = PromotionRepo(Path(temp))
            (repo.target / "state.txt").write_text("staged edit\n", encoding="utf-8")
            repo.git(repo.target, "add", "state.txt")
            (repo.target / "untracked.txt").write_text("local only\n", encoding="utf-8")
            with commit_snapshot(repo.target, repo.target_commit) as snapshot:
                self.assertEqual((snapshot / "state.txt").read_text(), "promotion\n")
                self.assertFalse((snapshot / "untracked.txt").exists())
                self.assertEqual(repo.head(snapshot), repo.target_commit)
                self.assertEqual((snapshot / ".venv-qt").resolve(), repo.main / ".venv-qt")
            self.assertFalse(snapshot.exists())
            self.assertEqual(
                repo.git(repo.target, "show", ":state.txt").stdout, "staged edit\n",
            )


class EvidenceRetentionTest(unittest.TestCase):
    def setUp(self):
        self.root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.source_root = self.root / "scratch"
        self.source_root.mkdir()
        self.source = self.source_root / "trace.gz"
        self.source.write_bytes(b"verified trace")
        self.packet = self.root / "packet"
        self.packet.mkdir()
        self.retained = self.packet / "trace.gz"
        self.retained.write_bytes(self.source.read_bytes())
        self.manifest = self.packet / "retention-manifest.json"
        self.manifest.write_text(json.dumps({"files": [{
            "source": str(self.source), "retained": str(self.retained),
            "bytes": self.source.stat().st_size,
            "sha256": hashlib.sha256(self.source.read_bytes()).hexdigest(),
        }]}))

    def test_dry_run_and_compaction_preserve_receipt_paths_and_independent_bytes(self):
        before = self.retained.stat().st_ino
        receipt = self.manifest.read_bytes()
        result = retain_evidence.compact(self.manifest, self.source_root, min_bytes=0)
        self.assertEqual(result["eligible_bytes"], len(b"verified trace"))
        self.assertEqual(self.retained.stat().st_ino, before)
        retain_evidence.compact(self.manifest, self.source_root, min_bytes=0, apply=True)
        self.assertNotEqual(self.retained.stat().st_ino, before)
        self.assertEqual(self.manifest.read_bytes(), receipt)
        self.source.write_bytes(b"private mutation")
        self.assertEqual(self.retained.read_bytes(), b"verified trace")

    def test_compaction_refuses_corruption_symlinks_and_escaping_paths(self):
        row = json.loads(self.manifest.read_text())["files"][0]
        for changed in ({**row, "sha256": "0" * 64},
                        {**row, "source": str(self.retained)},
                        {**row, "retained": str(self.source)}):
            with self.subTest(changed=changed):
                self.manifest.write_text(json.dumps({"files": [changed]}))
                with self.assertRaises((ValueError, RuntimeError)):
                    retain_evidence.compact(self.manifest, self.source_root, min_bytes=0, apply=True)
                self.assertEqual(self.retained.read_bytes(), b"verified trace")
        self.manifest.write_text(json.dumps({"files": [row]}))
        self.source.unlink()
        self.source.symlink_to(self.retained)
        with self.assertRaises(ValueError):
            retain_evidence.compact(self.manifest, self.source_root, min_bytes=0, apply=True)
        self.assertEqual(self.retained.read_bytes(), b"verified trace")

    def test_compaction_detects_a_changed_target_before_replacement(self):
        copy = retain_evidence._copy_file

        def concurrent_edit(source, destination):
            copy(source, destination)
            self.retained.write_bytes(b"concurrent edit")

        with patch.object(retain_evidence, "_copy_file", side_effect=concurrent_edit):
            with self.assertRaisesRegex(RuntimeError, "changed"):
                retain_evidence.compact(self.manifest, self.source_root, min_bytes=0, apply=True)
        self.assertEqual(self.retained.read_bytes(), b"concurrent edit")
        self.assertEqual({p.name for p in self.packet.iterdir()},
                         {"trace.gz", "retention-manifest.json"})

    def test_retention_budget_and_dirty_revision_refuse_before_copying(self):
        destination = self.root / "new-packet"
        with patch.object(retain_evidence, "_git", side_effect=["a" * 40, ""]):
            with self.assertRaisesRegex(ValueError, "budget"):
                retain_evidence.retain(self.root, "a" * 40, destination,
                                       [self.source], max_file_bytes=3)
        self.assertFalse(destination.exists())
        with patch.object(retain_evidence, "_git", side_effect=["a" * 40, " M source"]):
            with self.assertRaisesRegex(ValueError, "dirty"):
                retain_evidence.retain(self.root, "a" * 40, destination, [self.source])
        self.assertFalse(destination.exists())

    def test_retention_refuses_symlinked_inputs_and_destination_before_copying(self):
        alias = self.root / "alias-packet"
        alias.symlink_to(self.packet, target_is_directory=True)
        for source, destination in ((self.source, alias), (alias, self.root / "new-packet")):
            with self.subTest(source=source), \
                    patch.object(retain_evidence, "_git", side_effect=["a" * 40, ""]):
                with self.assertRaisesRegex(ValueError, "symlink"):
                    retain_evidence.retain(self.root, "a" * 40, destination, [source])
        self.assertEqual(self.retained.read_bytes(), b"verified trace")
        self.assertEqual({p.name for p in self.packet.iterdir()},
                         {"trace.gz", "retention-manifest.json"})

    def test_reserved_manifest_name_is_rejected_before_retaining_any_input(self):
        source = self.source_root / "retention-manifest.json"
        source.write_bytes(b"source evidence")
        destination = self.root / "new-packet"
        with patch.object(retain_evidence, "_git", side_effect=["a" * 40, ""]):
            with self.assertRaisesRegex(ValueError, "reserved"):
                retain_evidence.retain(self.root, "a" * 40, destination, [source])
        self.assertFalse(destination.exists())
        self.assertEqual(source.read_bytes(), b"source evidence")

    def test_reused_original_or_hardlink_is_refused_as_retained_evidence(self):
        self.retained.unlink()
        self.retained.hardlink_to(self.source)
        for destination in (self.source_root, self.root / "linked-packet"):
            destination.mkdir(exist_ok=True)
            if destination != self.source_root:
                (destination / self.source.name).hardlink_to(self.source)
            with self.subTest(destination=destination), \
                    patch.object(retain_evidence, "_git", side_effect=["a" * 40, ""]):
                with self.assertRaisesRegex(ValueError, "independent"):
                    retain_evidence.retain(self.root, "a" * 40, destination, [self.source])
            self.assertFalse((destination / "retention-manifest.json").exists())
        self.assertEqual(self.source.read_bytes(), b"verified trace")

    def test_growth_after_budgeting_refuses_copy_and_receipt(self):
        destination = self.root / "new-packet"
        target = destination / self.source.name
        create_target = retain_evidence._retained_target
        planned_size = self.source.stat().st_size

        def concurrent_growth(*arguments):
            result = create_target(*arguments)
            self.source.write_bytes(b"too large for the planned budget")
            return result

        with patch.object(retain_evidence, "_git", side_effect=["a" * 40, ""]), \
                patch.object(retain_evidence, "_retained_target", side_effect=concurrent_growth):
            with self.assertRaisesRegex(RuntimeError, "size changed"):
                retain_evidence.retain(self.root, "a" * 40, destination, [self.source],
                                       max_file_bytes=planned_size, max_packet_bytes=planned_size)
        self.assertFalse(target.exists())
        self.assertFalse((destination / "retention-manifest.json").exists())

    def test_successful_packet_binds_independent_contents_and_exact_sizes(self):
        destination = self.root / "new-packet"
        with patch.object(retain_evidence, "_git", side_effect=["a" * 40, "", "a" * 40, ""]):
            result = retain_evidence.retain(self.root, "a" * 40, destination, [self.source])
        manifest = json.loads(Path(result["manifest"]).read_text())
        row = manifest["files"][0]
        target = Path(row["retained"])
        self.assertEqual(row["bytes"], target.stat().st_size)
        self.assertEqual(row["sha256"], hashlib.sha256(target.read_bytes()).hexdigest())
        self.source.write_bytes(b"private mutation")
        self.assertEqual(target.read_bytes(), b"verified trace")


if __name__ == "__main__":
    unittest.main()
