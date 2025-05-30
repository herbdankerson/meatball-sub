#!/usr/bin/env python3
"""
Cron-like simulator for testing DABOTMAN command queue
Simulates pg_cron functionality for development
"""

import time
import psycopg2
import threading
import json
from datetime import datetime

class CronSimulator:
    def __init__(self, db_config):
        self.db_config = db_config
        self.running = False
        
    def connect(self):
        """Create database connection"""
        return psycopg2.connect(**self.db_config)
        
    def check_scheduled_jobs(self):
        """Check and queue scheduled jobs - mimics pg_cron"""
        conn = self.connect()
        cur = conn.cursor()
        
        try:
            # Call the database function
            cur.execute("SELECT system_schema.check_scheduled_jobs()")
            conn.commit()
            
            # Log what happened
            cur.execute("""
                SELECT job_name, command_type, last_run 
                FROM system_schema.scheduled_jobs 
                WHERE last_run >= CURRENT_TIMESTAMP - INTERVAL '1 minute'
            """)
            
            for job in cur.fetchall():
                print(f"[CRON] Scheduled job '{job[0]}' ({job[1]}) executed at {job[2]}")
                
        except Exception as e:
            print(f"[CRON ERROR] {e}")
            conn.rollback()
        finally:
            cur.close()
            conn.close()
            
    def process_queue(self):
        """Process command queue - mimics external wrapper"""
        conn = self.connect()
        cur = conn.cursor()
        
        try:
            # Get next job
            cur.execute("SELECT * FROM system_schema.get_next_job()")
            job = cur.fetchone()
            
            if job:
                job_id, command_type, payload = job
                print(f"[QUEUE] Processing job {job_id}: {command_type}")
                
                # Simulate processing
                time.sleep(2)  # Simulate work
                
                # Mark complete
                result = {"status": "success", "timestamp": datetime.now().isoformat()}
                cur.execute(
                    "SELECT system_schema.complete_job(%s, %s::jsonb)",
                    (job_id, json.dumps(result))
                )
                
                # Record storage location
                cur.execute(
                    "SELECT workspace_schema.record_storage_location(%s, %s, %s, %s::jsonb)",
                    (job_id, "file", f"/output/job_{job_id}_result.json", json.dumps({"size": 1024}))
                )
                
                conn.commit()
                print(f"[QUEUE] Job {job_id} completed")
                
        except Exception as e:
            print(f"[QUEUE ERROR] {e}")
            if 'job_id' in locals():
                cur.execute(
                    "SELECT system_schema.complete_job(%s, %s::jsonb, %s)",
                    (job_id, json.dumps({}), str(e))
                )
            conn.rollback()
        finally:
            cur.close()
            conn.close()
            
    def run_scheduler(self):
        """Run cron scheduler every 60 seconds"""
        while self.running:
            self.check_scheduled_jobs()
            time.sleep(60)
            
    def run_queue_processor(self):
        """Run queue processor every 5 seconds"""
        while self.running:
            self.process_queue()
            time.sleep(5)
            
    def start(self):
        """Start both cron and queue processor"""
        self.running = True
        
        # Start scheduler thread
        scheduler_thread = threading.Thread(target=self.run_scheduler)
        scheduler_thread.daemon = True
        scheduler_thread.start()
        
        # Start queue processor thread
        queue_thread = threading.Thread(target=self.run_queue_processor)
        queue_thread.daemon = True
        queue_thread.start()
        
        print("[SIMULATOR] Started cron scheduler and queue processor")
        print("[SIMULATOR] Press Ctrl+C to stop")
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n[SIMULATOR] Shutting down...")
            self.stop()
            
    def stop(self):
        """Stop the simulator"""
        self.running = False

if __name__ == "__main__":
    # Database configuration
    db_config = {
        'host': 'localhost',
        'port': 5432,
        'user': 'supabase',
        'password': 'your-super-secret-password',
        'database': 'test_system_db'
    }
    
    # Create and start simulator
    simulator = CronSimulator(db_config)
    simulator.start()