#!/usr/bin/env python3
"""Dump and hash a module's complete public module-level surface.

The output is intentionally a text format rather than a Python object display.  Mapping
and set members are sorted by their normalized representation, and functions
and classes omit implementation details that are not part of an import
surface.  This makes the final digest useful as a pure-move regression guard.
"""

from __future__ import annotations

import argparse
import dataclasses
import enum
import hashlib
import importlib
import importlib.util
import inspect
import json
import os
import platform
import subprocess
import sys
import types
from collections.abc import Mapping
from pathlib import Path
from typing import Any, Callable
import typing


ROOT = Path(__file__).resolve().parents[1]
# The root package's import name enters the digest through ``__name__``, so it
# is fixed rather than taken from the checkout folder.  This is the canonical
# checkout's name, which the pinned root digest was recorded under; the
# ``ankiscape`` name is unavailable because pkg_alias binds it to an alias that
# deliberately skips the root initializer.
ROOT_PACKAGE_NAME = "ankiscape_fork"


def _qualified_type(value: Any) -> str:
    return type(value).__qualname__


def _qualified_object(value: Any) -> str:
    name = getattr(value, "__qualname__", None) or getattr(value, "__name__", None)
    if name:
        return name
    return _qualified_type(value)


def _safe_signature(value: Any) -> str | None:
    try:
        signature = inspect.signature(value)
    except (TypeError, ValueError):
        return None
    parameters = []
    for parameter in signature.parameters.values():
        item: dict[str, Any] = {"name": parameter.name, "kind": parameter.kind.name}
        if parameter.annotation is not inspect.Parameter.empty:
            item["annotation"] = _normalize(parameter.annotation, set())
        if parameter.default is not inspect.Parameter.empty:
            item["default"] = _normalize(parameter.default, set())
        parameters.append(item)
    result: dict[str, Any] = {"parameters": parameters}
    if signature.return_annotation is not inspect.Signature.empty:
        result["return"] = _normalize(signature.return_annotation, set())
    return _json(result)


def _json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=True, separators=(",", ":"), sort_keys=True)


def _stable_string(value: str) -> str:
    """Keep repository-local paths stable when the checkout moves."""

    root = str(ROOT)
    if value == root:
        return "<repo>"
    prefix = root + os.sep
    if value.startswith(prefix):
        return "<repo>/" + value[len(prefix) :].replace(os.sep, "/")
    return value


def _normalize_function(value: Any, _active: set[int]) -> dict[str, Any]:
    result: dict[str, Any] = {"type": "function", "qualified_name": _qualified_object(value)}
    signature = _safe_signature(value)
    if signature is not None:
        result["signature"] = signature
    return result


def _normalize_class(value: Any, _active: set[int]) -> dict[str, Any]:
    result: dict[str, Any] = {"type": "class", "qualified_name": _qualified_object(value)}
    signature = _safe_signature(value)
    if signature is not None:
        result["signature"] = signature
    return result


def _normalize_enum(value: enum.Enum, active: set[int]) -> dict[str, Any]:
    return {
        "type": "enum",
        "class": _qualified_object(value.__class__),
        "name": value.name,
        "value": _normalize(value.value, active),
    }


def _normalize_active(value: Any, active: set[int], build: Callable[[], Any]) -> Any:
    object_id = id(value)
    if object_id in active:
        return {"type": "cycle", "class": _qualified_type(value)}
    active.add(object_id)
    try:
        return build()
    finally:
        active.remove(object_id)


def _normalize_dataclass(value: Any, active: set[int]) -> Any:
    def build() -> dict[str, Any]:
        fields = {
            field.name: _normalize(getattr(value, field.name), active)
            for field in sorted(dataclasses.fields(value), key=lambda item: item.name)
        }
        return {"type": "dataclass", "class": _qualified_object(value.__class__), "fields": fields}

    return _normalize_active(value, active, build)


def _normalize_mapping(value: Mapping[Any, Any], active: set[int]) -> Any:
    def build() -> dict[str, Any]:
        pairs = [(_normalize(key, active), _normalize(item, active)) for key, item in value.items()]
        pairs.sort(key=lambda pair: (_json(pair[0]), _json(pair[1])))
        return {"type": "mapping", "class": _qualified_type(value), "items": pairs}

    return _normalize_active(value, active, build)


