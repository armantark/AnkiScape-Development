"""Compare exact frozen and candidate unproductive review blocks after source guards."""

import argparse
import ast
import base64
import copy
import gzip
import hashlib
import json
import os
from pathlib import Path
import pickle
import sys
import textwrap
import types
from contextlib import ExitStack
from unittest.mock import patch

EVIDENCE = Path("memory-bank/evidence/unproductive-activity-selector-2026-09-08")
BASELINE = "6dacde5486c72e73ca170c039bf8207dec22ac81"


def source_guard(root, inventory, expected):
    raw = inventory.read_bytes()
    if hashlib.sha256(raw).hexdigest() != expected:
        raise ValueError("Inventory hash differs; product imports not started.")
    manifest = json.loads(gzip.decompress(raw))
    if manifest["baseline_commit"] != BASELINE:
        raise ValueError("Baseline differs; product imports not started.")
    for name, digest in manifest["files"].items():
        if hashlib.sha256((root / name).read_bytes()).hexdigest() != digest:
            raise ValueError(f"Source differs: {name}; product imports not started.")
    return manifest["files"]


def branch_source(source):
    function = next(node for node in ast.parse(source).body
                    if isinstance(node, ast.FunctionDef) and node.name == "on_answer_card")
    branches = [node for node in ast.walk(function) if isinstance(node, ast.If)
                and ast.unparse(node.test) == "review_answered and before_state is not None"]
    branch = next(node for node in branches
                  if ast.unparse(node.body[-1]) == "_advance_world_events_after_review()")
    lines = source.splitlines(keepends=True)
    return textwrap.dedent("".join(lines[branch.body[0].lineno - 1:branch.body[-1].end_lineno]))


def load_sources(root):
    import pkg_alias  # noqa: F401
    from ankiscape.runtime import runtime_actions as candidate

    frozen = types.ModuleType("ankiscape.runtime._frozen_unproductive_runtime_actions")
    frozen.__package__ = "ankiscape.runtime"
    original = gzip.decompress((root / EVIDENCE / "baseline-runtime-actions.py.gz").read_bytes())
    exec(compile(original, "<frozen-runtime-actions>", "exec"), frozen.__dict__)
    old_root = gzip.decompress((root / EVIDENCE / "baseline-entrypoint.py.gz").read_bytes()).decode()
    return (frozen, branch_source(old_root)), (candidate, branch_source((root / "__init__.py").read_text()))


def activity_rows(root):
    rows = json.loads((root / EVIDENCE / "selection-rows.json").read_text())
    result = []
    for activity, predicate, handler in rows:
        call = ast.parse(predicate, mode="eval").body
        if isinstance(call.func, ast.Attribute):
            view, field = call.func.value.func.id, call.args[0].value
        else:
            view, field = call.func.id, None
        result.append((activity, view, field, handler))
    return result


def cases(module, rows):
    for activity, view, field, handler in rows:
        for active in (False, True):
            player = {"current_utility": getattr(module, activity),
                      "troll_invasion": {"active": False} if active else {}}
            yield {"name": f"{activity}:{active}", "player": player, "key": "utility",
                   "active": active, "view": view, "field": field,
                   "handler": handler if active else None}
        if view != "bool":
            yield {"name": f"{activity}:predicate-error", "player": player, "key": "utility",
                   "active": True, "view": view, "field": field, "handler": None, "error": True}
    flash = module.FLASH_POWDER_FACTORY_ACTIVITY_ID
    for key in ("utility", "agility"):
        for state in ({flash: {"active": False}}, {flash: {}}, ["truthy non-dict"]):
            active = isinstance(state, dict) and bool(state.get(flash))
            yield {"name": f"flash:{key}:{state!r}", "key": key,
                   "player": {"current_" + key: flash, "agility_activity_state": state},
                   "active": active, "view": None, "field": None,
                   "handler": "handle_flash_powder_factory_answer" if active else None}
    for key, selection in (("utility", []), ("utility", "unknown"), ("other", flash), (None, flash)):
        yield {"name": f"no-match:{key}:{selection!r}", "key": key,
               "player": {"current_utility": selection}, "active": False,
               "view": None, "field": None, "handler": None}


def observed_view(name, field, fixture, events, player):
    def view(supplied):
        events.append(["view", name, supplied is player, copy.deepcopy(supplied)])
        if fixture.get("error"):
            raise ValueError("controlled predicate failure")
        result = {field: fixture["active"]} if field else fixture["active"]
        events.append(["view-result", name, copy.deepcopy(result)])
        return result
    return view


