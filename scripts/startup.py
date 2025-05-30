"""Startup orchestrator for the simulated environment."""

from .database_initializer import init_db
from .dependency_installer import install
from .service_starter import start
from .health_checker import check
from loaders.bulk_loader import bulk_load


def main():
    install()
    db = init_db("database-simulator.sql")
    bulk_load(db)
    start()
    if check(db):
        print("System started successfully")


if __name__ == "__main__":
    main()
