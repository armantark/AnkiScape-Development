#!/usr/bin/env python3
"""Own isolated Anki launches and check that the owner's collection is unchanged."""

from __future__ import annotations

import argparse
import ctypes
import hashlib
import json
import os
import plistlib
import runpy
import shlex
import shutil
import subprocess
import sys
import tempfile
from functools import cache
from pathlib import Path
from typing import Optional, Sequence


RECEIPT = "native-session-receipt.json"
ANKI_APP = Path("/Applications/Anki.app")
TEST_APP = "AnkiScape Native Test.app"
BOOTSTRAP = "ankiscape_native_bootstrap"


def owner_collection() -> Path:
    return Path.home() / "Library/Application Support/Anki2/User 1/collection.anki2"


def measure(collection: Path) -> dict:
    try:
        stream = collection.open("rb")
    except FileNotFoundError:
        return {"exists": False}
    with stream:
        before = os.fstat(stream.fileno())
        digest = hashlib.sha256()
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
        after = os.fstat(stream.fileno())
    if (before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns):
        raise RuntimeError(f"collection changed while measuring: {collection}")
    return {"exists": True, "sha256": digest.hexdigest(),
            "size": after.st_size, "mtime_ns": after.st_mtime_ns}


def require_anki_stopped(*, exclude_self: bool = False) -> None:
    result = subprocess.run(
        ("/usr/bin/pgrep", "-ix", "anki|anki-runtime"), text=True, capture_output=True,
    )
    if result.returncode == 0:
        pids = [int(pid) for pid in result.stdout.split()]
        if exclude_self:
            pids = [pid for pid in pids if pid != os.getpid()]
        if not pids:
            return
        raise RuntimeError(
            f"Anki is already running (PIDs: {pids}); "
            "quit Anki before preparing or launching an isolated session"
        )
    if result.returncode != 1:
        raise RuntimeError(f"cannot check whether Anki is running: {result.stderr.strip()}")


@cache
def _clonefile():
    clone = ctypes.CDLL(None, use_errno=True).clonefile
    clone.argtypes = (ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int)
    clone.restype = ctypes.c_int
    return clone


def _copy_file(source: str, destination: str) -> str:
    if sys.platform != "darwin":
        return shutil.copy2(source, destination)
    if _clonefile()(os.fsencode(source), os.fsencode(destination), 0) != 0:
        error = ctypes.get_errno()
        raise OSError(error, os.strerror(error), source, None, destination)
    shutil.copystat(source, destination)
    return destination


def copy_addon(repo: Path, destination: Path) -> None:
    def ignore(directory: str, names: list[str]) -> set[str]:
        ignored = set(shutil.ignore_patterns(
            ".*", "__pycache__", "user_files", "tmp", "memory-bank", "meta.json",
        )(directory, names))
        for name in set(names) - ignored:
            if (Path(directory) / name).is_symlink():
                raise RuntimeError(f"refusing add-on symlink: {Path(directory) / name}")
        return ignored

    shutil.copytree(repo, destination, ignore=ignore, copy_function=_copy_file)


def prepare(repo: Path) -> Path:
    require_safe_environment()
    require_anki_stopped()
    repo = repo.resolve()
    if not (repo / "__init__.py").is_file():
        raise RuntimeError(f"not an add-on repository: {repo}")
    collection = owner_collection()
    baseline = measure(collection)
    base = Path(tempfile.mkdtemp(prefix="ankiscape-native-")).resolve()
    copy_addon(repo, base / "addons21" / "ankiscape_fork")
    app = base / TEST_APP
    shutil.copytree(ANKI_APP, app, symlinks=True, copy_function=_copy_file)
    plist_path = app / "Contents/Info.plist"
    info = plistlib.loads(plist_path.read_bytes())
    if info.get("MainModule") != "anki":
        raise ValueError("Anki app does not use the supported MainModule=anki startup")
    executable = info["CFBundleExecutable"]
    if executable != "Anki":
        raise ValueError("Anki app does not use the supported Anki executable")
    info["CFBundleIdentifier"] = "net.ankiscape.native." + base.name
    info["CFBundleName"] = "AnkiScape Native Test"
    info["CFBundleDisplayName"] = "AnkiScape Native Test"
    info["MainModule"] = BOOTSTRAP
    for key in ("CFBundleDocumentTypes", "CFBundleURLTypes",
                "UTExportedTypeDeclarations", "UTImportedTypeDeclarations"):
        info.pop(key, None)
    plist_path.write_bytes(plistlib.dumps(info))
    receipt = {"base": str(base), "repo": str(repo),
               "collection": str(collection), "baseline": baseline,
               "source_sha256": source_digest(base / "addons21/ankiscape_fork")}
    receipt_path = base / RECEIPT
    receipt_path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    module_root = app / "Contents/Resources/app"
    shutil.copyfile(Path(__file__), module_root / "ankiscape_session_guard.py")
    (module_root / (BOOTSTRAP + ".py")).write_text(
        "from ankiscape_session_guard import bootstrap\n"
        f"bootstrap(__file__, {str(base)!r}, {str(collection)!r}, "
        f"{hashlib.sha256(receipt_path.read_bytes()).hexdigest()!r})\n",
        encoding="utf-8",
    )
    launcher = app / "Contents/MacOS" / executable
    runtime = launcher.with_name(executable + "-runtime")
    launcher.rename(runtime)
    # Briefcase reads this override before importing MainModule, so Python is too late.
    launcher.write_text(
        "#!/bin/sh\n"
        'if [ "${BRIEFCASE_MAIN_MODULE+x}" = x ]; then\n'
        '  echo "error: BRIEFCASE_MAIN_MODULE is forbidden for native tests" >&2\n'
        '  exit 2\n'
        'fi\n'
        f"exec {shlex.quote(str(runtime))} \"$@\"\n",
        encoding="utf-8",
    )
    launcher.chmod(0o755)
    subprocess.run(("/usr/bin/codesign", "--force", "--deep", "--sign", "-", str(app)),
                   check=True, capture_output=True, text=True)
    subprocess.run(("/usr/bin/codesign", "--verify", "--deep", "--strict", str(app)),
                   check=True, capture_output=True, text=True)
    command = (sys.executable, str(Path(__file__).resolve()), "launch", str(base))
    print(json.dumps({"path": str(base), "launch_command": shlex.join(command),
                      "app_path": str(app), "bundle_id": info["CFBundleIdentifier"],
                      "anki_command": shlex.join((str(launcher),))}))
    return base


