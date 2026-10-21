"""Run a pace closure check and retain its command, revision, time and exit."""

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import shlex
import subprocess
import time


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--name", required=True)
    parser.add_argument("--env", action="append", default=[])
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    command = args.command[1:] if args.command[:1] == ["--"] else args.command
    if not command:
        parser.error("a command is required after --")
    environment = dict(entry.split("=", 1) for entry in args.env)
    args.output.mkdir(parents=True, exist_ok=True)
    record = {
        "command": shlex.join(command), "environment": environment,
        "cwd": str(Path.cwd()),
        "head": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
        "started": datetime.now(timezone.utc).isoformat(), "exit": None,
    }
    receipt = args.output / f"{args.name}.json"
    receipt.write_text(json.dumps(record, indent=2) + "\n")
    start = time.monotonic()
    with (args.output / f"{args.name}.log").open("w") as log:
        result = subprocess.run(command, env={**os.environ, **environment}, stdout=log, stderr=subprocess.STDOUT)
    record.update(exit=result.returncode, seconds=time.monotonic() - start,
                  ended=datetime.now(timezone.utc).isoformat())
    receipt.write_text(json.dumps(record, indent=2) + "\n")
    print(json.dumps(record, indent=2), flush=True)
    raise SystemExit(result.returncode)


if __name__ == "__main__":
    main()
