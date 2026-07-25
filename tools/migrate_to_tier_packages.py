#!/usr/bin/env python3
"""Move the 176 flat AnkiScape modules into six tier packages, in place.

Phases (idempotent; re-running after a partial or complete run is safe):
  1. create the tier package directories (with marker __init__.py files),
     write the top-level ``pkg_alias.py`` bootstrap, and ``git mv`` each flat
     module into its bucket;
  2. apply the explicit per-file fixups (``__file__``-relative paths that now
     live one directory deeper, generator output paths, and the handful of
     tests that load add-on files by path);
  3. rewrite imports everywhere with AST-guided line surgery:
     - add-on modules: every ``from .x import y`` becomes package-relative to
       the new location, and every ``try: relative / except: flat`` dual-import
       block collapses to the single relative form;
     - tests and tools: flat imports of moved modules become
       ``from ankiscape.<bucket>.<module> import ...`` through the alias
       installed by ``pkg_alias.py`` (inserted as each file's first import);
     - tests additionally get their string module references rewritten
       (``mock.patch("x_logic.f")`` targets and ``sys.modules["pkg.x"]`` keys);
  4. audit: re-parse every file and fail loudly if any flat or stale-relative
     reference to a moved module survives.

The file -> bucket mapping is explicit data (BUCKETS below), not inference.
Run with --dry-run to see the planned actions without touching the tree.
"""

from __future__ import annotations

import argparse
import ast
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

ALIAS = "ankiscape"

# ---------------------------------------------------------------------------
# The owner-decided mapping. __init__.py and run_tests.py stay at top level.
#
# Loose-file bucketing decisions (the files with no <feature>_data/_logic
# name): pure logic goes to logic/, pure data to data/.
#   logic/: agility_travel (pure run-energy/weight transactions),
#           cadence_coverage, cadence_kernel, cadence_live, cadence_shadow
#           (the pure cadence engine, declarations, telemetry and audit
#           catalog - functions, not tables), combat_session (pure risk
#           fingerprints plus a process-local confirmation set),
#           inventory_pure (pure carried-inventory helpers; not part of the
#           logic_pure* naming family), shop_fixtures (computes fixture view
#           models by exercising shop_logic - behavior, not tables),
#           slayer_readiness (pure completeness checks).
#   data/:  item_values (a value/stackable/exchangeable lookup table merged
#           from shop_data and the generated cache dump; consumed as data).
# ---------------------------------------------------------------------------
BUCKETS: dict[str, tuple[str, ...]] = {
    "data": (
        "agility_data",
        "barbarian_assault_data",
        "barrows_data",
        "big_chinchompa_data",
        "castle_wars_data",
        "circus_data",
        "combat_data",
        "construction_data",
        "cooking_data",
        "court_cases_data",
        "crafting_data",
        "dungeoneering_data",
        "equipment_condition_data",
        "equipment_data",
        "evil_tree_data",
        "farming_data",
        "fight_caves_data",
        "firemaking_data",
        "fish_flingers_data",
        "fishing_data",
        "fishing_trawler_data",
        "fist_of_guthix_data",
        "flash_powder_factory_data",
        "fletching_data",
        "gnome_ball_data",
        "grand_exchange_data",
        "great_orb_project_data",
        "herblore_data",
        "hunter_data",
        "item_values",
        "livid_farm_data",
        "magic_data",
        "managing_miscellania_data",
        "mining_data",
        "pack_data",
        "penguin_hide_and_seek_data",
        "pest_control_data",
        "pet_data",
        "phoenix_lair_data",
        "potion_data",
        "prayer_data",
        "prayer_passive_data",
        "pyramid_plunder_data",
        "quest_data",
        "runecrafting_data",
        "shades_of_mortton_data",
        "shooting_star_data",
        "shop_data",
        "slayer_data",
        "smithing_data",
        "sorceress_garden_data",
        "soul_wars_data",
        "stealing_creation_data",
        "stronghold_of_security_data",
        "stronghold_player_safety_data",
        "summoning_data",
        "thieving_data",
        "trouble_brewing_data",
        "tzhaar_fight_pit_data",
        "urn_data",
        "varrock_museum_data",
        "vinesweeper_data",
        "warriors_guild_data",
        "werewolf_skullball_data",
        "woodcutting_data",
    ),
    "logic": (
        "agility_logic",
        "agility_travel",
        "barbarian_assault_logic",
        "barrows_logic",
        "big_chinchompa_logic",
        "cadence_coverage",
        "cadence_kernel",
        "cadence_live",
        "cadence_shadow",
        "castle_wars_logic",
        "circus_logic",
        "combat_session",
        "court_cases_logic",
        "dungeoneering_logic",
        "equipment_instance_logic",
        "evil_tree_logic",
        "farming_logic",
        "fight_caves_logic",
        "fish_flingers_logic",
        "fishing_trawler_logic",
        "fist_of_guthix_logic",
        "flash_powder_factory_logic",
        "gnome_ball_logic",
        "grand_exchange_logic",
        "great_orb_project_logic",
        "inventory_pure",
        "livid_farm_logic",
        "managing_miscellania_logic",
        "penguin_hide_and_seek_logic",
        "pest_control_logic",
        "pet_logic",
        "phoenix_lair_logic",
        "pyramid_plunder_logic",
        "shades_of_mortton_logic",
        "shooting_star_logic",
        "shop_fixtures",
        "shop_logic",
        "slayer_logic",
        "slayer_readiness",
        "sorceress_garden_logic",
        "soul_wars_logic",
        "stealing_creation_logic",
        "stronghold_player_safety_logic",
        "summoning_logic",
        "trouble_brewing_logic",
        "tzhaar_fight_pit_logic",
        "varrock_museum_logic",
        "vinesweeper_logic",
        "warriors_guild_logic",
        "werewolf_skullball_logic",
        "wicked_hood_logic",
        "world_population_logic",
    ),
    "logic_pure": (
        "logic_pure",
        "logic_pure_claims",
        "logic_pure_combat_engine",
        "logic_pure_combat_model",
        "logic_pure_combat_supplies",
        "logic_pure_construction",
        "logic_pure_consumables",
        "logic_pure_equipment",
        "logic_pure_gathering",
        "logic_pure_landmarks",
        "logic_pure_magic",
        "logic_pure_prayer",
        "logic_pure_production",
        "logic_pure_progression",
        "logic_pure_quest",
        "logic_pure_runecrafting",
        "logic_pure_smithing",
        "logic_pure_state",
        "logic_pure_telemetry",
        "logic_pure_thieving",
        "logic_pure_urns",
    ),
    "runtime": (
        "runtime_actions",
        "runtime_actions_activities",
        "runtime_actions_carried",
        "runtime_actions_combat",
        "runtime_actions_context",
        "runtime_actions_gates",
        "runtime_actions_gathering",
        "runtime_actions_magic",
        "runtime_actions_production",
        "runtime_actions_shared",
        "runtime_actions_thieving",
        "runtime_actions_utility",
    ),
    "ui": (
        "ui",
        "ui_menu_ctx",
        "ui_tab_achievements",
        "ui_tab_quests",
        "ui_tab_shop",
    ),
    "core": (
        "achievement_metadata",
        "action_registry",
        "constants",
        "debug",
        "help_system",
        "hooks",
        "injectors",
        "item_registry",
        "logic",
        "review_context",
        "skill_hub",
        "skill_registry",
        "storage",
        "storage_pure",
        "target_metadata",
        "utils",
    ),
    "generated": (
        "grand_exchange_period_generated",
        "item_values_generated",
        "pet_data_generated",
        "quest_catalog_generated",
        "summoning_data_generated",
    ),
}

