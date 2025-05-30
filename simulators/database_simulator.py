import datetime
from typing import Any, Dict, List, Optional

class DatabaseSimulator:
    """In-memory simulator for the Postgres schema defined in database-simulator.sql."""

    def __init__(self) -> None:
        self.tool_registry: List[Dict[str, Any]] = []
        self.command_queue: List[Dict[str, Any]] = []
        self.execution_logs: List[Dict[str, Any]] = []
        self.storage_locations: List[Dict[str, Any]] = []
        self.scheduled_jobs: List[Dict[str, Any]] = []
        self.job_counter = 1

    def load_schema(self, _sql_file: str) -> None:
        """Pretend to load schema from SQL file."""
        # In this simple simulator there is nothing to parse.
        pass

    # --- Tool Registry ---------------------------------------------------------------------
    def insert_tool(self, tool_id: str, name: str, description: str, gateway_type: str = "python") -> None:
        self.tool_registry.append({
            "id": len(self.tool_registry) + 1,
            "tool_id": tool_id,
            "name": name,
            "description": description,
            "gateway_type": gateway_type,
            "created_at": datetime.datetime.utcnow(),
            "updated_at": datetime.datetime.utcnow(),
            "is_active": True,
        })

    # --- Command Queue --------------------------------------------------------------------
    def add_job(self, command_type: str, payload: Dict[str, Any], priority: int = 0) -> int:
        job_id = self.job_counter
        self.job_counter += 1
        self.command_queue.append({
            "id": job_id,
            "command_type": command_type,
            "payload": payload,
            "priority": priority,
            "status": "pending",
            "retry_count": 0,
            "max_retries": 3,
            "created_at": datetime.datetime.utcnow(),
            "started_at": None,
            "completed_at": None,
            "error_details": None,
        })
        return job_id

    def get_next_job(self) -> Optional[Dict[str, Any]]:
        pending = sorted(
            [j for j in self.command_queue if j["status"] == "pending"],
            key=lambda j: (-j["priority"], j["created_at"]),
        )
        if not pending:
            return None
        job = pending[0]
        job["status"] = "executing"
        job["started_at"] = datetime.datetime.utcnow()
        return job

    def complete_job(self, job_id: int, result: Dict[str, Any], error: Optional[str] = None) -> None:
        for job in self.command_queue:
            if job["id"] == job_id:
                job["status"] = "completed" if error is None else "failed"
                job["completed_at"] = datetime.datetime.utcnow()
                job["error_details"] = error
                job.setdefault("result", result)
                break

    # --- Storage Locations ---------------------------------------------------------------
    def record_storage_location(self, job_id: int, storage_type: str, location: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        self.storage_locations.append({
            "id": len(self.storage_locations) + 1,
            "job_id": job_id,
            "storage_type": storage_type,
            "location": location,
            "metadata": metadata or {},
            "created_at": datetime.datetime.utcnow(),
        })

    # --- Scheduled Jobs ------------------------------------------------------------------
    def add_scheduled_job(self, job_name: str, command_type: str, schedule_seconds: int, payload: Dict[str, Any]) -> None:
        self.scheduled_jobs.append({
            "id": len(self.scheduled_jobs) + 1,
            "job_name": job_name,
            "command_type": command_type,
            "schedule_seconds": schedule_seconds,
            "payload": payload,
            "last_run": None,
            "next_run": datetime.datetime.utcnow(),
            "is_active": True,
        })

    def check_scheduled_jobs(self) -> None:
        now = datetime.datetime.utcnow()
        for job in self.scheduled_jobs:
            if job["is_active"] and (job["next_run"] is None or job["next_run"] <= now):
                self.add_job(job["command_type"], job["payload"], priority=50)
                job["last_run"] = now
                job["next_run"] = now + datetime.timedelta(seconds=job["schedule_seconds"])
