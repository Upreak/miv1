-- Database Setup Script for Recruitment Platform
-- Run this with: psql -U postgres -f setup_db.sql

-- Create user
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_user WHERE usename = 'myuser') THEN
        CREATE USER myuser WITH PASSWORD 'mysecurepwd';
    END IF;
END
$$;

-- Create database
CREATE DATABASE recruitment_db OWNER myuser;

-- Connect to the database
\c recruitment_db

-- Grant all privileges on schema
GRANT ALL ON SCHEMA public TO myuser;
ALTER SCHEMA public OWNER TO myuser;

-- Grant privileges on database
GRANT ALL PRIVILEGES ON DATABASE recruitment_db TO myuser;