BUCKET_OF: dict[str, str] = {
    module: bucket for bucket, modules in BUCKETS.items() for module in modules
}

# Top-level subpackages/directories that add-on modules may import relatively
# and that do NOT move (``from .tools.sourced_xp_rates import ...``).
STAY_SUBPACKAGES = frozenset({"tools"})

PKG_ALIAS_SOURCE = '''"""Install the stable ``ankiscape`` package alias for tests and tools.

Anki imports this directory as a package named after the folder it sits in
(``ankiscape_fork``, a worktree name, an add-on id...), so that name cannot be
written in an import statement. Tests and tools instead import the add-on
through the stable alias package ``ankiscape``: importing this module binds
``ankiscape`` in ``sys.modules`` to this directory WITHOUT executing the
add-on's __init__.py (which needs aqt). Submodule imports such as
``from ankiscape.logic.farming_logic import ...`` then resolve normally, and
the package-relative imports inside those modules work unchanged.
"""

import os
import sys
import types

PACKAGE_ALIAS = "ankiscape"
_ROOT = os.path.dirname(os.path.abspath(__file__))


def install_package_alias() -> None:
    if PACKAGE_ALIAS in sys.modules:
        return
    package = types.ModuleType(PACKAGE_ALIAS)
    package.__path__ = [_ROOT]  # type: ignore[attr-defined]
    package.__package__ = PACKAGE_ALIAS
    sys.modules[PACKAGE_ALIAS] = package


install_package_alias()
'''

BOOTSTRAP_IMPORT = "import pkg_alias  # noqa: F401  (installs the ankiscape package alias)"

