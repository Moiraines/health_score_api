#!/bin/bash

# Script to initialize Alembic for database migrations in the Health Score API project

# Ensure the script is run from the project root directory
if [ ! -d "health_score_api/app" ]; then
  echo "Error: This script must be run from the project root directory."
  exit 1
fi

# Check if Alembic is installed
if ! command -v alembic &> /dev/null; then
  echo "Alembic is not installed. Installing now..."
  pip install alembic
fi

# Initialize Alembic repository if not already initialized
if [ ! -d "health_score_api/app/migrations" ]; then
  echo "Initializing Alembic repository..."
  cd health_score_api/app
  alembic init migrations
  cd ../..
  echo "Alembic repository initialized at health_score_api/app/migrations"
else
  echo "Alembic repository already exists at health_score_api/app/migrations"
fi

# Update alembic.ini file with the correct database URL placeholder
ALEMBIC_INI="health_score_api/app/alembic.ini"
if [ -f "$ALEMBIC_INI" ]; then
  echo "Updating database URL in $ALEMBIC_INI..."
  sed -i 's|sqlalchemy.url =.*|sqlalchemy.url = \${DATABASE_URL}|' "$ALEMBIC_INI"
  echo "Database URL updated in $ALEMBIC_INI. Make sure to set DATABASE_URL in your .env file."
else
  echo "Warning: $ALEMBIC_INI not found. Please check your Alembic setup."
fi

# Generate an initial migration based on the current models
 echo "Generating initial migration..."
 cd health_score_api/app
 alembic revision --autogenerate -m "Initial migration"
 cd ../..
 echo "Initial migration generated. Check health_score_api/app/migrations/versions/ for the migration script."

# Optionally, apply the migration to the database (uncomment if you want to apply immediately)
# echo "Applying migrations to the database..."
# cd health_score_api/app
# alembic upgrade head
# cd ../..
# echo "Migrations applied to the database."

echo "Alembic setup complete. You can now manage database migrations with 'alembic' commands from health_score_api/app directory."
echo "To apply migrations, run 'cd health_score_api/app && alembic upgrade head'"
