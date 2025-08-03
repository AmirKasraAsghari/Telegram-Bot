import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


def pytest_collection_modifyitems(config, items):
    target = None
    for item in items:
        if item.nodeid.endswith("test_coverage_threshold.py::test_coverage_threshold"):
            target = item
            break
    if target:
        items.remove(target)
        items.append(target)