# ---------------------------------------------------------------------------
# Explicit per-file fixups: strings that the AST import rewriter cannot see.
# Each entry is (path relative to ROOT after the move, old, new). Idempotent:
# a file already containing `new` is skipped; otherwise `old` must occur
# exactly once.
# ---------------------------------------------------------------------------
FIXUPS: tuple[tuple[str, str, str], ...] = (
    # Moved modules that located the add-on root via __file__: they now live
    # one directory deeper.
    (
        "data/agility_data.py",
        "_ROOT = Path(__file__).resolve().parent",
        "_ROOT = Path(__file__).resolve().parents[1]",
    ),
    (
        "data/thieving_data.py",
        "_ROOT = Path(__file__).resolve().parent",
        "_ROOT = Path(__file__).resolve().parents[1]",
    ),
    (
        "core/constants.py",
        "current_dir = os.path.dirname(os.path.abspath(__file__))",
        "current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))",
    ),
    (
        "core/debug.py",
        'DEBUG_LOG_FILE = os.path.join(os.path.dirname(__file__), "ankiscape_debug.log")',
        'DEBUG_LOG_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "ankiscape_debug.log")',
    ),
    (
        "core/help_system.py",
        'HELP_TOPICS_DIR = Path(__file__).with_name("help_topics")',
        'HELP_TOPICS_DIR = Path(__file__).resolve().parents[1] / "help_topics"',
    ),
    (
        "core/injectors.py",
        'icon_path = os.path.join(os.path.dirname(__file__), "icon", "stats_icon.png")',
        'icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "icon", "stats_icon.png")',
    ),
    # injectors resolves the add-on package to call its _on_main_menu; its
    # __package__ is now "<addon>.core", one level below the add-on package.
    (
        "core/injectors.py",
        "pkg = sys.modules.get(__package__)",
        'pkg = sys.modules.get(__package__.rpartition(".")[0])',
    ),
    (
        "ui/ui.py",
        'base = os.path.join(os.path.dirname(__file__), "ankiscape_debug.log")',
        'base = os.path.join(os.path.dirname(os.path.dirname(__file__)), "ankiscape_debug.log")',
    ),
    (
        "ui/ui.py",
        "root = os.path.dirname(os.path.abspath(__file__))",
        "root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))",
    ),
    # Tests that read or load add-on files by path.
    (
        "tests/test_agility.py",
        'for filename in ("agility_data.py", "agility_logic.py", "agility_travel.py"):',
        'for filename in ("data/agility_data.py", "logic/agility_logic.py", "logic/agility_travel.py"):',
    ),
    (
        "tests/test_storage_runtime.py",
        'f"{package_name}.storage",',
        'f"{package_name}.core.storage",',
    ),
    (
        "tests/test_storage_runtime.py",
        'root / "storage.py",',
        'root / "core" / "storage.py",',
    ),
    (
        "tests/test_generated_skill_data.py",
        '(ROOT / "smithing_data.py").read_text',
        '(ROOT / "data" / "smithing_data.py").read_text',
    ),
    (
        "tests/test_generated_skill_data.py",
        '(ROOT / "equipment_data.py").read_text',
        '(ROOT / "data" / "equipment_data.py").read_text',
    ),
    (
        "tests/test_shop_data.py",
        'repo_root / "shop_data.py",',
        'repo_root / "data" / "shop_data.py",',
    ),
    # This attribute chain relied on the flat submodule import setting
    # "farming_logic" directly on the add-on package.
    (
        "tests/test_integration_smoke.py",
        "state.update(addon.farming_logic.default_farming_state_pure())",
        "state.update(addon.logic.farming_logic.default_farming_state_pure())",
    ),
    # The gate keys its direct-call table by flat module name and generates
    # test method names from it; module __name__ is now package-qualified, so
    # use the basename to keep the historical test ids stable.
    (
        "tests/test_logic_no_input_mutation.py",
        "direct = _DIRECT_CALLS.get(module.__name__, ())",
        'direct = _DIRECT_CALLS.get(module.__name__.rpartition(".")[2], ())',
    ),
    (
        "tests/test_logic_no_input_mutation.py",
        'f"test_{_module.__name__}_does_not_mutate_input",',
        "f\"test_{_module.__name__.rpartition('.')[2]}_does_not_mutate_input\",",
    ),
    # Generators that write moved modules back into the repo.
    (
        "tools/build_pre_eoc_quest_catalog.py",
        'OUTPUT_PATH = ROOT / "quest_catalog_generated.py"',
        'OUTPUT_PATH = ROOT / "generated" / "quest_catalog_generated.py"',
    ),
    (
        "tools/generate_construction_data.py",
        '(ROOT / "construction_data.py").write_text',
        '(ROOT / "data" / "construction_data.py").write_text',
    ),
    (
        "tools/generate_equipment_data.py",
        'default=Path(__file__).resolve().parents[1] / "equipment_data.py"',
        'default=Path(__file__).resolve().parents[1] / "data" / "equipment_data.py"',
    ),
    (
        "tools/generate_npc_shop_data.py",
        'SHOP_DATA_PATH = REPO_ROOT / "shop_data.py"',
        'SHOP_DATA_PATH = REPO_ROOT / "data" / "shop_data.py"',
    ),
    (
        "tools/generate_npc_shop_data.py",
        'runpy.run_path(str(REPO_ROOT / "summoning_data_generated.py"))',
        'runpy.run_path(str(REPO_ROOT / "generated" / "summoning_data_generated.py"))',
    ),
    (
        "tools/generate_pet_catalog.py",
        'OUTPUT = ROOT / "pet_data_generated.py"',
        'OUTPUT = ROOT / "generated" / "pet_data_generated.py"',
    ),
    (
        "tools/generate_smithing_data.py",
        'default=Path(__file__).resolve().parents[1] / "smithing_data.py"',
        'default=Path(__file__).resolve().parents[1] / "data" / "smithing_data.py"',
    ),
    (
        "tools/generate_summoning_catalog.py",
        'OUTPUT = ROOT / "summoning_data_generated.py"',
        'OUTPUT = ROOT / "generated" / "summoning_data_generated.py"',
    ),
)


