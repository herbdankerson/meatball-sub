"""Generate a simple tool manifest JSON."""

import json
from pathlib import Path
from .tool_discovery import discover_tools


def generate_manifest(path: str) -> None:
    tools = [p.stem for p in discover_tools()]
    with open(path, "w") as f:
        json.dump({"tools": tools}, f, indent=2)
