-- Initialize the database with proper settings
-- This file is run when the postgres container starts

-- Ensure proper encoding
CREATE DATABASE foia_db 
    WITH ENCODING 'UTF8'
    LC_COLLATE = 'en_US.UTF-8'
    LC_CTYPE = 'en_US.UTF-8'
    TEMPLATE = template0;

-- Create user if not exists (though this is handled by environment variables)
-- This is a no-op in most cases but ensures compatibility
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'foia_user') THEN
        CREATE USER foia_user WITH PASSWORD 'foia_pass';
    END IF;
END
$$;

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE foia_db TO foia_user;