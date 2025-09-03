# Database Migrations

This directory contains database migration scripts managed by Alembic.

## Setup

1. Ensure you have the required dependencies installed:
   ```bash
   pip install alembic sqlalchemy asyncpg
   ```

2. Configure your database connection in `app/core/config.py`:
   ```python
   SQLALCHEMY_DATABASE_URI = "postgresql+asyncpg://user:password@localhost:5432/healthscore"
   ```

## Creating Migrations

1. After making changes to your models, create a new migration:
   ```bash
   cd /path/to/health_score_api
   alembic revision --autogenerate -m "Your migration message"
   ```

2. Review the generated migration file in `app/db/migrations/versions/`

## Running Migrations

- Apply all pending migrations:
  ```bash
  alembic upgrade head
  ```

- Rollback to a specific revision:
  ```bash
  alembic downgrade <revision>
  ```

- Run a specific migration:
  ```bash
  alembic upgrade <revision>
  ```

## Common Commands

- Show current revision:
  ```bash
  alembic current
  ```

- Show migration history:
  ```bash
  alembic history
  ```

- Show available revisions:
  ```bash
  alembic heads
  ```

## Best Practices

1. Always review auto-generated migrations before applying them
2. Write idempotent migrations when possible
3. Test migrations in a development environment first
4. Keep migrations small and focused on a single change
5. Never modify migration files after they've been committed to version control

## Troubleshooting

- If you encounter issues with the database connection, verify your `SQLALCHEMY_DATABASE_URI` in `app/core/config.py`
- For PostgreSQL permission issues, ensure the database user has the necessary privileges
- If migrations fail, check the error message and review the migration files for any issues

## Migration Dependencies

Migrations may depend on each other. The `depends_on` field in the migration file specifies these dependencies. Ensure all dependencies are met before applying migrations.
