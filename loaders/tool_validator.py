"""Validate tool modules have a main() function."""

from importlib import import_module
from typing import List

from .tool_discovery import discover_tools


def validate_tools() -> List[str]:
    errors = []
    for path in discover_tools():
        module = import_module(f"tools.{path.stem}")
        if not hasattr(module, "main"):
            errors.append(f"{path.stem} missing main()")
    return errors
