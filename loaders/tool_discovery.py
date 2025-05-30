"""Discover tool modules in the tools directory."""

from pathlib import Path
from typing import List


def discover_tools() -> List[Path]:
    return [p for p in Path("tools").glob("*.py") if p.is_file()]
