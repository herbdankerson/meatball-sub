"""Load all tools after validation."""

from .tool_loader import load_all_tools
from .tool_validator import validate_tools


def bulk_load(db) -> None:
    errors = validate_tools()
    if errors:
        raise RuntimeError("Validation errors: " + ", ".join(errors))
    load_all_tools(db)
