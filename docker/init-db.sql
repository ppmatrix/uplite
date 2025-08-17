-- UpLite PostgreSQL Initialization Script
-- This script runs when the PostgreSQL container starts for the first time

-- The database 'uplite' and user 'uplite' are created automatically by the
-- POSTGRES_DB, POSTGRES_USER, and POSTGRES_PASSWORD environment variables

-- Create any additional extensions if needed
-- CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Grant necessary permissions (usually done automatically for the main user)
-- GRANT ALL PRIVILEGES ON DATABASE uplite TO uplite;

-- Log the initialization
SELECT 'UpLite PostgreSQL database initialized successfully' as status;
