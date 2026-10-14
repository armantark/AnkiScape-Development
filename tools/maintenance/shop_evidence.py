"""Project exact shop rows without printing the generated catalog."""

import argparse
import ast
import hashlib
import json
import subprocess
from pathlib import Path


def _shops(source):
    assignment = next(
        node for node in ast.parse(source).body
        if isinstance(node, ast.AnnAssign)
        and isinstance(node.target, ast.Name)
        and node.target.id == "SHOP_DATA"
    )
    return ast.literal_eval(assignment.value)


def project(repo, names, limit):
    path = repo / "data/shop_data.py"
    source = path.read_bytes()
    shops = _shops(source)
    matches = {name: [] for name in names}
    for shop_id, shop in shops.items():
        for row in shop["stock"]:
            if row["item_name"] in matches:
                matches[row["item_name"]].append({
                    "shop_id": shop_id,
                    "provider": {key: value for key, value in shop.items() if key != "stock"},
                    "row": row,
                })
    for rows in matches.values():
        rows.sort(key=lambda entry: (bool(entry["provider"].get("access")), entry["shop_id"]))
    return {
        "revision": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo, text=True).strip(),
        "dirty_paths": subprocess.check_output(["git", "status", "--short"], cwd=repo, text=True).splitlines(),
        "source_path": str(path),
        "source_sha256": hashlib.sha256(source).hexdigest(),
        "scope": "Current catalog rows; provider access and row availability still require runtime checks.",
        "items": {name: {"matches": len(rows), "providers": rows[:limit]} for name, rows in matches.items()},
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("names", nargs="+")
    parser.add_argument("--providers", type=int, default=2)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if not 1 <= args.providers <= 5:
        parser.error("--providers must be between 1 and 5")
    repo = Path(__file__).resolve().parents[2]
    if args.output.resolve().is_relative_to(repo):
        parser.error("evidence output must be outside the checkout")
    result = project(repo, args.names, args.providers)
    with args.output.open("x") as output:
        output.write(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"output": str(args.output), "bytes": args.output.stat().st_size,
                      "matches": {name: row["matches"] for name, row in result["items"].items()}}))


if __name__ == "__main__":
    main()
