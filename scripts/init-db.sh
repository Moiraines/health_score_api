#!/bin/bash
set -e

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL to be ready..."
until pg_isready -h db -U "$POSTGRES_USER" -d "$POSTGRES_DB"; do
  sleep 1
done

echo "Creating database $POSTGRES_DB..."
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    -- Create extensions
    CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
    
    -- Create additional schemas if needed
    -- CREATE SCHEMA IF NOT EXISTS auth;
    -- CREATE SCHEMA IF NOT EXISTS analytics;
    
    -- Grant permissions
    GRANT ALL PRIVILEGES ON DATABASE "$POSTGRES_DB" TO "$POSTGRES_USER";
    
    -- Create initial admin user (password will be set by the application)
    -- This is just a placeholder, the actual password will be hashed by the application
    -- INSERT INTO users (email, username, hashed_password, is_superuser, is_active, email_verified)
    -- VALUES ('admin@example.com', 'admin', '', TRUE, TRUE, TRUE)
    -- ON CONFLICT (email) DO NOTHING;
EOSQL

echo "Database initialization complete!"
