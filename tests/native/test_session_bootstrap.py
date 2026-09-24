import hashlib
import io
import json
import os
import plistlib
import shlex
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import Mock, patch

from tools.native import session_guard as native


def fixture_environment():
    return {key: value for key, value in os.environ.items()
            if not key.startswith("ANKI_")
            and key not in {"BRIEFCASE_MAIN_MODULE", "PYTHONHOME", "PYTHONPATH"}}


def make_anki_fixture(app):
    modules = app / "Contents/Resources/app"
    modules.mkdir(parents=True)
    executable = app / "Contents/MacOS/Anki"
    executable.parent.mkdir()
    executable.write_text(
        f"#!{sys.executable}\n"
        "import os, pathlib, plistlib, runpy, sys\n"
        "contents = pathlib.Path(__file__).resolve().parents[1]\n"
        "sys.path.insert(0, str(contents / 'Resources/app'))\n"
        "with (contents / 'Info.plist').open('rb') as stream:\n"
        "    info = plistlib.load(stream)\n"
        "main = os.environ.get('BRIEFCASE_MAIN_MODULE', info['MainModule'])\n"
        "if main == 'ankiscape_native_bootstrap':\n"
        "    import ankiscape_session_guard as guard\n"
        # This Python fixture has no Anki process identity; process checks have unit coverage.
        "    guard.require_anki_stopped = lambda **kwargs: None\n"
        "runpy._run_module_as_main(main, alter_argv=False)\n"
    )
    executable.chmod(0o755)
    (modules / "anki.py").write_text(
        "import json, pathlib, sys\n"
        "base = pathlib.Path(__file__).resolve().parents[4]\n"
        "with (base / 'runtime-invocations.jsonl').open('a') as output:\n"
        "    output.write(json.dumps({'argv': sys.argv,\n"
        "        'main_is_runtime': sys.modules['__main__'].__dict__ is globals(),\n"
        "        'main_spec': sys.modules['__main__'].__spec__.name}) + '\\n')\n"
    )
    (app / "Contents/Info.plist").write_bytes(plistlib.dumps({
        "CFBundleExecutable": "Anki", "CFBundleIdentifier": "net.ankiweb.dtop",
        "CFBundleName": "Anki", "MainModule": "anki",
    }))


