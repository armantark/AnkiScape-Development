"""Replay only the two cape IDs with class origins in the same stdout stream."""

from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess

from capture_cache import PACKET, ROOT, sha256


if __name__ == "__main__":
    manifest = PACKET / "cache-provenance-replay.json"
    if manifest.exists():
        raise SystemExit("The provenance replay already exists; do not overwrite it")
    provenance = json.loads((PACKET / "cache-decoder-provenance.json").read_text())
    java = Path(provenance["java_bin"])
    classes = ROOT / "tmp/review/cape-query-classes"
    classes.mkdir(parents=True, exist_ok=True)
    source = ROOT / "tools/OpenRs2CacheItemSearch.java"
    helper = PACKET / "CapeCacheQuery.java"
    classpath = ":".join(provenance["actual_classpath_order"])
    command = [str(java.with_name("javac")), "--class-path", classpath, "-d", str(classes), str(source), str(helper)]
    compiled = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
    compiled.check_returncode()
    report = {
        "captured_at_utc": datetime.now(timezone.utc).isoformat(),
        "cwd": str(ROOT),
        "compile_argv": command,
        "compile_stdout": compiled.stdout,
        "compile_stderr": compiled.stderr,
        "query_source_sha256": sha256(source),
        "origin_helper_sha256": sha256(helper),
        "compiled_classes": {path.name: sha256(path) for path in sorted(classes.glob("*.class"))},
        "current_decoder_jars": [],
        "queries": [],
        "historical_limit": "Current classpath order does not establish which JAR an earlier source pass loaded.",
    }
    for entry in provenance["available_item_definition_decoder_jars"]:
        path = Path(entry["path"])
        assert sha256(path) == entry["sha256"]
        report["current_decoder_jars"].append({**entry, "mtime_ns": path.stat().st_mtime_ns})
    for revision in (727, 742):
        binding = json.loads((PACKET / f"cache-{revision}-input-binding.json").read_text())
        assert sha256(Path(binding["archive_path"])) == binding["archive_sha256"]
        for member in binding["members"]:
            assert sha256(Path(member["extracted_path"])) == member["zip_member_sha256"]
        verified = datetime.now(timezone.utc).isoformat()
        command = [str(java), "--class-path", str(classes) + ":" + classpath, "CapeCacheQuery", binding["extracted_path"], "--id", "10069", "10071"]
        result = subprocess.run(command, cwd=ROOT, capture_output=True)
        stdout = PACKET / f"cache-{revision}-provenance-replay.txt"
        stderr = PACKET / f"cache-{revision}-provenance-replay.stderr"
        stdout.write_bytes(result.stdout)
        stderr.write_bytes(result.stderr)
        report["queries"].append({
            "revision": revision, "argv": command, "cwd": str(ROOT),
            "inputs_reverified_at_utc": verified,
            "finished_at_utc": datetime.now(timezone.utc).isoformat(),
            "exit_code": result.returncode,
            "stdout": stdout.name, "stdout_sha256": sha256(stdout),
            "stderr": stderr.name, "stderr_sha256": sha256(stderr),
        })
        manifest.write_text(json.dumps(report, indent=2) + "\n")
        result.check_returncode()
        print(result.stdout.decode(), flush=True)