def run_git(*args: str) -> None:
    subprocess.run(["git", "-C", str(ROOT), *args], check=True)


# ---------------------------------------------------------------------------
# Import statement rewriting
# ---------------------------------------------------------------------------

_REL_HEAD_RE = re.compile(r"^(\s*)from\s+(\.+)\s*([A-Za-z_][\w.]*)\s+import\b")
_FLAT_HEAD_RE = re.compile(r"^(\s*)from\s+([A-Za-z_][\w.]*)\s+import\b")
_DOT_ONLY_RE = re.compile(r"^(\s*)from\s+(\.+)\s+import\s+(.*?)(\s*#.*)?$")


def _split_comment(line: str) -> str:
    """Trailing comment of a single-line statement (including leading spaces)."""
    m = _DOT_ONLY_RE.match(line)
    return m.group(4) or "" if m else ""


class FileRewriter:
    """AST-guided line surgery for one file."""

    def __init__(self, path: Path, kind: str):
        # kind: "top" (stays at top level), "bucket" (moved one level down),
        # "external" (tests/ and tools/: imports via the alias package)
        self.path = path
        self.kind = kind
        self.text = path.read_text(encoding="utf-8")
        self.lines = self.text.splitlines(keepends=True)
        self.tree = ast.parse(self.text)
        # (start_line, end_line, replacement_lines) with 1-based inclusive rows
        self.edits: list[tuple[int, int, list[str]]] = []
        self.consumed: set[int] = set()  # linenos of import nodes already handled
        self.changed_flat_import = False

    # -- helpers ------------------------------------------------------------

    def _stmt_lines(self, node: ast.stmt) -> list[str]:
        return [self.lines[i] for i in range(node.lineno - 1, node.end_lineno)]

    @staticmethod
    def _dedent(lines: list[str], amount: int) -> list[str]:
        pad = " " * amount
        return [ln[amount:] if ln.startswith(pad) else ln.lstrip() if ln.strip() else ln for ln in lines]

    def _new_rel_prefix(self, node: ast.ImportFrom) -> str | None:
        """New module path for a level-1 relative import, or None to keep."""
        target_module = node.module or ""
        parts = target_module.split(".")
        first = parts[0]
        up = "." if self.kind == "top" else ".."
        if len(parts) > 1 and first in BUCKETS:
            return None  # already package-qualified (idempotent re-run)
        if first in BUCKET_OF:
            # Ambiguity guard for re-runs at top level: "ui", "logic" and
            # "logic_pure" are both moved modules and bucket names. A
            # single-segment import whose names are all modules of that
            # bucket is the already-rewritten form.
            if (
                len(parts) == 1
                and first in BUCKETS
                and all(alias.name in BUCKETS[first] for alias in node.names)
            ):
                return None
            return f"{up}{BUCKET_OF[first]}.{target_module}"
        if self.kind == "top":
            return None  # e.g. from .tools.x import y in __init__: unchanged
        return f"{up}{target_module}"  # e.g. from ..tools.x import y

    def _rewrite_importfrom_lines(self, node: ast.ImportFrom) -> list[str] | None:
        """Rewritten source lines for a relative/flat ImportFrom, or None."""
        stmt = self._stmt_lines(node)
        if node.level == 1 and node.module is not None:
            new_mod = self._new_rel_prefix(node)
            if new_mod is None:
                return None
            head = _REL_HEAD_RE.match(stmt[0])
            if not head:
                raise RuntimeError(f"{self.path}:{node.lineno}: unparseable relative import head")
            stmt[0] = _REL_HEAD_RE.sub(rf"\g<1>from {new_mod} import", stmt[0], count=1)
            return stmt
        if node.level == 1 and node.module is None:
            # from . import a, b [as c]
            comment = _split_comment(stmt[0].rstrip("\n"))
            indent = stmt[0][: len(stmt[0]) - len(stmt[0].lstrip())]
            up = "." if self.kind == "top" else ".."
            out: list[str] = []
            for alias in node.names:
                first = alias.name.split(".")[0]
                if first in BUCKET_OF:
                    src = f"{up}{BUCKET_OF[first]}"
                else:
                    src = up
                as_clause = f" as {alias.asname}" if alias.asname else ""
                out.append(f"{indent}from {src} import {alias.name}{as_clause}")
            out[0] += comment
            return [ln + "\n" for ln in out]
        if node.level == 0 and self.kind == "external" and "." in (node.module or ""):
            # Synthetic add-on packages in tests, e.g.
            # "from ankiscape_evil_tree_clock_integration.evil_tree_logic
            # import ..." after _load_addon_as_package: insert the bucket
            # before the moved module segment.
            parts = node.module.split(".")
            for i in range(1, len(parts)):
                if parts[i] not in BUCKET_OF:
                    continue
                # already bucket-qualified: "<pkg>.<bucket>.<module>" (watch
                # for names like "logic"/"ui" that are both moved modules and
                # bucket names)
                if parts[i - 1] in BUCKETS and parts[i] in BUCKETS[parts[i - 1]]:
                    break
                if (
                    parts[i] in BUCKETS
                    and i + 1 < len(parts)
                    and parts[i + 1] in BUCKETS[parts[i]]
                ):
                    continue  # this segment IS the bucket of the next one
                if (
                    i == len(parts) - 1
                    and parts[i] in BUCKETS
                    and all(a.name in BUCKETS[parts[i]] for a in node.names)
                ):
                    break  # "from <pkg>.<bucket> import <module>" form
                new_parts = parts[:i] + [BUCKET_OF[parts[i]]] + parts[i:]
                new_mod = ".".join(new_parts)
                stmt[0] = _FLAT_HEAD_RE.sub(
                    rf"\g<1>from {new_mod} import", stmt[0], count=1
                )
                return stmt
        if node.level == 0:
            first = (node.module or "").split(".")[0]
            if first in BUCKET_OF:
                if self.kind == "external":
                    new_mod = f"{ALIAS}.{BUCKET_OF[first]}.{node.module}"
                    self.changed_flat_import = True
                else:
                    # a bare flat import inside an add-on module (outside any
                    # dual-import block, e.g. a lazy function-level import)
                    up = "." if self.kind == "top" else ".."
                    new_mod = f"{up}{BUCKET_OF[first]}.{node.module}"
                stmt[0] = _FLAT_HEAD_RE.sub(rf"\g<1>from {new_mod} import", stmt[0], count=1)
                return stmt
        return None

    def _rewrite_import_lines(self, node: ast.Import) -> list[str] | None:
        """Rewrite `import x[, y]` statements that name moved modules."""
        if not any(alias.name.split(".")[0] in BUCKET_OF for alias in node.names):
            return None
        for alias in node.names:
            if "." in alias.name and alias.name.split(".")[0] in BUCKET_OF:
                raise RuntimeError(f"{self.path}:{node.lineno}: dotted import of moved module")
        stmt = self._stmt_lines(node)
        raw = stmt[0].rstrip("\n")
        comment = "  " + raw[raw.index("#"):].strip() if "#" in raw else ""
        indent = stmt[0][: len(stmt[0]) - len(stmt[0].lstrip())]
        out: list[str] = []
        keep: list[str] = []
        for alias in node.names:
            first = alias.name.split(".")[0]
            if first in BUCKET_OF:
                if self.kind == "external":
                    src = f"{ALIAS}.{BUCKET_OF[first]}"
                else:
                    up = "." if self.kind == "top" else ".."
                    src = f"{up}{BUCKET_OF[first]}"
                as_clause = f" as {alias.asname}" if alias.asname else ""
                out.append(f"{indent}from {src} import {alias.name}{as_clause}")
                self.changed_flat_import = self.kind == "external" or self.changed_flat_import
            else:
                as_clause = f" as {alias.asname}" if alias.asname else ""
                keep.append(f"{indent}import {alias.name}{as_clause}")
        lines = keep + out
        if comment and lines:
            lines[0] += comment
        return [ln + "\n" for ln in lines]

    # -- dual-import try/except collapse (add-on modules only) ---------------

    @staticmethod
    def _catches_import_error(handler: ast.ExceptHandler) -> bool:
        t = handler.type
        if t is None:
            return True
        names = [t.id] if isinstance(t, ast.Name) else [
            e.id for e in t.elts if isinstance(e, ast.Name)
        ] if isinstance(t, ast.Tuple) else []
        return any(n in ("ImportError", "ModuleNotFoundError", "Exception") for n in names)

    @staticmethod
    def _is_flat_addon_import(stmt: ast.stmt) -> bool:
        if isinstance(stmt, ast.ImportFrom) and stmt.level == 0:
            first = (stmt.module or "").split(".")[0]
            return first in BUCKET_OF or first in STAY_SUBPACKAGES
        if isinstance(stmt, ast.Import):
            return all(a.name.split(".")[0] in BUCKET_OF for a in stmt.names)
        return False

    def _try_collapse(self, node: ast.Try) -> bool:
        if self.kind == "external":
            return False
        if node.orelse or node.finalbody or len(node.handlers) != 1:
            return False
        handler = node.handlers[0]
        if not self._catches_import_error(handler):
            return False
        if not all(isinstance(s, ast.ImportFrom) and s.level >= 1 for s in node.body):
            return False
        try_indent = node.col_offset
        body_indent = node.body[0].col_offset
        delta = body_indent - try_indent

        def rewritten_body() -> list[str]:
            out: list[str] = []
            try_line = self.lines[node.lineno - 1]
            trailing = try_line.split(":", 1)[1].strip()
            if trailing.startswith("#"):
                out.append(" " * try_indent + trailing + "\n")
            start = node.body[0].lineno
            end = node.body[-1].end_lineno
            pieces: list[str] = []
            covered: set[int] = set()
            for stmt in node.body:
                assert isinstance(stmt, ast.ImportFrom)
                repl = self._rewrite_importfrom_lines(stmt) or self._stmt_lines(stmt)
                for i in range(stmt.lineno, stmt.end_lineno + 1):
                    covered.add(i)
                pieces.append((stmt.lineno, repl))
            # keep interior comment lines between statements
            merged: list[str] = []
            i = start
            idx = 0
            while i <= end:
                if idx < len(pieces) and pieces[idx][0] == i:
                    merged.extend(pieces[idx][1])
                    # skip past this statement's lines
                    stmt = node.body[idx]
                    i = stmt.end_lineno + 1
                    idx += 1
                else:
                    merged.append(self.lines[i - 1])
                    i += 1
            out.extend(self._dedent(merged, delta))
            return out

        # Case 1: handler body is entirely flat add-on imports -> collapse.
        if all(self._is_flat_addon_import(s) for s in handler.body):
            for stmt in ast.walk(node):
                if isinstance(stmt, (ast.Import, ast.ImportFrom)):
                    self.consumed.add(stmt.lineno)
            self.edits.append((node.lineno, node.end_lineno, rewritten_body()))
            return True

        # Case 2: handler body is exactly one nested Try whose own body is
        # flat add-on imports (the "dump may be missing" pattern). Keep the
        # outer try/except, drop the flat middle layer, promote the nested
        # handler's fallback body.
        if (
            len(handler.body) == 1
            and isinstance(handler.body[0], ast.Try)
            and not handler.body[0].orelse
            and not handler.body[0].finalbody
            and len(handler.body[0].handlers) == 1
            and all(self._is_flat_addon_import(s) for s in handler.body[0].body)
        ):
            inner = handler.body[0]
            inner_handler = inner.handlers[0]
            for stmt in ast.walk(inner):
                if isinstance(stmt, (ast.Import, ast.ImportFrom)):
                    self.consumed.add(stmt.lineno)
            fallback_start = inner_handler.body[0].lineno
            fallback_end = inner.end_lineno
            fallback = self._dedent(
                [self.lines[i - 1] for i in range(fallback_start, fallback_end + 1)],
                inner_handler.body[0].col_offset - handler.body[0].col_offset,
            )
            # carry the inner except's explanatory comment onto the outer one
            outer_except_line = self.lines[handler.lineno - 1]
            inner_except_line = self.lines[inner_handler.lineno - 1]
            if "#" in inner_except_line and "#" not in outer_except_line:
                comment = inner_except_line[inner_except_line.index("#"):].rstrip("\n")
                self.edits.append(
                    (handler.lineno, handler.lineno,
                     [outer_except_line.rstrip("\n") + "  " + comment + "\n"])
                )
            self.edits.append((inner.lineno, inner.end_lineno, fallback))
            return True
        return False

    # -- driver ---------------------------------------------------------------

    def rewrite(self) -> bool:
        for node in ast.walk(self.tree):
            if isinstance(node, ast.Try):
                self._try_collapse(node)
        for node in ast.walk(self.tree):
            if isinstance(node, ast.ImportFrom) and node.lineno not in self.consumed:
                repl = self._rewrite_importfrom_lines(node)
                if repl is not None:
                    self.edits.append((node.lineno, node.end_lineno, repl))
            elif isinstance(node, ast.Import) and node.lineno not in self.consumed:
                repl = self._rewrite_import_lines(node)
                if repl is not None:
                    self.edits.append((node.lineno, node.end_lineno, repl))
        if not self.edits:
            return False
        for start, end, repl in sorted(self.edits, key=lambda e: e[0], reverse=True):
            self.lines[start - 1 : end] = repl
        self.text = "".join(self.lines)
        return True


