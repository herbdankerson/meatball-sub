"""Initialize the database simulator with schema and demo data."""

from simulators.database_simulator import DatabaseSimulator


def init_db(sql_file: str) -> DatabaseSimulator:
    db = DatabaseSimulator()
    db.load_schema(sql_file)
    return db
