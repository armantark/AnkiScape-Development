"""Retain the four bounded public wiki responses for the two-cape audit."""

import argparse
from datetime import datetime, timezone
import gzip
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
from urllib.parse import urlencode


PACKET = Path(__file__).resolve().parent


def retain_bytes(name: str, data: bytes) -> dict:
    path = PACKET / (name + ".gz")
    compressed = gzip.compress(data, compresslevel=9, mtime=0)
    assert gzip.decompress(compressed) == data
    path.write_bytes(compressed)
    return {
        "path": path.name,
        "raw_bytes": len(data),
        "raw_sha256": hashlib.sha256(data).hexdigest(),
        "gzip_bytes": len(compressed),
        "gzip_sha256": hashlib.sha256(compressed).hexdigest(),
    }


def fetch(name: str, selection: dict) -> dict:
    parameters = {
        "action": "query",
        "format": "json",
        "formatversion": "2",
        "prop": "revisions",
        "rvprop": "ids|timestamp|content",
        "rvslots": "main",
        **selection,
    }
    url = "https://runescape.wiki/api.php?" + urlencode(parameters)
    with tempfile.TemporaryDirectory(prefix="cape-source-response-") as temporary:
        response = Path(temporary) / "response.json"
        headers = Path(temporary) / "headers"
        command = [
            "curl", "--fail", "--silent", "--show-error", "--location",
            "--retry", "2", "--retry-delay", "1", "--connect-timeout", "15",
            "--max-time", "45", "--dump-header", str(headers),
            "--output", str(response), url,
        ]
        started = datetime.now(timezone.utc).isoformat()
        completed = subprocess.run(command, text=True, capture_output=True)
        record = {
            "name": name,
            "started_at_utc": started,
            "finished_at_utc": datetime.now(timezone.utc).isoformat(),
            "cwd": str(Path.cwd()),
            "argv": command,
            "url": url,
            "exit_code": completed.returncode,
            "stderr": completed.stderr,
        }
        if headers.exists():
            record["headers"] = retain_bytes(name + ".headers", headers.read_bytes())
        if response.exists():
            raw = response.read_bytes()
            record["response"] = retain_bytes(name + ".json", raw)
            if completed.returncode == 0:
                payload = json.loads(raw)
                if "error" in payload:
                    record["api_error"] = payload["error"]
                else:
                    page, = payload["query"]["pages"]
                    revision, = page["revisions"]
                    content = revision["slots"]["main"]["content"]
                    record["main_slot"] = retain_bytes(
                        name + ".wikitext", content.encode("utf-8")
                    )
                    record["revision"] = {
                        "title": page["title"],
                        "pageid": page["pageid"],
                        "revid": revision["revid"],
                        "parentid": revision["parentid"],
                        "timestamp": revision["timestamp"],
                    }
        return record


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    phase = parser.add_mutually_exclusive_group()
    phase.add_argument("--june-corroboration", action="store_true")
    phase.add_argument("--pre-marker-parents", action="store_true")
    options = parser.parse_args()
    manifest = PACKET / "requests.json"
    if manifest.exists() and not (options.june_corroboration or options.pre_marker_parents):
        raise SystemExit("Existing responses must be reviewed before any retry")
    requests = [
        ("spotted-cape-item", {"revids": "6308186"}),
        ("spottier-cape-item", {"revids": "6308184"}),
        ("spotted-cape-exchange", {"titles": "Exchange:Spotted cape"}),
        ("spottier-cape-exchange", {"titles": "Exchange:Spottier cape"}),
    ]
    if options.june_corroboration:
        requests = [
            ("spotted-cape-item-june", {"titles": "Spotted cape"}),
            ("spottier-cape-item-june", {"titles": "Spottier cape"}),
        ]
    if options.pre_marker_parents:
        requests = [
            ("spotted-cape-item-before-beta", {"revids": "5549170"}),
            ("spottier-cape-item-before-beta", {"revids": "5728066"}),
        ]
    records = json.loads(manifest.read_text()) if manifest.exists() else []
    if any(record["name"] in dict(requests) for record in records):
        raise SystemExit("The selected responses already exist; do not overwrite them")
    for name, selection in requests:
        if "titles" in selection:
            selection.update({
                "rvlimit": "1",
                "rvstart": (
                    "2012-06-25T23:59:59Z" if options.june_corroboration
                    else "2012-11-19T23:59:59Z"
                ),
                "rvdir": "older",
            })
        record = fetch(name, selection)
        records.append(record)
        manifest.write_text(json.dumps(records, indent=2) + "\n")
        print(json.dumps({"name": name, "revision": record.get("revision")}), flush=True)
        if record["exit_code"] or "api_error" in record or "revision" not in record:
            raise SystemExit("Source response failed qualification; inspect retained bytes")