class NativeBootstrapTest(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name).resolve()
        self.repo = self.root / "repo"
        self.repo.mkdir()
        (self.repo / "__init__.py").write_text("ADDON = True\n")
        self.collection = self.root / "owner/collection.anki2"
        self.collection.parent.mkdir()
        self.collection.write_bytes(b"owner sentinel")
        self.app = self.root / "Anki.app"
        make_anki_fixture(self.app)
        self.environment = fixture_environment()

    def prepare(self):
        with patch.object(native, "ANKI_APP", self.app), \
                patch.object(native, "owner_collection", return_value=self.collection), \
                patch.object(native.tempfile, "tempdir", str(self.root)), \
                patch.object(native.subprocess, "run", return_value=Mock(returncode=1)), \
                patch.dict(os.environ, self.environment, clear=True), \
                redirect_stdout(io.StringIO()) as output:
            base = native.prepare(self.repo)
        return base, json.loads(output.getvalue())

    def test_argument_free_app_launch_and_reopen_use_bound_base(self):
        base, report = self.prepare()
        app = Path(report["app_path"])
        executable = app / "Contents/MacOS/Anki"
        another_temp = self.root / "launchservices-temp"
        another_temp.mkdir()
        environments = (self.environment, {**self.environment, "TMPDIR": str(another_temp)})
        for environment in environments:
            result = subprocess.run([str(executable)], env=environment,
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
        invocations = [json.loads(line) for line in
                       (base / "runtime-invocations.jsonl").read_text().splitlines()]
        self.assertEqual(len(invocations), 2)
        for invocation in invocations:
            self.assertEqual(invocation["argv"][1:], ["-b", str(base)])
            self.assertTrue(invocation["main_is_runtime"])
            self.assertEqual(invocation["main_spec"], "anki")
        self.assertEqual(self.collection.read_bytes(), b"owner sentinel")

    def assert_blocked(self, base, *, arguments=(), environment=None, exit_code=2):
        result = subprocess.run(
            [str(base / native.TEST_APP / "Contents/MacOS/Anki"), *arguments],
            env=environment or self.environment, capture_output=True, text=True,
        )
        self.assertNotEqual(result.returncode, 0, result.stderr)
        if exit_code is not None:
            self.assertEqual(result.returncode, exit_code, result.stderr)
            self.assertIn("error: ", result.stderr)
        self.assertFalse((base / "runtime-invocations.jsonl").exists(), result.stdout)
        self.assertEqual(self.collection.read_bytes(), b"owner sentinel")

    def test_external_arguments_never_reach_runtime(self):
        base, _ = self.prepare()
        for arguments in (("-b", str(self.collection.parent)),
                          ("--base=" + str(self.collection.parent),),
                          ("--profile", "User 1"), ("deck.apkg",),
                          ("-b", str(base), "-b", str(self.collection.parent))):
            with self.subTest(arguments=arguments):
                self.assert_blocked(base, arguments=arguments)

    def test_environment_overrides_cannot_bypass_bound_startup(self):
        base, _ = self.prepare()
        for key, value in (("ANKI_BASE", str(self.collection.parent)),
                           ("ANKI_SINGLE_INSTANCE_KEY", "owner"),
                           ("BRIEFCASE_MAIN_MODULE", "anki"),
                           ("PYTHONPATH", str(self.root))):
            with self.subTest(key=key):
                self.assert_blocked(base, environment={**self.environment, key: value})

    def test_receipt_loss_corruption_or_tampering_stops_before_runtime(self):
        base, _ = self.prepare()
        receipt = base / native.RECEIPT
        original = receipt.read_text()
        for contents in (None, "{broken", original.replace('"exists": true', '"exists": false')):
            with self.subTest(contents=contents):
                if contents is None:
                    receipt.unlink()
                else:
                    receipt.write_text(contents)
                self.assert_blocked(base)
        receipt.write_text(original)

    def test_profile_or_addon_symlinks_cannot_escape_base(self):
        for name in ("User 1", "addons21/other_addon", "User 1/collection.anki2"):
            with self.subTest(name=name):
                base, _ = self.prepare()
                path = base / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.symlink_to(self.collection.parent)
                self.assert_blocked(base)

    def test_changed_or_missing_addon_stops_before_runtime(self):
        base, _ = self.prepare()
        source = base / "addons21/ankiscape_fork/__init__.py"
        source.write_text("CHANGED = True\n")
        self.assert_blocked(base)
        source.unlink()
        self.assert_blocked(base)

    def test_relocated_bundle_stops_before_runtime(self):
        base, _ = self.prepare()
        moved = base.rename(base.with_name("ankiscape-native-moved"))
        self.assert_blocked(moved, exit_code=None)

    def test_runtime_generated_metadata_does_not_change_source_identity(self):
        base, _ = self.prepare()
        addon = base / "addons21/ankiscape_fork"
        before = native.source_digest(addon)
        (addon / "meta.json").write_text('{"config": {}}')
        (addon / "user_files").mkdir()
        (addon / "user_files/profile.json").write_text("{}")
        self.assertEqual(native.source_digest(addon), before)


class NativeSessionGuardTest(unittest.TestCase):
    def setUp(self):
        self.enterContext(patch.dict(os.environ, fixture_environment(), clear=True))
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name).resolve()
        self.repo = self.root / "repo"
        self.repo.mkdir()
        (self.repo / "__init__.py").write_text("ADDON = True\n", encoding="utf-8")
        self.collection = self.root / "owner/collection.anki2"
        self.collection.parent.mkdir()
        self.collection.write_bytes(b"original collection")
        self.enterContext(patch.object(native, "owner_collection", return_value=self.collection))
        self.process = self.enterContext(patch.object(
            native.subprocess, "run", return_value=Mock(returncode=1, stdout="", stderr=""),
        ))
        self.enterContext(patch.object(native.tempfile, "tempdir", str(self.root)))
        app = self.root / "Anki.app"
        make_anki_fixture(app)
        self.enterContext(patch.object(native, "ANKI_APP", app))

    def prepare_session(self):
        with redirect_stdout(io.StringIO()) as output:
            base = native.prepare(self.repo)
        return base, json.loads(output.getvalue())

    def test_prepare_copies_addon_and_records_collection_without_modifying_it(self):
        before = native.measure(self.collection)
        base, output = self.prepare_session()
        copied = base / "addons21/ankiscape_fork/__init__.py"
        self.assertEqual(copied.read_bytes(), b"ADDON = True\n")
        self.assertFalse(copied.is_symlink())
        receipt = json.loads((base / native.RECEIPT).read_text())
        self.assertEqual(receipt["baseline"], before)
        self.assertEqual(native.measure(self.collection), before)
        self.assertEqual(output["path"], str(base))
        self.assertEqual(shlex.split(output["anki_command"]), [
            str(base / native.TEST_APP / "Contents/MacOS/Anki"),
        ])
        self.assertIn(" launch ", output["launch_command"])
        self.assertEqual(shlex.split(output["launch_command"]), [
            sys.executable, str(Path(native.__file__).resolve()), "launch", str(base),
        ])
        with patch.object(native, "prepare") as prepare:
            self.assertEqual(native.main(["prepare"]), 0)
        prepare.assert_called_once_with(Path(__file__).resolve().parents[2])

    def test_prepare_refuses_running_anki_before_creating_a_session(self):
        self.process.return_value = Mock(returncode=0, stdout="123\n", stderr="")
        before = native.measure(self.collection)
        with self.assertRaisesRegex(RuntimeError, "Anki is already running"):
            native.prepare(self.repo)
        self.assertEqual(list(self.root.glob("ankiscape-native-*")), [])
        self.assertEqual(native.measure(self.collection), before)
        self.process.assert_called_once_with(
            ("/usr/bin/pgrep", "-ix", "anki|anki-runtime"), text=True, capture_output=True,
        )

    def test_verify_detects_modified_collection_and_preserves_evidence(self):
        base, _ = self.prepare_session()
        with redirect_stdout(io.StringIO()) as output:
            self.assertEqual(native.main(["verify", str(base)]), 0)
        self.assertTrue(json.loads(output.getvalue())["unchanged"])
        self.collection.write_bytes(b"modified collection with more data")
        with redirect_stdout(io.StringIO()) as output:
            self.assertEqual(native.main(["verify", str(base)]), 1)
        report = json.loads(output.getvalue())
        self.assertFalse(report["unchanged"])
        self.assertIn("sha256", report["changes"])
        self.assertIn("size", report["changes"])
        self.assertTrue((base / native.RECEIPT).is_file())
        self.assertTrue((base / "addons21/ankiscape_fork/__init__.py").is_file())

    def test_verify_refuses_while_anki_runs(self):
        base, _ = self.prepare_session()
        self.process.return_value = Mock(returncode=0, stdout="123\n", stderr="")
        with redirect_stdout(io.StringIO()) as output, redirect_stderr(io.StringIO()) as error:
            with self.assertRaises(SystemExit) as exit_status:
                native.main(["verify", str(base)])
        self.assertEqual(exit_status.exception.code, 2)
        self.assertEqual(output.getvalue(), "")
        self.assertIn("Anki is already running (PIDs: [123])", error.getvalue())

    def test_verify_handles_absence_and_detects_creation_and_removal(self):
        self.collection.unlink()
        base, _ = self.prepare_session()
        with redirect_stdout(io.StringIO()):
            self.assertEqual(native.verify(base), 0)
            self.collection.write_bytes(b"new collection")
            self.assertEqual(native.verify(base), 1)
        present, _ = self.prepare_session()
        self.collection.unlink()
        with redirect_stdout(io.StringIO()) as output:
            self.assertEqual(native.verify(present), 1)
        self.assertEqual(json.loads(output.getvalue())["changes"]["exists"],
                         {"before": True, "after": False})

    def test_launch_refuses_unprepared_or_relocated_receipt(self):
        with self.assertRaisesRegex(RuntimeError, "missing native-session-receipt.json"):
            native.launch(self.root)
        self.process.assert_not_called()
        base, _ = self.prepare_session()
        moved = base.rename(base.with_name("ankiscape-native-moved"))
        self.process.reset_mock()
        with self.assertRaisesRegex(ValueError, "receipt does not match"):
            native.launch(moved)
        self.process.assert_not_called()

    def test_launch_uses_dedicated_app_and_returns_its_exit_status(self):
        base, _ = self.prepare_session()
        self.process.reset_mock()
        self.process.return_value = Mock(returncode=7)
        self.assertEqual(native.launch(base), 7)
        self.process.assert_called_once_with(
            (str(base / native.TEST_APP / "Contents/MacOS/Anki"),), check=False,
        )

    def test_cli_still_rejects_a_base_outside_its_temporary_root(self):
        base, _ = self.prepare_session()
        another_temp = self.root / "another-temp"
        another_temp.mkdir()
        self.process.reset_mock()
        with patch.object(native.tempfile, "tempdir", str(another_temp)):
            with self.assertRaisesRegex(ValueError, "receipt does not match"):
                native.launch(base)
        self.process.assert_not_called()

    def test_bootstrap_process_check_excludes_only_its_own_pid(self):
        base, _ = self.prepare_session()
        module = base / native.TEST_APP / "Contents/Resources/app" / (native.BOOTSTRAP + ".py")
        receipt_digest = hashlib.sha256((base / native.RECEIPT).read_bytes()).hexdigest()
        with patch.object(native.os, "getpid", return_value=123), \
                patch.object(sys, "argv", ["Anki"]), \
                patch.object(native.runpy, "_run_module_as_main") as start:
            self.process.return_value = Mock(returncode=0, stdout="123\n", stderr="")
            native.bootstrap(str(module), str(base), str(self.collection), receipt_digest)
            start.assert_called_once_with("anki", alter_argv=False)
            start.reset_mock()
            sys.argv[:] = ["Anki"]
            self.process.return_value.stdout = "123\n456\n"
            with redirect_stderr(io.StringIO()) as diagnostic:
                with self.assertRaises(SystemExit) as stopped:
                    native.bootstrap(str(module), str(base), str(self.collection), receipt_digest)
            self.assertEqual(stopped.exception.code, 2)
            self.assertIn("Anki is already running", diagnostic.getvalue())
            start.assert_not_called()

    def test_runtime_errors_are_not_caught_as_validation_failures(self):
        base, _ = self.prepare_session()
        module = base / native.TEST_APP / "Contents/Resources/app" / (native.BOOTSTRAP + ".py")
        receipt_digest = hashlib.sha256((base / native.RECEIPT).read_bytes()).hexdigest()
        with patch.object(sys, "argv", ["Anki"]), \
                patch.object(native.runpy, "_run_module_as_main", side_effect=RuntimeError("runtime failure")):
            with self.assertRaisesRegex(RuntimeError, "runtime failure"):
                native.bootstrap(str(module), str(base), str(self.collection), receipt_digest)

    def test_process_probe_failure_is_not_treated_as_anki_stopped(self):
        self.process.return_value = Mock(returncode=2, stderr="probe denied")
        with self.assertRaisesRegex(RuntimeError, "cannot check.*probe denied"):
            native.prepare(self.repo)
        self.assertEqual(list(self.root.glob("ankiscape-native-*")), [])
