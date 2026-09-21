import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

_CHECK_INDEPENDENT_IMPORT = """
import importlib
import inspect
import sys
from pathlib import Path

import pkg_alias

part = importlib.import_module(sys.argv[1])
assert 'ankiscape.logic.shop_logic' not in sys.modules
owned = {
    name: value
    for name, value in vars(part).items()
    if inspect.isfunction(value)
    and Path(value.__code__.co_filename).resolve() == Path(part.__file__).resolve()
}
assert owned
for name, function in owned.items():
    assert function.__globals__ is vars(part), name

shop = importlib.import_module('ankiscape.logic.shop_logic')
for name, function in owned.items():
    assert getattr(shop, name) is function, name
    assert function.__globals__ is vars(part), name
    assert function.__module__ == part.__name__, name

for name in ('SHOP_SERVICES', 'SHOP_VENDOR_ACTIONS', 'SHOP_PLAYER_SELL_PRICES'):
    assert getattr(part, name) is getattr(shop, name), name
assert shop._append_event is shop.apply_shop_service_pure.__globals__['_append_event']
"""


class ShopModuleBoundariesTest(unittest.TestCase):
    def test_parts_import_independently_and_keep_native_globals(self):
        for module in ("ankiscape.logic.shop.state", "ankiscape.logic.shop.services"):
            with self.subTest(module=module):
                result = subprocess.run(
                    [sys.executable, "-c", _CHECK_INDEPENDENT_IMPORT, module],
                    cwd=ROOT,
                    text=True,
                    capture_output=True,
                    check=False,
                    timeout=60,
                )
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