def _normalize_set(value: set[Any] | frozenset[Any], active: set[int]) -> Any:
    def build() -> dict[str, Any]:
        members = sorted((_normalize(item, active) for item in value), key=_json)
        return {"type": "set", "class": _qualified_type(value), "items": members}

    return _normalize_active(value, active, build)


def _normalize_sequence(value: tuple[Any, ...] | list[Any], active: set[int]) -> Any:
    def build() -> dict[str, Any]:
        items = [_normalize(item, active) for item in value]
        return {"type": "sequence", "class": _qualified_type(value), "items": items}

    return _normalize_active(value, active, build)


def _normalize_path(value: Path, _active: set[int]) -> dict[str, Any]:
    return {"type": "path", "value": _stable_string(os.fspath(value))}


def _normalize_object(value: Any, active: set[int]) -> Any:
    def build() -> dict[str, Any]:
        attributes = getattr(value, "__dict__")
        public_attributes = {
            name: _normalize(attributes[name], active)
            for name in sorted(attributes)
            if not name.startswith("_")
        }
        return {"type": "object", "class": _qualified_type(value), "attributes": public_attributes}

    return _normalize_active(value, active, build)


def _normalize_typing(value: Any, active: set[int]) -> dict[str, Any] | None:
    module = getattr(value, "__module__", None)
    name = getattr(value, "__qualname__", None) or getattr(value, "__name__", None)
    origin = typing.get_origin(value)
    args = typing.get_args(value)
    if module == "typing" and name and origin is None and not args:
        return {"type": "typing_symbol", "qualified_name": f"typing.{name}"}
    if origin is None:
        return None
    if origin is typing.Union or origin is types.UnionType:
        origin_name = "typing.Union"
    else:
        origin_name = _qualified_object(origin)
    return {
        "type": "typing_alias",
        "origin": origin_name,
        "args": [_normalize(argument, active) for argument in args],
    }


def _normalize_fallback(value: Any, _active: set[int]) -> dict[str, Any]:
    return {"type": "unrepresentable", "class": _qualified_type(value)}


_EXACT_HANDLERS: dict[type[Any], Callable[[Any, set[int]], Any]] = {
    bytes: lambda value, _active: {"type": "bytes", "hex": value.hex()},
    types.ModuleType: lambda value, _active: {
        "type": "module", "name": getattr(value, "__name__", _qualified_type(value))
    },
    types.FunctionType: _normalize_function,
    types.MethodType: _normalize_function,
    types.BuiltinFunctionType: _normalize_function,
    types.BuiltinMethodType: _normalize_function,
    type: _normalize_class,
}

_BASE_HANDLERS: tuple[tuple[type[Any], Callable[[Any, set[int]], Any]], ...] = (
    (enum.Enum, _normalize_enum),
    (Mapping, _normalize_mapping),
    (set, _normalize_set),
    (frozenset, _normalize_set),
    (tuple, _normalize_sequence),
    (list, _normalize_sequence),
    (Path, _normalize_path),
)


def _normalize(value: Any, active: set[int]) -> Any:
    """Return JSON-shaped, deterministic data for one module-level value."""

    if value is Ellipsis:
        return {"type": "ellipsis"}
    if value is None or isinstance(value, (bool, int, float)):
        return value
    if isinstance(value, str):
        return _stable_string(value)
    if normalized_typing := _normalize_typing(value, active):
        return normalized_typing
    if handler := _EXACT_HANDLERS.get(type(value)):
        return handler(value, active)
    for value_type, handler in _BASE_HANDLERS:
        if isinstance(value, value_type):
            return handler(value, active)
    if dataclasses.is_dataclass(value):
        return _normalize_dataclass(value, active)
    if inspect.isclass(value):
        return _normalize_class(value, active)
    if hasattr(value, "__dict__"):
        return _normalize_object(value, active)
    return _normalize_fallback(value, active)


