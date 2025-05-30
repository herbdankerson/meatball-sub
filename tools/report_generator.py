"""Simulated report generator tool."""

import json
import sys


def main():
    data = json.loads(sys.argv[1])
    sections = data.get("sections", [])
    content = "\n".join(f"# {s.title()}" for s in sections)
    result = {"report": content}
    json.dump(result, sys.stdout)


if __name__ == "__main__":
    main()
