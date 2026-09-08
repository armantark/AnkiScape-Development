"""Parent-only static measurement of the operational packet; imports no product code."""

import ast
import gzip
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
from unittest.mock import patch

if sys.flags.optimize or "PYTHONOPTIMIZE" in os.environ:
    raise SystemExit("Optimized interpreter refused; static pins use assertions.")
root = Path(__file__).resolve().parents[3]
evidence = Path(__file__).resolve().parent
pins = json.loads((evidence / "operational-bindings.json").read_text())
attempts = []


def sha(value):
    return hashlib.sha256(value).hexdigest()


def forbid_product(event, values):
    if event == "import" and values[0].split(".")[0] in {"ankiscape", "pkg_alias", "tests"}:
        attempts.append(values[0])
        raise RuntimeError("Product import forbidden in static verification.")


sys.addaudithook(forbid_product)
gate_path = Path(pins["gate"]["path"])
assert sha(gate_path.read_bytes()) == pins["gate"]["sha256"]
for name, tool in pins["tools"].items():
    assert Path(shutil.which(name)).resolve() == Path(tool["resolved_path"]), name
    assert sha(Path(tool["path"]).read_bytes()) == tool["sha256"], name
inventory_raw = (evidence / "source-inventory.json.gz").read_bytes()
assert sha(inventory_raw) == pins["inventory_sha256"]
inventory = json.loads(gzip.decompress(inventory_raw))
for name, expected in inventory.items():
    assert sha((root / name).read_bytes()) == expected, name
for name, expected in pins["sources"].items():
    assert sha((root / name).read_bytes()) == expected, name
ast_hashes = {
    name: sha(ast.dump(ast.parse((root / name).read_bytes())).encode())
    for name in pins["sources"]
}
spec = importlib.util.spec_from_file_location("_fixed_static_gate", gate_path)
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)
assert {key: getattr(gate, key) for key in pins["gate"]["thresholds"]} == pins["gate"]["thresholds"]
assert gate.PEP8_LAYOUT_CODES == pins["gate"]["layout_codes"]
raw = []
run_tool = gate.run_tool


def capture(argv, tool):
    result = run_tool(argv, tool)
    row = {"argv": argv, "tool": tool, "exit_code": result.returncode,
           "stdout": result.stdout, "stderr": result.stderr}
    if tool == "complexipy":
        directory = Path(argv[argv.index("--output") + 1])
        row["reports"] = {path.name: path.read_text() for path in directory.glob("*.json")}
    raw.append(row)
    (evidence / "operational-static-raw.json.gz").write_bytes(
        gzip.compress(json.dumps(raw, indent=2).encode(), mtime=0)
    )
    return result


with tempfile.TemporaryDirectory(prefix="vampyre-static-") as temporary:
    scratch = Path(temporary)
    base_tree, candidate_tree = scratch / "base", scratch / "candidate"
    base_tree.mkdir()
    for name in pins["sources"]:
        destination = candidate_tree / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes((root / name).read_bytes())
    metrics = {}
    with patch.object(gate, "run_tool", side_effect=capture):
        for label, tree in (("base", base_tree), ("candidate", candidate_tree)):
            metrics[label] = {name: function(tree) for name, function in (
                ("ccn", gate.ccn_by_function), ("cognitive", gate.cognitive_by_function),
                ("halstead", gate.halstead_by_function), ("layout", gate.pep8_layout_findings),
            )}
    failures = {name: gate.ratchet(metrics["candidate"][name], metrics["base"][name], limit)
                for name, limit in (("ccn", gate.CCN_MAX), ("cognitive", gate.COGNITIVE_MAX),
                                    ("halstead", gate.HALSTEAD_MAX))}
    failures["layout"] = gate.layout_ratchet(metrics["candidate"]["layout"], metrics["base"]["layout"])
    base_lines = gate.line_counts(base_tree, list(pins["sources"]))
    candidate_lines = gate.line_counts(candidate_tree, list(pins["sources"]))
    failures["file_growth"] = [(name, count) for name, count in candidate_lines.items()
                               if count > gate.FILE_LINES_MAX and count > base_lines.get(name, 0)]
    report = {"status": "PASS" if not any(failures.values()) else "FAIL", "sources": pins["sources"],
              "inventory_sha256": pins["inventory_sha256"], "gate": pins["gate"], "tools": pins["tools"],
              "metrics": {label: {kind: {"|".join(key): value for key, value in values.items()}
                                   for kind, values in table.items()} for label, table in metrics.items()},
              "lines": {"base": base_lines, "candidate": candidate_lines}, "failures": failures,
              "ast_sha256": ast_hashes,
              "product_import_attempts": attempts, "python": sys.executable, "python_version": sys.version}
for name, expected in {**inventory, **pins["sources"]}.items():
    assert sha((root / name).read_bytes()) == expected, name
assert sha(gate_path.read_bytes()) == pins["gate"]["sha256"]
for tool in pins["tools"].values():
    assert sha(Path(tool["path"]).read_bytes()) == tool["sha256"]
assert not attempts
(evidence / "operational-static-measurements.json").write_text(json.dumps(report, indent=2) + "\n")
assert not any(failures.values()), failures
print(json.dumps({"status": report["status"], "failures": failures, "sources": pins["sources"]}, indent=2))
