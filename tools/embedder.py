"""Simulated embedder tool."""

import json
import sys
import random


def main():
    data = json.loads(sys.argv[1])
    texts = data.get("texts", [])
    result = {"embeddings": [[random.random() for _ in range(3)] for _ in texts]}
    json.dump(result, sys.stdout)


if __name__ == "__main__":
    main()
