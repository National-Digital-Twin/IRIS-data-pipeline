import sys
import os


def add_src_path(relative_path: str) -> None:
    abs_path = os.path.abspath(os.path.join(os.path.dirname(__file__), relative_path))
    if abs_path not in sys.path:
        sys.path.insert(0, abs_path)


# Make mapper/src importable as top-level modules for tests
add_src_path("mapper/src")