def observed_handler(name, events, player):
    def handler(ctx, *, productive):
        events.append(["handler", name, productive, ctx.player_data is player, copy.deepcopy(player)])
        player["handled_by"] = name
        return False
    return handler


def capture(module, source, rows, fixture):
    player, events = copy.deepcopy(fixture["player"]), []

    def context():
        events.append(["context", copy.deepcopy(player)])
        return types.SimpleNamespace(player_data=player)

    namespace = {"_state": types.SimpleNamespace(player_data=player, current_skill=fixture["key"]),
                 "runtime_actions": module, "review_action_handler_key": lambda skill: skill,
                 "_runtime_action_context": context,
                 "_show_exp": lambda xp: events.append(["xp", xp]),
                 "_advance_world_events_after_review": lambda: events.append(["world"])}
    body = "def run_branch():\n    context_xp = 7\n" + textwrap.indent(source, "    ") + "    return context_xp\n"
    exec(compile(body, "<exact-unproductive-review-block>", "exec"), namespace)
    with ExitStack() as patches:
        for _activity, view, field, handler in rows:
            if view != "bool":
                patches.enter_context(patch.object(module, view, observed_view(view, field, fixture, events, player)))
            patches.enter_context(patch.object(module, handler, observed_handler(handler, events, player)))
        patches.enter_context(patch.object(module, "handle_flash_powder_factory_answer",
                                          observed_handler("handle_flash_powder_factory_answer", events, player)))
        try:
            result, error = namespace["run_branch"](), None
        except Exception as failure:
            result, error = None, (type(failure).__name__, str(failure))
    return {"result": result, "error": error, "events": events, "player": player}


def route_observed(captured):
    events = captured["events"]
    return {"handlers": [event[1] for event in events if event[0] == "handler"],
            "views": [event[1] for event in events if event[0] == "view"],
            "contexts": sum(event[0] == "context" for event in events),
            "tail": [event for event in events if event[0] in {"xp", "world"}],
            "error": captured["error"]}


def expected_route(fixture):
    view = fixture["view"]
    return {"handlers": [fixture["handler"]] if fixture["handler"] else [],
            "views": [view] if view not in {None, "bool"} else [],
            "contexts": int(fixture["handler"] is not None),
            "tail": [] if fixture.get("error") else [["xp", 7], ["world"]],
            "error": ("ValueError", "controlled predicate failure") if fixture.get("error") else None}


def compare(root):
    baseline, candidate = load_sources(root)
    rows, results = activity_rows(root), []
    for fixture in cases(candidate[0], rows):
        before = capture(*baseline, rows, fixture)
        after = capture(*candidate, rows, fixture)
        before_bytes, after_bytes = pickle.dumps(before, protocol=4), pickle.dumps(after, protocol=4)
        expected = expected_route(fixture)
        observed = route_observed(after)
        results.append({"case": fixture["name"], "equal": before == after,
                        "pickle_bytes_equal": before_bytes == after_bytes,
                        "route_pass": observed == expected == route_observed(before),
                        "expected": expected, "observed": observed,
                        "baseline_pickle_base64": base64.b64encode(before_bytes).decode(),
                        "candidate_pickle_base64": base64.b64encode(after_bytes).decode()})
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inventory", type=Path, required=True)
    parser.add_argument("--inventory-sha256", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--preflight", action="store_true")
    args = parser.parse_args()
    if sys.flags.optimize or "PYTHONOPTIMIZE" in os.environ:
        raise SystemExit("Optimized interpreter refused; product imports not started.")
    root = Path(__file__).resolve().parents[2]
    sources = source_guard(root, args.inventory, args.inventory_sha256)
    report = {"baseline_commit": BASELINE, "inventory_sha256": args.inventory_sha256,
              "sources_before": sources}
    if args.preflight:
        imported = [name for name in sys.modules if name.split(".")[0] in {"ankiscape", "pkg_alias", "tests"}]
        if imported:
            raise RuntimeError(f"Product modules already loaded: {imported}")
        report.update(status="PREFLIGHT_PASS", product_imported=False)
    else:
        sys.path.insert(0, str(root))
        rows = compare(root)
        passed = all(row["equal"] and row["pickle_bytes_equal"] and row["route_pass"] for row in rows)
        report.update(cases=rows, status="PASS" if passed else "FAIL")
    report["sources_after"] = source_guard(root, args.inventory, args.inventory_sha256)
    args.output.write_bytes(gzip.compress((json.dumps(report, indent=2) + "\n").encode(), mtime=0))
    if report["status"] == "FAIL":
        raise SystemExit("Differential output or route proof failed.")


if __name__ == "__main__":
    main()
