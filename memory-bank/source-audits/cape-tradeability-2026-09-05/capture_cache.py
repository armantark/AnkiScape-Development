"""Bind the selected cape queries to dated archive bytes before each query."""

from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import zipfile


PACKET = Path(__file__).resolve().parent
ROOT = PACKET.parents[2]
CACHE_ROOT = Path.home() / "Library/Caches/codex/2012scape-openrs2"


def sha256(path: Path) -> str:
    with path.open("rb") as source:
        return hashlib.file_digest(source, "sha256").hexdigest()


def git(*arguments: str) -> str:
    return subprocess.check_output(["git", *arguments], cwd=ROOT, text=True).strip()


def source_record(relative: str) -> dict:
    path = ROOT / relative
    return {
        "path": str(path),
        "repository_commit": git("rev-parse", "HEAD"),
        "git_blob": git("rev-parse", f"HEAD:{relative}"),
        "bytes": path.stat().st_size,
        "sha256": sha256(path),
    }


def capture(revision: int, date: str, archive_id: int, java_bin: str, classpath: list[str]) -> dict:
    archive = CACHE_ROOT / f"runescape-{revision}-{date}-openrs2-{archive_id}-disk.zip"
    extracted_parent = CACHE_ROOT / "extracted" / f"{revision}-{date}"
    cache = extracted_parent / "cache"
    members = []
    before_stats = {}
    with zipfile.ZipFile(archive) as zipped:
        for entry in zipped.infolist():
            if entry.is_dir():
                continue
            path = extracted_parent / entry.filename
            assert path.resolve().is_relative_to(cache.resolve()), path
            stat = path.stat()
            with zipped.open(entry) as source:
                archive_member_sha = hashlib.file_digest(source, "sha256").hexdigest()
            extracted_sha = sha256(path)
            assert stat.st_size == entry.file_size and archive_member_sha == extracted_sha
            before_stats[str(path)] = (stat.st_size, stat.st_mtime_ns)
            members.append({
                "zip_member": entry.filename,
                "extracted_path": str(path),
                "resolved_extracted_path": str(path.resolve()),
                "bytes": entry.file_size,
                "zip_member_sha256": archive_member_sha,
                "extracted_sha256": extracted_sha,
            })
    actual_files = {str(path) for path in cache.rglob("*") if path.is_file()}
    assert actual_files == set(before_stats), "Extra or missing extracted cache files"
    binding = {
        "revision": revision,
        "date": date,
        "archive_url": f"https://archive.openrs2.org/caches/runescape/{archive_id}/disk.zip",
        "archive_path": str(archive),
        "archive_bytes": archive.stat().st_size,
        "archive_sha256": sha256(archive),
        "extracted_path": str(cache),
        "members": members,
        "no_extra_or_missing_files": True,
        "input_verification_finished_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    binding_path = PACKET / f"cache-{revision}-input-binding.json"
    binding_path.write_text(json.dumps(binding, indent=2) + "\n")
    command = [
        java_bin, "--class-path", ":".join(classpath),
        str(ROOT / "tools/OpenRs2CacheItemSearch.java"), str(cache),
        "--id", "10069", "10071",
    ]
    started = datetime.now(timezone.utc).isoformat()
    result = subprocess.run(command, cwd=ROOT, capture_output=True)
    output = PACKET / f"cache-{revision}-items-10069-10071.txt"
    error = PACKET / f"cache-{revision}-items-10069-10071.stderr"
    output.write_bytes(result.stdout)
    error.write_bytes(result.stderr)
    after_stats = {
        name: (Path(name).stat().st_size, Path(name).stat().st_mtime_ns)
        for name in before_stats
    }
    record = {
        "revision": revision,
        "cwd": str(ROOT),
        "argv": command,
        "started_at_utc": started,
        "finished_at_utc": datetime.now(timezone.utc).isoformat(),
        "exit_code": result.returncode,
        "stdout": output.name,
        "stdout_sha256": sha256(output),
        "stderr": error.name,
        "stderr_sha256": sha256(error),
        "input_binding": binding_path.name,
        "input_binding_sha256": sha256(binding_path),
        "input_size_and_mtime_unchanged_after_query": before_stats == after_stats,
    }
    (PACKET / f"cache-{revision}-query.json").write_text(json.dumps(record, indent=2) + "\n")
    assert result.returncode == 0 and before_stats == after_stats, record
    print(json.dumps({
        "revision": revision, "exit_code": result.returncode,
        "stdout": output.name, "stdout_sha256": sha256(output),
        "verified_input_members": len(members),
    }), flush=True)
    return record


if __name__ == "__main__":
    if any(PACKET.glob("cache-*-query.json")):
        raise SystemExit("Existing query outputs must not be overwritten")
    assert Path.cwd() == ROOT
    gradle = Path(os.environ.get("GRADLE_CACHE", str(Path.home() / ".gradle/caches/modules-2/files-2.1")))
    jar_paths = subprocess.check_output(["find", str(gradle), "-name", "*.jar", "-print"], text=True).splitlines()
    decoder_jars = []
    for name in jar_paths:
        path = Path(name)
        with zipfile.ZipFile(path) as jar:
            if "com/rs/cache/loaders/ItemDefinitions.class" in jar.namelist():
                decoder_jars.append({"path": name, "bytes": path.stat().st_size, "sha256": sha256(path)})
    selected, = [
        entry for entry in decoder_jars
        if Path(entry["path"]).is_relative_to(gradle / "rs.darkan/core/2.0.5")
    ]
    excluded = {entry["path"] for entry in decoder_jars if entry != selected}
    classpath = [path for path in jar_paths if path not in excluded]
    java_bin = os.environ.get("JAVA_BIN", "/opt/homebrew/opt/openjdk@25/bin/java")
    provenance = {
        "sources": [source_record(name) for name in ("tools/query_openrs2_cache.sh", "tools/OpenRs2CacheItemSearch.java")],
        "java_bin": java_bin,
        "java_binary_sha256": sha256(Path(java_bin)),
        "gradle_cache": str(gradle),
        "wrapper_classpath_order": jar_paths,
        "actual_classpath_order": classpath,
        "available_item_definition_decoder_jars": decoder_jars,
        "selected_decoder_jar": selected,
        "excluded_decoder_jars": sorted(excluded),
        "invocation": "The unchanged Java query source is invoked directly with an explicit classpath because the shell wrapper includes competing decoder versions.",
        "qualification": "Only selected client definitions are queried. Exchangeability does not prove direct player tradeability.",
    }
    (PACKET / "cache-decoder-provenance.json").write_text(json.dumps(provenance, indent=2) + "\n")
    for revision, date, archive_id in ((727, "2012-07-24", 309), (742, "2012-11-07", 544)):
        capture(revision, date, archive_id, java_bin, classpath)