# ---------------------------------------------------------------------------
# Test-file string rewriting (mock.patch targets and sys.modules keys)
# ---------------------------------------------------------------------------

_MODULE_ALTERNATION = "|".join(sorted(BUCKET_OF, key=len, reverse=True))

# "farming_logic.apply_x" -> "ankiscape.logic.farming_logic.apply_x"
_PATCH_TARGET_RE = re.compile(
    rf"""(["'])({_MODULE_ALTERNATION})\.(?!py["'])([A-Za-z_][\w.]*)\1"""
)

# "...package_prefix.farming_logic" / f"{addon.__name__}.farming_logic"
# -> insert the bucket before the trailing module name.
_DOTTED_SUFFIX_RE = re.compile(rf"""\.({_MODULE_ALTERNATION})(["'])""")
_BUCKET_TAILS = tuple(f".{bucket}" for bucket in BUCKETS)


def rewrite_test_strings(text: str) -> str:
    def patch_repl(m: re.Match[str]) -> str:
        quote, module, attr = m.group(1), m.group(2), m.group(3)
        return f"{quote}{ALIAS}.{BUCKET_OF[module]}.{module}.{attr}{quote}"

    text = _PATCH_TARGET_RE.sub(patch_repl, text)

    def suffix_repl(m: re.Match[str]) -> str:
        module, quote = m.group(1), m.group(2)
        prefix = m.string[: m.start()]
        if prefix.endswith(_BUCKET_TAILS) or prefix.endswith(ALIAS):
            return m.group(0)  # already rewritten
        # Only touch dynamic add-on package names: an f-string interpolation
        # ("f\"{addon.__name__}.farming_logic\"") or a literal synthetic
        # package name ("ankiscape_garden_undo_integration.sorceress_..."),
        # never unrelated dotted names like "anki.hooks".
        quote_pos = max(prefix.rfind('"'), prefix.rfind("'"))
        string_head = prefix[quote_pos + 1 :]
        if not (string_head.endswith("}") or string_head.startswith("ankiscape")):
            return m.group(0)
        return f".{BUCKET_OF[module]}.{module}{quote}"

    return _DOTTED_SUFFIX_RE.sub(suffix_repl, text)