def read_receipt(base: Path, *, collection: Optional[Path] = None,
                 session_root: Optional[Path] = None) -> dict:
    base = base.resolve()
    root = session_root if session_root is not None else Path(tempfile.gettempdir()).resolve()
    if not (base / RECEIPT).is_file():
        raise RuntimeError(f"not a prepared session (missing {RECEIPT}): {base}")
    receipt = json.loads((base / RECEIPT).read_text(encoding="utf-8"))
    if not isinstance(receipt, dict):
        raise ValueError(f"invalid session receipt: {base}")
    if (receipt.get("base") != str(base)
            or receipt.get("collection") != str(collection or owner_collection())
            or not base.is_relative_to(root)
            or not base.name.startswith("ankiscape-native-")):
        raise ValueError(f"receipt does not match an isolated session: {base}")
    baseline = receipt.get("baseline")
    if not isinstance(baseline, dict) or not isinstance(baseline.get("exists"), bool):
        raise ValueError(f"invalid collection baseline: {base}")
    expected = {"exists", "sha256", "size", "mtime_ns"} if baseline["exists"] else {"exists"}
    if set(baseline) != expected:
        raise ValueError(f"incomplete collection baseline: {base}")
    return receipt


def require_safe_environment() -> None:
    forbidden = sorted(key for key in os.environ if key.startswith("ANKI_")
                       or key in {"BRIEFCASE_MAIN_MODULE", "PYTHONHOME", "PYTHONPATH"})
    if forbidden:
        raise RuntimeError(f"native-test startup overrides are forbidden: {forbidden}")


def require_session_tree(base: Path) -> None:
    # Framework symlinks inside the copied app are expected; data paths must be real.
    for directory, directories, files in os.walk(base, followlinks=False):
        if Path(directory) == base and TEST_APP in directories:
            directories.remove(TEST_APP)
        for name in directories + files:
            path = Path(directory) / name
            if path.is_symlink():
                raise RuntimeError(f"session data contains a symlink: {path}")
    if not (base / "addons21/ankiscape_fork/__init__.py").is_file():
        raise RuntimeError(f"prepared add-on is missing: {base}")


def source_digest(addon: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(addon.rglob("*")):
        relative = path.relative_to(addon)
        if any(part.startswith(".") or part in {"__pycache__", "user_files", "tmp", "meta.json"}
               for part in relative.parts):
            continue
        if path.is_file():
            digest.update(str(relative).encode("utf-8") + b"\0")
            digest.update(hashlib.sha256(path.read_bytes()).digest())
    return digest.hexdigest()


def bootstrap(module: str, bound_base: str, collection: str, receipt_sha256: str) -> None:
    try:
        base = Path(bound_base)
        expected_module = base / TEST_APP / "Contents/Resources/app" / (BOOTSTRAP + ".py")
        if Path(module).resolve() != expected_module or base.resolve() != base:
            raise RuntimeError("native-test app was relocated or redirected")
        if sys.argv[1:]:
            raise RuntimeError("native-test app does not accept startup arguments")
        require_safe_environment()
        require_session_tree(base)
        if hashlib.sha256((base / RECEIPT).read_bytes()).hexdigest() != receipt_sha256:
            raise RuntimeError("native-test receipt changed after preparation")
        receipt = read_receipt(base, collection=Path(collection), session_root=base.parent)
        if source_digest(base / "addons21/ankiscape_fork") != receipt["source_sha256"]:
            raise RuntimeError("prepared add-on source changed after preparation")
        require_anki_stopped(exclude_self=True)
    except (RuntimeError, ValueError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr, flush=True)
        raise SystemExit(2) from None
    sys.argv = [sys.argv[0], "-b", str(base)]
    # Briefcase uses this call to give the application its real __main__ namespace.
    runpy._run_module_as_main("anki", alter_argv=False)


def launch(base: Path) -> int:
    base = base.resolve()
    read_receipt(base)
    launcher = base / TEST_APP / "Contents/MacOS/Anki"
    return subprocess.run((str(launcher),), check=False).returncode


def verify(base: Path) -> int:
    receipt = read_receipt(base)
    # A running Anki may still write the collection, so any result now could be premature.
    require_anki_stopped()
    before = receipt["baseline"]
    after = measure(owner_collection())
    changes = {key: {"before": before.get(key), "after": after.get(key)}
               for key in sorted(before.keys() | after.keys())
               if before.get(key) != after.get(key)}
    print(json.dumps({"path": str(base.resolve()), "collection": receipt["collection"],
                      "unchanged": not changes, "changes": changes}))
    return 1 if changes else 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[2])
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("prepare")
    for command in ("launch", "verify"):
        subparsers.add_parser(command).add_argument("base", type=Path)
    args = parser.parse_args(argv)
    try:
        if args.command == "prepare":
            prepare(args.repo)
        elif args.command == "launch":
            return launch(args.base)
        else:
            return verify(args.base)
    except (RuntimeError, ValueError, OSError, subprocess.CalledProcessError) as exc:
        parser.exit(2, f"error: {exc}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
