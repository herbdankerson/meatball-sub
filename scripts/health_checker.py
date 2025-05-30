"""Simple health checks for components."""

from simulators.database_simulator import DatabaseSimulator


def check(db: DatabaseSimulator) -> bool:
    return db is not None
