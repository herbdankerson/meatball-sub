"""Simulated graph builder tool."""

import json
import sys


def main():
    data = json.loads(sys.argv[1])
    nodes = data.get("nodes", [])
    edges = data.get("edges", [])
    result = {"nodes": nodes, "edges": edges}
    json.dump(result, sys.stdout)


if __name__ == "__main__":
    main()
