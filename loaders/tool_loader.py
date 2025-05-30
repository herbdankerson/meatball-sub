"""Load tools into the database simulator."""

from importlib import import_module
from typing import Any
from .tool_discovery import discover_tools


def load_all_tools(db) -> None:
    for path in discover_tools():
        module_name = f"tools.{path.stem}"
        module = import_module(module_name)
        description = (module.__doc__ or "").strip()
        db.insert_tool(path.stem, path.stem.replace("_", " ").title(), description)
