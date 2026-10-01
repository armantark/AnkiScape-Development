import gzip
import json
import os
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
LEGACY = "LEGACY_BANK_RUN_REVIEWS = 'two reviews per carried bank run'"
HELPER = (
    "def settle_carried_pack(player_data):\n"
    "    return {**player_data, 'carried_pack_settled': True}\n"
)


class FixCitationDriftTests(unittest.TestCase):
    def setUp(self) -> None:
        self.root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.env = {
            **os.environ,
            "GIT_AUTHOR_NAME": "Citation test",
            "GIT_AUTHOR_EMAIL": "citation-test@example.invalid",
            "GIT_COMMITTER_NAME": "Citation test",
            "GIT_COMMITTER_EMAIL": "citation-test@example.invalid",
            "GIT_CONFIG_GLOBAL": os.devnull,
            "GIT_CONFIG_SYSTEM": os.devnull,
        }
        self.report = Path(self.enterContext(tempfile.TemporaryDirectory())) / "drift.json.gz"
        self._git("init", "-q")

    def _git(self, *args: str) -> str:
        return subprocess.run(
            ["git", *args], cwd=self.root, env=self.env, check=True, capture_output=True, text=True
        ).stdout.strip()

    def _write(self, relative: str, content: str) -> None:
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    def _commit(self, message: str) -> str:
        self._git("add", "--all")
        self._git("commit", "-q", "-m", message)
        return self._git("rev-parse", "HEAD")

    def _audit(self) -> dict:
        # The audit exits 1 whenever it finds drift; the report is the result under test.
        subprocess.run(
            [sys.executable, str(ROOT / "tools" / "audit_citation_drift.py"), "--root", str(self.root),
             "--no-default-sources", "--output", str(self.report)],
            check=False, capture_output=True, text=True,
        )
        return json.loads(gzip.decompress(self.report.read_bytes()))

    def test_split_module_is_repointed_and_deleted_code_is_pinned(self) -> None:
        self._write("logic/runtime.py", "import json\n\n\n" + HELPER + "\n\ndef answer():\n    return None\n")
        self._write("logic/legacy.py", LEGACY + "\n")
        self._write(
            "memory-bank/record.md",
            "# Carried pack\n\n"
            "- Settlement lives at `logic/runtime.py:4-5`.\n"
            "- The old bank-run cost was `logic/legacy.py:1`.\n",
        )
        written = self._commit("Record citations")
        # The helper moves into its own module and the legacy constant is deleted, so both
        # citations drift: one to code that still exists, one to code that is gone.
        self._write("logic/runtime.py", "def answer():\n    return None\n")
        self._write("logic/carried_pack.py", HELPER)
        (self.root / "logic" / "legacy.py").unlink()
        self._commit("Split carried-pack settlement and drop the legacy cost")
        self.assertEqual(self._audit()["actionable"], 2)

        subprocess.run(
            [sys.executable, str(ROOT / "tools" / "memory_bank" / "fix_citation_drift.py"), "--root", str(self.root),
             "--report", str(self.report), "--apply"],
            check=True, capture_output=True, text=True,
        )

        self._commit("Fix citation drift")
        report = self._audit()
        self.assertEqual(report["actionable"], 0)
        # The repointed citation resolves to the moved helper in the current tree.
        resolved = [(row["real_target"], tuple(row["real_text"])) for row in report["results"]]
        self.assertEqual(resolved, [("logic/carried_pack.py:1-2", tuple(HELPER.splitlines()))])
        # The audit skips the pinned citation; `git show` proves the pin names the deleted line.
        record = (self.root / "memory-bank" / "record.md").read_text(encoding="utf-8")
        commit, path, line = re.search(r"`([0-9a-f]{8}):(logic/legacy\.py):(\d+)`", record).groups()
        self.assertEqual(commit, written[:8])
        self.assertEqual(self._git("show", f"{commit}:{path}").splitlines()[int(line) - 1], LEGACY)


if __name__ == "__main__":
    unittest.main()
