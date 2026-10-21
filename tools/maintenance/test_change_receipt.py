"""List existing test functions touched by a diff for decision/provenance receipts."""

import argparse
import ast
from pathlib import Path
import re
import subprocess


def _file_test_functions(path, base):
    tree = ast.parse(Path(path).read_text())
    scopes = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
    diff = subprocess.check_output(["git", "diff", base, "--unified=0", "--", path], text=True)
    names = []
    for match in re.finditer(r"^@@ .*?\+(\d+)(?:,(\d+))? @@", diff, re.M):
        line = int(match[1])
        containing = [node for node in scopes if node.lineno <= line <= node.end_lineno]
        if containing:
            names.append(f"{path}:{containing[-1].name}")
    return names


def changed_test_functions(base):
    paths = subprocess.check_output(["git", "diff", base, "--name-only", "--", "tests"], text=True).splitlines()
    names = []
    for path in paths:
        if path.endswith(".py") and Path(path).is_file():
            names.extend(_file_test_functions(path, base))
    return list(dict.fromkeys(names))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", default="HEAD")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.write_text("\n".join(changed_test_functions(args.base)) + "\n")


if __name__ == "__main__":
    main()
