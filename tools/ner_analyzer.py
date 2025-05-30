"""Simulated NER analyzer tool."""

import json
import sys


def main():
    data = json.loads(sys.argv[1])
    text = data.get("text", "")
    # simplistic 'entity' extraction splitting words starting with capital letters
    entities = [word for word in text.split() if word.istitle()]
    json.dump(entities, sys.stdout)


if __name__ == "__main__":
    main()
