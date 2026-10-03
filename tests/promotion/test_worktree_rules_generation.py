import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import Mock, patch

from tools import worktree_guard


class WorktreeRulesGenerationTest(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name).resolve()
        self.canonical = self.root / "Anki2/addons21/ankiscape_fork"
        interpreter = self.canonical / ".venv-qt/bin/python"
        interpreter.parent.mkdir(parents=True)
        interpreter.touch()
        subprocess.run(
            ("git", "init", "-q", str(self.canonical)), check=True, capture_output=True,
        )
        self.bin = self.root / "bin"
        self.bin.mkdir()
        self.stub = self.bin / "rulesync"
        self.stub.write_text(
            f"#!{sys.executable}\n"
            "import argparse, json\n"
            "from pathlib import Path\n"
            "parser = argparse.ArgumentParser()\n"
            "parser.add_argument('--json', action='store_true')\n"
            "parser.add_argument('command', choices=['generate'])\n"
            "parser.add_argument('--config', required=True)\n"
            "parser.add_argument('--features', choices=['rules'], required=True)\n"
            "parser.add_argument('--dry-run', action='store_true')\n"
            "parser.add_argument('--output-roots')\n"
            "parser.add_argument('--input-root')\n"
            "args = parser.parse_args()\n"
            "config = json.loads(Path(args.config).read_text())\n"
            "local = Path('rulesync.local.jsonc')\n"
            "if local.exists():\n"
            "    config.update(json.loads(local.read_text()))\n"
            "outputs = {'codexcli': 'AGENTS.md', 'claudecode': 'CLAUDE.md'}\n"
            "files = {outputs[target]: Path('.rulesync/rules/example.md').read_text() for target in config['targets']}\n"
            "for source in Path('.rulesync/rules').glob('sidecar*.md'):\n"
            "    files['.claude/rules/' + source.name] = source.read_text()\n"
            "root = Path(args.output_roots or config.get('outputRoots', ['.'])[0])\n"
            "paths = [str(root / name) for name in files]\n"
            "if not args.dry_run:\n"
            "    for name, content in files.items():\n"
            "        path = root / name\n"
            "        path.parent.mkdir(parents=True, exist_ok=True)\n"
            "        path.write_text(content)\n"
            "print(json.dumps({'data': {'features': {'rules': {'paths': paths}}}}))\n",
            encoding="utf-8",
        )
        self.stub.chmod(0o755)

    def destination(self, operation):
        root = worktree_guard.safe_worktree_root(self.canonical)
        return root / ("feature" if operation == "add" else "pool/feature")

    def prepare_sources(self, destination):
        rules = destination / ".rulesync/rules"
        rules.mkdir(parents=True)
        (rules / "example.md").write_text("Rules from the destination tree.\n", encoding="utf-8")
        (destination / "rulesync.jsonc").write_text(
            json.dumps({"targets": ["codexcli", "claudecode"]}), encoding="utf-8",
        )
        (destination / "AGENTS.md").write_text("Stale pooled rules.\n", encoding="utf-8")

    def invoke(self, operation, *, tracked=()):
        destination = self.destination(operation)

        def fake_git(_repo, *args, **_kwargs):
            if args[:2] == ("worktree", "add"):
                destination.mkdir(parents=True, exist_ok=True)
            if args[:2] == ("worktree", "remove"):
                shutil.rmtree(destination)
            return Mock(returncode=1, stdout="\0".join(tracked) if args[0] == "ls-files" else "")

        def fake_treehouse(_repo, *args):
            if args[0] == "get":
                destination.mkdir(parents=True, exist_ok=True)
            return Mock(stdout=json.dumps({"path": str(destination), "lease_id": "lease-1"}))

        with (
            patch("tools.worktree_guard.audit"),
            patch("tools.worktree_guard.canonical_and_paths", return_value=(self.canonical, (self.canonical,))),
            patch("tools.worktree_guard._git", side_effect=fake_git) as git,
            patch("tools.worktree_guard._treehouse", side_effect=fake_treehouse) as treehouse,
            patch.dict(os.environ, {"PATH": str(self.bin)}),
            redirect_stdout(io.StringIO()),
        ):
            self.git, self.treehouse = git, treehouse
            if operation == "add":
                worktree_guard.add_worktree(self.canonical, "feature", None, "main")
            else:
                worktree_guard.lease_worktree(self.canonical, "feature", None, "main")
        return git, treehouse

    def test_add_and_lease_generate_from_destination_sources(self):
        for operation in ("add", "lease"):
            with self.subTest(operation=operation):
                destination = self.destination(operation)
                self.prepare_sources(destination)
                self.invoke(operation)
                for filename in ("CLAUDE.md", "AGENTS.md"):
                    self.assertEqual(
                        (destination / filename).read_text(encoding="utf-8"),
                        "Rules from the destination tree.\n",
                    )

    def test_missing_rulesync_refuses_add_and_lease_with_config(self):
        self.stub.unlink()
        for operation in ("add", "lease"):
            with self.subTest(operation=operation):
                destination = self.destination(operation)
                self.prepare_sources(destination)
                with self.assertRaisesRegex(RuntimeError, "rulesync.*not found"):
                    self.invoke(operation)
                self.assertFalse((destination / "CLAUDE.md").exists())
                if operation == "lease":
                    self.assertEqual(
                        self.treehouse.call_args.args[1:],
                        ("return", "--force", "--if-lease-id", "lease-1", str(destination)),
                    )

    def test_add_and_lease_skip_generation_without_config(self):
        self.stub.unlink()
        for operation in ("add", "lease"):
            with self.subTest(operation=operation):
                self.invoke(operation)
                destination = self.destination(operation)
                self.assertTrue((destination / ".venv-qt").is_symlink())
                for filename in ("CLAUDE.md", "AGENTS.md"):
                    self.assertFalse((destination / filename).exists())

    def test_failed_rulesync_refuses_add_and_lease(self):
        self.stub.write_text(
            f"#!{sys.executable}\n"
            "import sys\n"
            "sys.stderr.write('source generation failed\\n')\n"
            "sys.exit(7)\n",
            encoding="utf-8",
        )
        for operation in ("add", "lease"):
            with self.subTest(operation=operation):
                self.prepare_sources(self.destination(operation))
                with self.assertRaisesRegex(RuntimeError, "(?s)rulesync.*source generation failed"):
                    self.invoke(operation)

    def test_local_override_cannot_overwrite_external_file(self):
        destination = self.destination("lease")
        self.prepare_sources(destination)
        sentinel = self.root / "AGENTS.md"
        sentinel.write_text("External rules stay.\n", encoding="utf-8")
        (destination / "rulesync.local.jsonc").write_text(
            json.dumps({"outputRoots": [str(self.root)]}), encoding="utf-8",
        )
        with self.assertRaisesRegex(RuntimeError, "rulesync.local.jsonc"):
            self.invoke("lease")
        self.assertEqual(sentinel.read_text(), "External rules stay.\n")

    def test_output_and_parent_symlinks_cannot_overwrite_external_file(self):
        for linked_parent in (False, True):
            with self.subTest(linked_parent=linked_parent), tempfile.TemporaryDirectory() as temporary:
                destination = Path(temporary) / "destination"
                self.prepare_sources(destination)
                sentinel = Path(temporary) / "sidecar.md"
                sentinel.write_text("External rules stay.\n", encoding="utf-8")
                (destination / ".rulesync/rules/sidecar.md").write_text("New rules.\n")
                if linked_parent:
                    (destination / ".claude").symlink_to(Path(temporary), target_is_directory=True)
                    (Path(temporary) / "rules").mkdir()
                    (Path(temporary) / "rules/sidecar.md").symlink_to(sentinel)
                else:
                    (destination / ".claude/rules").mkdir(parents=True)
                    (destination / ".claude/rules/sidecar.md").symlink_to(sentinel)
                with patch.dict(os.environ, {"PATH": str(self.bin)}):
                    with self.assertRaisesRegex(RuntimeError, "outside.*destination"):
                        worktree_guard.generate_worktree_rules(destination)
                self.assertEqual(sentinel.read_text(), "External rules stay.\n")
                self.assertEqual((destination / "AGENTS.md").read_text(), "Stale pooled rules.\n")

    def test_config_output_root_cannot_overwrite_external_file(self):
        destination = self.destination("lease")
        self.prepare_sources(destination)
        sentinel = self.root / "AGENTS.md"
        sentinel.write_text("External rules stay.\n", encoding="utf-8")
        (destination / "rulesync.jsonc").write_text(json.dumps({
            "targets": ["codexcli", "claudecode"], "outputRoots": [str(self.root)],
        }))
        with self.assertRaisesRegex(RuntimeError, "outside.*destination"):
            self.invoke("lease")
        self.assertEqual(sentinel.read_text(), "External rules stay.\n")

    def test_timeout_during_lease_returns_the_lease(self):
        self.prepare_sources(self.destination("lease"))
        self.stub.write_text(f"#!{sys.executable}\nimport time\ntime.sleep(30)\n")
        with patch.object(worktree_guard, "RULESYNC_TIMEOUT_SECONDS", 0.05, create=True):
            with self.assertRaisesRegex(RuntimeError, "rulesync.*timed out"):
                self.invoke("lease")
        self.assertEqual(self.treehouse.call_args.args[1:], (
            "return", "--force", "--if-lease-id", "lease-1", str(self.destination("lease")),
        ))

    def test_failed_add_removes_destination_so_retry_succeeds(self):
        destination = self.destination("add")
        self.prepare_sources(destination)
        original = self.stub.read_text()
        self.stub.write_text(f"#!{sys.executable}\nraise SystemExit(7)\n")
        with self.assertRaisesRegex(RuntimeError, "rulesync generation failed"):
            self.invoke("add")
        self.assertFalse(destination.exists())
        self.assertEqual(self.git.call_args.args[1:], ("worktree", "remove", "--force", str(destination)))
        self.stub.write_text(original)
        self.prepare_sources(destination)
        self.invoke("add")
        self.assertEqual((destination / "CLAUDE.md").read_text(), "Rules from the destination tree.\n")

    def test_reused_lease_removes_only_obsolete_managed_untracked_rules(self):
        destination = self.destination("lease")
        self.prepare_sources(destination)
        sources = destination / ".rulesync/rules"
        for name in ("sidecar-old.md", "sidecar-tracked.md", "sidecar-current.md"):
            (sources / name).write_text(name + "\n")
        self.invoke("lease")
        outputs = destination / ".claude/rules"
        (outputs / "manual.md").write_text("Keep manual rule.\n")
        (sources / "sidecar-old.md").unlink()
        (sources / "sidecar-tracked.md").unlink()
        self.invoke("lease", tracked=(".claude/rules/sidecar-tracked.md",))
        self.assertFalse((outputs / "sidecar-old.md").exists())
        self.assertEqual((outputs / "sidecar-tracked.md").read_text(), "sidecar-tracked.md\n")
        self.assertEqual((outputs / "sidecar-current.md").read_text(), "sidecar-current.md\n")
        self.assertEqual((outputs / "manual.md").read_text(), "Keep manual rule.\n")

    def test_obsolete_output_symlink_refuses_cleanup_before_any_write(self):
        destination = self.destination("lease")
        self.prepare_sources(destination)
        source = destination / ".rulesync/rules/sidecar-old.md"
        source.write_text("Old rule.\n")
        self.invoke("lease")
        source.unlink()
        sentinel = self.root / "sentinel.md"
        sentinel.write_text("External rules stay.\n")
        output = destination / ".claude/rules/sidecar-old.md"
        output.unlink()
        output.symlink_to(sentinel)
        (destination / "AGENTS.md").write_text("No writes before containment.\n")
        with self.assertRaisesRegex(RuntimeError, "outside.*destination"):
            self.invoke("lease")
        self.assertTrue(output.is_symlink())
        self.assertEqual(sentinel.read_text(), "External rules stay.\n")
        self.assertEqual((destination / "AGENTS.md").read_text(), "No writes before containment.\n")

    def test_external_parent_refused_when_output_symlink_points_back_inside(self):
        destination = self.destination("lease")
        self.prepare_sources(destination)
        (destination / ".rulesync/rules/sidecar.md").write_text("New rules.\n")
        external = self.root / "external"
        external.mkdir()
        owned = destination / "owned-rules"
        owned.mkdir()
        (external / "rules").symlink_to(owned, target_is_directory=True)
        (destination / ".claude").symlink_to(external, target_is_directory=True)
        target = owned / "sidecar.md"
        target.write_text("No write through an external parent.\n")
        with self.assertRaisesRegex(RuntimeError, "outside.*destination"):
            self.invoke("lease")
        self.assertEqual(target.read_text(), "No write through an external parent.\n")

    def test_internal_symlink_refuses_pruning_before_any_delete_or_write(self):
        for linked in (".claude", ".claude/rules", ".claude/rules/sidecar-old.md"):
            with self.subTest(linked=linked), tempfile.TemporaryDirectory() as temporary:
                destination = Path(temporary).resolve() / "destination"
                self.prepare_sources(destination)
                sources = destination / ".rulesync/rules"
                for name in ("sidecar-old.md", "sidecar-other.md"):
                    (sources / name).write_text(name + "\n")
                with patch.dict(os.environ, {"PATH": str(self.bin)}), patch(
                    "tools.worktree_guard._git", return_value=Mock(stdout=""),
                ):
                    worktree_guard.generate_worktree_rules(destination)
                outputs = destination / ".claude/rules"
                for source in sources.glob("sidecar*.md"):
                    source.unlink()
                link = destination / linked
                owned = destination / "owned-rules"
                link.rename(owned)
                link.symlink_to(owned, target_is_directory=owned.is_dir())
                subprocess.run(("git", "init", "-q", str(destination)), check=True, capture_output=True)
                subprocess.run(("git", "-C", str(destination), "add", "owned-rules"), check=True, capture_output=True)
                (destination / "AGENTS.md").write_text("No publication before safety checks.\n")
                with patch.dict(os.environ, {"PATH": str(self.bin) + os.pathsep + os.environ["PATH"]}):
                    with self.assertRaisesRegex(RuntimeError, "symlink"):
                        worktree_guard.generate_worktree_rules(destination)
                self.assertEqual((outputs / "sidecar-old.md").read_text(), "sidecar-old.md\n")
                self.assertEqual((outputs / "sidecar-other.md").read_text(), "sidecar-other.md\n")
                self.assertEqual((destination / "AGENTS.md").read_text(), "No publication before safety checks.\n")

    def test_manifest_filename_without_matching_generated_bytes_is_not_owned(self):
        relative = ".claude/rules/manual.md"
        for manifest in ([relative], {relative: None}, {relative: "0" * 64}):
            with self.subTest(manifest=manifest), tempfile.TemporaryDirectory() as temporary:
                destination = Path(temporary).resolve() / "destination"
                self.prepare_sources(destination)
                manual = destination / relative
                manual.parent.mkdir(parents=True)
                manual.write_text("Keep a rule Rulesync never generated.\n")
                (destination / worktree_guard.RULE_OUTPUT_MANIFEST).write_text(json.dumps(manifest))
                with patch.dict(os.environ, {"PATH": str(self.bin)}), patch(
                    "tools.worktree_guard._git", return_value=Mock(stdout=""),
                ):
                    worktree_guard.generate_worktree_rules(destination)
                self.assertEqual(manual.read_text(), "Keep a rule Rulesync never generated.\n")
                self.assertEqual((destination / "AGENTS.md").read_text(), "Rules from the destination tree.\n")

    def test_edited_generated_rule_survives_when_source_is_removed(self):
        destination = self.destination("lease")
        self.prepare_sources(destination)
        source = destination / ".rulesync/rules/sidecar-old.md"
        source.write_text("Generated rule.\n")
        self.invoke("lease")
        source.unlink()
        output = destination / ".claude/rules/sidecar-old.md"
        output.write_text("Keep the edited rule.\n")
        self.invoke("lease")
        self.assertEqual(output.read_text(), "Keep the edited rule.\n")
