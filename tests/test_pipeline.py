import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))

from simulators.database_simulator import DatabaseSimulator
from loaders.bulk_loader import bulk_load
from main import execute_job


def test_pipeline():
    db = DatabaseSimulator()
    bulk_load(db)
    job_id = db.add_job("schema_extractor", {"database": "test"})
    job = db.get_next_job()
    assert job
    execute_job(db, job)
    completed = next(j for j in db.command_queue if j["id"] == job_id)
    assert completed["status"] == "completed"
