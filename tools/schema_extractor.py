"""Simulated schema extractor tool."""

import json
import sys


def main():
    data = json.loads(sys.argv[1])
    database = data.get("database", "unknown")
    result = {"database": database, "tables": ["table1", "table2"]}
    json.dump(result, sys.stdout)


if __name__ == "__main__":
    main()