def insert_bootstrap_import(text: str, tree: ast.Module) -> str:
    """Add the pkg_alias import immediately before the first top-level
    statement that mentions the alias package.

    Tools set up sys.path themselves before importing add-on modules, so the
    bootstrap must go right before the first alias use, not before their
    stdlib imports.
    """
    if re.search(r"^import pkg_alias\b", text, re.MULTILINE):
        return text
    lines = text.splitlines(keepends=True)
    insert_at = None
    for index, node in enumerate(tree.body):
        if index == 0 and isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant):
            continue  # module docstring
        start = node.lineno
        decorators = getattr(node, "decorator_list", None)
        if decorators:
            start = min(start, decorators[0].lineno)
        segment = "".join(lines[start - 1 : node.end_lineno])
        if f"{ALIAS}." in segment:
            insert_at = start - 1
            break
    if insert_at is None:
        for node in tree.body:
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                insert_at = node.lineno - 1
                break
    if insert_at is None:
        insert_at = 0
        for node in tree.body:
            if isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant):
                insert_at = node.end_lineno  # after the module docstring
            break
    lines.insert(insert_at, BOOTSTRAP_IMPORT + "\n")
    return "".join(lines)


# ---------------------------------------------------------------------------
# Phases
# ---------------------------------------------------------------------------

