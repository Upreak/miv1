"""Alembic environment configuration for database migrations."""

from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context
import sys
import os

# Add the Backend directory to the Python path (where backend_app package is located)
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)


# Import Base and all models
try:
    from backend_app.db.base import Base
    # Import all model classes to ensure they're registered with Base.metadata
    from backend_app.db.models import (
        User, SystemSettings, Client, Job, ExternalJobPosting,
        JobPrescreenQuestion, PrescreenAnswer, JobFAQ,
        CandidateProfile, CandidateWorkHistory,
        Application, ApplicationTimeline,
        ChatMessage, ActionQueue, ActivityLog,
        Lead, SalesTask
    )
except ImportError as e:
    print(f"Error importing models: {e}")
    raise

# Import settings to get database URL
try:
    from backend_app.config_settings import settings
    database_url = str(settings.DATABASE_URL).replace('postgresql+asyncpg://', 'postgresql://')
except ImportError:
    import os
    from dotenv import load_dotenv
    load_dotenv()
    database_url = os.getenv('DATABASE_URL', 'postgresql://myuser:mysecurepwd@localhost/recruitment_db')
    # Ensure it's synchronous URL for migrations
    database_url = database_url.replace('postgresql+asyncpg://', 'postgresql://')


# this is the Alembic Config object
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set the SQLAlchemy URL from application settings
config.set_main_option('sqlalchemy.url', database_url)


# Add your model's MetaData object here for 'autogenerate' support
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.
    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
