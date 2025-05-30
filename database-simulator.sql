-- DABOTMAN Database Simulator Setup
-- Creates test databases with exact schema matching production

-- Create test databases
CREATE DATABASE IF NOT EXISTS test_system_db;
CREATE DATABASE IF NOT EXISTS test_workspace_db;
CREATE DATABASE IF NOT EXISTS test_analytics_db;

-- Switch to test_system_db
\c test_system_db;

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "postgres_fdw";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Create schemas
CREATE SCHEMA IF NOT EXISTS system_schema;
CREATE SCHEMA IF NOT EXISTS workspace_schema;

-- Create core tables
CREATE TABLE IF NOT EXISTS system_schema.tool_registry (
    id SERIAL PRIMARY KEY,
    tool_id VARCHAR(255) NOT NULL UNIQUE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    category VARCHAR(100),
    gateway_type VARCHAR(50) DEFAULT 'base',
    schema JSONB DEFAULT '{}',
    config JSONB DEFAULT '{}',
    documentation TEXT,
    installation_notes TEXT,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS system_schema.command_queue (
    id SERIAL PRIMARY KEY,
    command_type VARCHAR(100) NOT NULL,
    payload JSONB DEFAULT '{}',
    status VARCHAR(50) DEFAULT 'pending',
    priority INTEGER DEFAULT 0,
    retry_count INTEGER DEFAULT 0,
    max_retries INTEGER DEFAULT 3,
    error_details TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    created_by VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS system_schema.execution_logs (
    id SERIAL PRIMARY KEY,
    command_id INTEGER REFERENCES system_schema.command_queue(id),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    level VARCHAR(20),
    message TEXT,
    details JSONB DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS workspace_schema.storage_locations (
    id SERIAL PRIMARY KEY,
    job_id INTEGER REFERENCES system_schema.command_queue(id),
    storage_type VARCHAR(50),
    location TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create get_next_job function
CREATE OR REPLACE FUNCTION system_schema.get_next_job()
RETURNS TABLE(
    job_id INTEGER,
    command_type VARCHAR,
    payload JSONB
) AS $$
BEGIN
    RETURN QUERY
    WITH next_job AS (
        SELECT id, command_type, payload
        FROM system_schema.command_queue
        WHERE status = 'pending'
        ORDER BY priority DESC, created_at ASC
        LIMIT 1
        FOR UPDATE SKIP LOCKED
    )
    UPDATE system_schema.command_queue cq
    SET status = 'executing',
        started_at = CURRENT_TIMESTAMP
    FROM next_job nj
    WHERE cq.id = nj.id
    RETURNING cq.id, cq.command_type, cq.payload;
END;
$$ LANGUAGE plpgsql;

-- Create complete_job function
CREATE OR REPLACE FUNCTION system_schema.complete_job(
    p_job_id INTEGER,
    p_result JSONB DEFAULT '{}',
    p_error TEXT DEFAULT NULL
)
RETURNS VOID AS $$
BEGIN
    UPDATE system_schema.command_queue
    SET status = CASE 
            WHEN p_error IS NULL THEN 'completed'
            ELSE 'failed'
        END,
        completed_at = CURRENT_TIMESTAMP,
        error_details = p_error,
        payload = payload || jsonb_build_object('result', p_result)
    WHERE id = p_job_id;
END;
$$ LANGUAGE plpgsql;

-- Create record_storage_location function
CREATE OR REPLACE FUNCTION workspace_schema.record_storage_location(
    p_job_id INTEGER,
    p_storage_type VARCHAR,
    p_location TEXT,
    p_metadata JSONB DEFAULT '{}'
)
RETURNS VOID AS $$
BEGIN
    INSERT INTO workspace_schema.storage_locations (job_id, storage_type, location, metadata)
    VALUES (p_job_id, p_storage_type, p_location, p_metadata);
END;
$$ LANGUAGE plpgsql;

-- Insert sample tools
INSERT INTO system_schema.tool_registry (tool_id, name, description, gateway_type, schema) VALUES
('schema_extractor', 'Schema Extractor', 'Extracts database schema information', 'python', 
 '{"input": {"type": "object", "properties": {"database": {"type": "string"}}}, "output": {"type": "object"}}'),
('ner_analyzer', 'NER Analyzer', 'Named Entity Recognition on SQL and text', 'python',
 '{"input": {"type": "object", "properties": {"text": {"type": "string"}}}, "output": {"type": "array"}}'),
('embedder_voyage', 'Voyage Embedder', 'Generate embeddings with Voyage AI', 'api',
 '{"input": {"type": "object", "properties": {"texts": {"type": "array"}}}, "output": {"type": "array"}}'),
('graph_builder', 'Graph Builder', 'Build knowledge graphs from data', 'python',
 '{"input": {"type": "object", "properties": {"nodes": {"type": "array"}, "edges": {"type": "array"}}}}'),
('report_generator', 'Report Generator', 'Generate analysis reports', 'python',
 '{"input": {"type": "object", "properties": {"data": {"type": "object"}}}, "output": {"type": "string"}}');

-- Insert sample jobs for testing
INSERT INTO system_schema.command_queue (command_type, payload, priority) VALUES
('analyze_schema', '{"database": "test_system_db", "output_destinations": {"primary": {"type": "file", "location": "schema_output.json"}}}', 10),
('extract_entities', '{"target": "sql_functions", "output_destinations": {"primary": {"type": "qdrant", "collection": "entities"}}}', 5);

-- Create cron-like scheduler simulation
CREATE TABLE IF NOT EXISTS system_schema.scheduled_jobs (
    id SERIAL PRIMARY KEY,
    job_name VARCHAR(255) UNIQUE NOT NULL,
    command_type VARCHAR(100) NOT NULL,
    schedule VARCHAR(100) NOT NULL, -- cron expression
    payload JSONB DEFAULT '{}',
    is_active BOOLEAN DEFAULT true,
    last_run TIMESTAMP,
    next_run TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Cron simulation function
CREATE OR REPLACE FUNCTION system_schema.check_scheduled_jobs()
RETURNS VOID AS $$
DECLARE
    job RECORD;
BEGIN
    FOR job IN 
        SELECT * FROM system_schema.scheduled_jobs
        WHERE is_active = true
        AND (next_run IS NULL OR next_run <= CURRENT_TIMESTAMP)
    LOOP
        -- Insert job into command queue
        INSERT INTO system_schema.command_queue (command_type, payload, priority)
        VALUES (job.command_type, job.payload, 50);
        
        -- Update last/next run times (simplified - real cron parser needed)
        UPDATE system_schema.scheduled_jobs
        SET last_run = CURRENT_TIMESTAMP,
            next_run = CURRENT_TIMESTAMP + INTERVAL '1 hour'
        WHERE id = job.id;
    END LOOP;
END;
$$ LANGUAGE plpgsql;

-- Insert sample scheduled jobs
INSERT INTO system_schema.scheduled_jobs (job_name, command_type, schedule, payload) VALUES
('hourly_analysis', 'analyze_schema', '0 * * * *', '{"auto": true}'),
('daily_report', 'generate_report', '0 0 * * *', '{"type": "daily"}');

-- Create trigger for auto-updating timestamps
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_tool_registry_updated_at
BEFORE UPDATE ON system_schema.tool_registry
FOR EACH ROW EXECUTE FUNCTION update_updated_at();