def phase_move(dry_run: bool) -> None:
    for bucket in BUCKETS:
        bucket_dir = ROOT / bucket
        marker = bucket_dir / "__init__.py"
        if not marker.exists():
            print(f"create {bucket}/__init__.py")
            if not dry_run:
                bucket_dir.mkdir(exist_ok=True)
                marker.write_text(f'"""AnkiScape tier package: {bucket}."""\n', encoding="utf-8")
                run_git("add", str(marker))
    alias_path = ROOT / "pkg_alias.py"
    if alias_path.read_text(encoding="utf-8") != PKG_ALIAS_SOURCE if alias_path.exists() else True:
        print("write pkg_alias.py")
        if not dry_run:
            alias_path.write_text(PKG_ALIAS_SOURCE, encoding="utf-8")
            run_git("add", str(alias_path))
    for module, bucket in sorted(BUCKET_OF.items()):
        src = ROOT / f"{module}.py"
        dst = ROOT / bucket / f"{module}.py"
        if src.exists():
            print(f"git mv {module}.py {bucket}/{module}.py")
            if not dry_run:
                run_git("mv", f"{module}.py", f"{bucket}/{module}.py")
        elif not dst.exists():
            raise RuntimeError(f"{module}.py is neither flat nor moved")


def resolve(rel: str) -> Path:
    """Path of a (possibly not yet moved) file, so --dry-run works pre-move."""
    path = ROOT / rel
    if not path.exists() and "/" in rel:
        flat = ROOT / rel.rsplit("/", 1)[1]
        if flat.exists():
            return flat
    return path


