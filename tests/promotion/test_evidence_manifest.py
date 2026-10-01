import gzip
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from tools.dispatcher.verify_evidence import EvidenceVerificationError, verify_manifest


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class EvidenceManifestTest(unittest.TestCase):
    def setUp(self):
        self._temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self._temporary.cleanup)
        self.root = Path(self._temporary.name)
        self.manifest_path = self.root / "manifest.json"

    def _write_manifest(self, artifacts: dict[str, dict[str, object]]) -> None:
        self.manifest_path.write_text(
            json.dumps({"artifacts": artifacts}),
            encoding="utf-8",
        )

    def test_verifies_mixed_plaintext_and_gzip_artifacts(self):
        plaintext = b"plain evidence\n"
        decompressed = b"compressed evidence\n"
        compressed = gzip.compress(decompressed, mtime=0)
        (self.root / "plain.txt").write_bytes(plaintext)
        (self.root / "compressed.txt.gz").write_bytes(compressed)
        self._write_manifest({
            "plain.txt": {"bytes": len(plaintext), "sha256": _sha256(plaintext)},
            "compressed.txt.gz": {
                "gzip_bytes": len(compressed),
                "gzip_sha256": _sha256(compressed),
                "plaintext_bytes": len(decompressed),
                "plaintext_sha256": _sha256(decompressed),
            },
        })

        self.assertEqual(verify_manifest(self.manifest_path, self.root), 2)

    def test_names_corrupted_plaintext_artifact(self):
        original = b"original"
        (self.root / "plain.txt").write_bytes(b"changed")
        self._write_manifest({
            "plain.txt": {"bytes": len(original), "sha256": _sha256(original)},
        })

        with self.assertRaisesRegex(EvidenceVerificationError, r"plain\.txt: bytes mismatch"):
            verify_manifest(self.manifest_path, self.root)

    def test_names_corrupted_gzip_artifact(self):
        decompressed = b"evidence"
        compressed = gzip.compress(decompressed, mtime=0)
        (self.root / "evidence.gz").write_bytes(compressed + b"changed")
        self._write_manifest({
            "evidence.gz": {
                "gzip_bytes": len(compressed),
                "gzip_sha256": _sha256(compressed),
                "plaintext_bytes": len(decompressed),
                "plaintext_sha256": _sha256(decompressed),
            },
        })

        with self.assertRaisesRegex(EvidenceVerificationError, r"evidence\.gz: gzip_bytes mismatch"):
            verify_manifest(self.manifest_path, self.root)

    def test_rejects_ambiguous_or_incomplete_declarations(self):
        artifact = self.root / "artifact"
        artifact.write_bytes(b"evidence")
        declarations = (
            {"bytes": 8, "sha256": _sha256(b"evidence"), "gzip_sha256": "unused"},
            {"sha256": _sha256(b"evidence")},
            {"gzip_bytes": 8, "gzip_sha256": _sha256(b"evidence")},
        )
        for declaration in declarations:
            with self.subTest(declaration=declaration):
                self._write_manifest({"artifact": declaration})
                with self.assertRaisesRegex(
                    EvidenceVerificationError,
                    r"artifact: unsupported hash declaration",
                ):
                    verify_manifest(self.manifest_path, self.root)

    def test_rejects_artifact_paths_outside_the_explicit_directory(self):
        outside = self.root.parent / "outside-evidence"
        outside.write_bytes(b"evidence")
        self.addCleanup(outside.unlink)
        self._write_manifest({
            "../outside-evidence": {"bytes": 8, "sha256": _sha256(b"evidence")},
        })

        with self.assertRaisesRegex(EvidenceVerificationError, "outside artifact directory"):
            verify_manifest(self.manifest_path, self.root)


if __name__ == "__main__":
    unittest.main()
