"""Install the stable ``ankiscape`` package alias for tests and tools.

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