def phase_fixups(dry_run: bool) -> None:
    for rel, old, new in FIXUPS:
        path = resolve(rel)
        text = path.read_text(encoding="utf-8")
        if new in text:
            continue
        count = text.count(old)
        if count != 1:
            raise RuntimeError(f"fixup anchor not unique ({count}x) in {rel}: {old!r}")
        print(f"fixup {rel}: {old[:60]!r}")
        if not dry_run:
            path.write_text(text.replace(old, new, 1), encoding="utf-8")


def iter_rewrite_targets():
    yield ROOT / "__init__.py", "top"
    for bucket, modules in BUCKETS.items():
        for module in modules:
            yield resolve(f"{bucket}/{module}.py"), "bucket"
    for path in sorted((ROOT / "tests").glob("*.py")):
        yield path, "external"
    for path in sorted((ROOT / "tools").glob("*.py")):
        if path.name != "migrate_to_tier_packages.py":
            yield path, "external"


def phase_rewrite(dry_run: bool) -> None:
    for path, kind in iter_rewrite_targets():
        rewriter = FileRewriter(path, kind)
        changed = rewriter.rewrite()
        text = rewriter.text
        if kind == "external" and path.parent.name == "tests":
            new_text = rewrite_test_strings(text)
            changed = changed or new_text != text
            text = new_text
        if kind == "external" and (rewriter.changed_flat_import or "ankiscape." in text):
            with_bootstrap = insert_bootstrap_import(text, ast.parse(text))
            changed = changed or with_bootstrap != text
            text = with_bootstrap
        if changed:
            rel = path.relative_to(ROOT)
            print(f"rewrite {rel}")
            if not dry_run:
                ast.parse(text)  # fail fast on broken surgery, before writing
                path.write_text(text, encoding="utf-8")


def phase_audit() -> int:
    errors: list[str] = []
    for path, kind in iter_rewrite_targets():
        rel = path.relative_to(ROOT)
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                parts = (node.module or "").split(".")
                first = parts[0]
                if node.level == 0 and first in BUCKET_OF:
                    errors.append(f"{rel}:{node.lineno}: flat import of moved module {first}")
                if node.level == 1 and kind == "bucket":
                    errors.append(f"{rel}:{node.lineno}: stale single-dot import in bucket module")
                if node.level == 1 and kind == "top":
                    already_new = (len(parts) > 1 and first in BUCKETS) or (
                        node.module is not None
                        and first in BUCKETS
                        and all(a.name in BUCKETS[first] for a in node.names)
                    )
                    if node.module is None:
                        if any(a.name in BUCKET_OF for a in node.names):
                            errors.append(f"{rel}:{node.lineno}: stale 'from . import' of moved module")
                    elif first in BUCKET_OF and not already_new:
                        errors.append(f"{rel}:{node.lineno}: stale relative import of moved module {first}")
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name.split(".")[0] in BUCKET_OF:
                        errors.append(f"{rel}:{node.lineno}: plain import of moved module {alias.name}")
            elif isinstance(node, ast.Try) and kind != "external":
                if (
                    node.body
                    and all(isinstance(s, ast.ImportFrom) and s.level >= 1 for s in node.body)
                    and len(node.handlers) == 1
                    and all(
                        isinstance(s, (ast.Import, ast.ImportFrom))
                        and (isinstance(s, ast.Import) or s.level == 0)
                        for s in node.handlers[0].body
                    )
                ):
                    errors.append(f"{rel}:{node.lineno}: surviving dual-import block")
    for e in errors:
        print(f"AUDIT: {e}", file=sys.stderr)
    print(f"audit: {len(errors)} problem(s)")
    return len(errors)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    phase_move(args.dry_run)
    phase_fixups(args.dry_run)
    phase_rewrite(args.dry_run)
    if args.dry_run:
        print("dry run: audit skipped (tree not modified)")
        return 0
    return 1 if phase_audit() else 0


if __name__ == "__main__":
    raise SystemExit(main())
