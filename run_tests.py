import os
import sys
import unittest


def main() -> int:
    # Ensure project root is importable for tests
    root = os.path.dirname(os.path.abspath(__file__))
    if root not in sys.path:
        sys.path.insert(0, root)

    # Discover and run tests under tests/
    loader = unittest.TestLoader()
    suite = loader.discover(start_dir=os.path.join(root, "tests"), pattern="test_*.py")

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
