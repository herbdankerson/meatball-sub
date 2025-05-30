"""Simple pipeline runner using the database simulator."""

import importlib
import json
import time

from simulators.database_simulator import DatabaseSimulator
from loaders.bulk_loader import bulk_load


def execute_job(db: DatabaseSimulator, job):
    tool_name = job["command_type"]
    module = importlib.import_module(f"tools.{tool_name}")
    payload = job["payload"]
    result = json.loads(subprocess_run(module.main, payload))
    db.complete_job(job["id"], result)


def subprocess_run(func, payload):
    # Simulate running the tool as a subprocess by calling its main
    import sys
    from io import StringIO

    stdout = StringIO()
    sys_stdout = sys.stdout
    sys.stdout = stdout
    try:
        func_arg = json.dumps(payload)
        func_main = func
        sys.argv = [sys.argv[0], func_arg]
        func_main()
    finally:
        sys.stdout = sys_stdout
    return stdout.getvalue()


def main():
    db = DatabaseSimulator()
    bulk_load(db)

    # Add sample job
    db.add_job("schema_extractor", {"database": "test"})

    while True:
        job = db.get_next_job()
        if not job:
            break
        execute_job(db, job)

    print(json.dumps(db.command_queue, default=str))


if __name__ == "__main__":
    main()