def _load_root_initializer() -> types.ModuleType:
    """Execute the root package when the caller has its runtime dependencies."""

    path = ROOT / "__init__.py"
    spec = importlib.util.spec_from_file_location(
        ROOT_PACKAGE_NAME,
        path,
        submodule_search_locations=[str(ROOT)],
    )
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load package initializer from {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[ROOT_PACKAGE_NAME] = module
    spec.loader.exec_module(module)
    return module


def _path_to_import(path_text: str) -> str | None:
    path = Path(path_text)
    if path.suffix != ".py":
        return None
    path = (ROOT / path).resolve() if not path.is_absolute() else path.resolve()
    try:
        relative = path.relative_to(ROOT)
    except ValueError as exc:
        raise ValueError(f"module path is outside repository: {path_text}") from exc
    if relative.name == "__init__.py" and relative.parent == Path("."):
        return ""
    dotted = relative.with_suffix("").parts
    if dotted[-1] == "__init__":
        dotted = dotted[:-1]
    return ".".join(("ankiscape", *dotted))


def _load_module(module_path: str) -> types.ModuleType:
    """Import using the repository's alias, accepting dotted or ``.py`` input."""

    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    import pkg_alias  # noqa: F401  (installs the ankiscape package alias)

    import_name = _path_to_import(module_path)
    if import_name == "" or module_path == "ankiscape":
        return _load_root_initializer()
    if import_name is None:
        import_name = module_path if module_path.startswith("ankiscape.") else f"ankiscape.{module_path}"
    if import_name == "ankiscape.data.achievement_diary_catalog":
        # This generated catalog and its data model import each other.  The
        # repository's normal import order loads the model first, which makes
        # the cycle complete without changing either module's surface.
        importlib.import_module("ankiscape.data.achievement_diary_data")
    return importlib.import_module(import_name)


def dump_module(module_path: str) -> tuple[str, str]:
    module = _load_module(module_path)
    names = sorted(name for name in vars(module) if not name.startswith("_"))
    lines = [f"MODULE_SURFACE module={module.__name__}"]
    for name in names:
        lines.append(f"NAME {name} = {_json(_normalize(vars(module)[name], set()))}")
    dump = "\n".join(lines) + "\n"
    digest = hashlib.sha256(dump.encode("utf-8")).hexdigest()
    return dump, digest


def _emit_batch(module_paths: list[str]) -> int:
    """Emit isolated digest lines for a batch of side-effectful imports."""

    _print_environment()
    for module_path in module_paths:
        child = subprocess.run(
            [sys.executable, str(Path(__file__).resolve()), "--digest-only", module_path],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        if child.returncode:
            if child.stderr:
                sys.stderr.write(child.stderr)
            return child.returncode
        sys.stdout.write(child.stdout)
    return 0


def _reexec_with_stable_hash_seed() -> None:
    if os.environ.get("MODULE_SURFACE_STABLE_HASH") == "1":
        return
    environment = os.environ.copy()
    environment["PYTHONHASHSEED"] = "0"
    environment["MODULE_SURFACE_STABLE_HASH"] = "1"
    os.execve(sys.executable, [sys.executable, *sys.argv], environment)


def _print_environment() -> None:
    print(
        f"MODULE_SURFACE_ENV: python={platform.python_version()} hash_seed=0",
        file=sys.stderr,
    )


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=__doc__,
        epilog=(
            "Hash only the exact 'MODULE_SURFACE module=' header and 'NAME ' rows, "
            "including the final newline; exclude the 'MODULE_SURFACE_SHA256:' footer, "
            "and call dump_module() from Python instead of reparsing stdout."
        ),
    )
    parser.add_argument("modules", nargs="+", help="module import paths or repository .py paths")
    parser.add_argument(
        "--digest-only", "--digests", dest="digest_only", action="store_true",
        help="print one digest line per module; required for multi-module checks",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    _reexec_with_stable_hash_seed()
    args = _parser().parse_args(argv)
    if len(args.modules) > 1:
        return _emit_batch(args.modules)
    _print_environment()
    module_path = args.modules[0]
    try:
        dump, digest = dump_module(module_path)
    except (ImportError, ModuleNotFoundError, OSError, ValueError) as exc:
        print(f"module_surface: cannot import {module_path!r}: {exc}", file=sys.stderr)
        return 1
    if args.digest_only:
        print(f"MODULE_SURFACE_SHA256: {module_path} {digest}")
    else:
        sys.stdout.write(dump)
        print(f"MODULE_SURFACE_SHA256: {digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
