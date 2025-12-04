"""
Database Connection Module
"""
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import MetaData
import logging

from backend_app.config import settings

logger = logging.getLogger(__name__)

# Create async engine
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DATABASE_ECHO,
    future=True
)

# Create async session factory
AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Create base class for models
Base = declarative_base(metadata=MetaData(schema="public"))


async def get_db() -> AsyncSession:
    """Dependency to get database session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    """Initialize database tables"""
    try:
        async with engine.begin() as conn:
            # Import all models to ensure they are registered
            from backend_app.db.models import users
            from backend_app.db.models import candidate_profiles
            from backend_app.db.models import jobs
            from backend_app.db.models import applications
            from backend_app.db.models import external_job_postings
            from backend_app.db.models import action_queue
            from backend_app.db.models import chat_messages
            from backend_app.db.models import activity_logs
            from backend_app.db.models import clients
            from backend_app.db.models import leads
            from backend_app.db.models import sales_tasks
            from backend_app.db.models import system_settings
            from backend_app.db.models import candidate_work_history
            from backend_app.db.models import application_timeline
            
            # Create all tables
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        raise


async def close_db():
    """Close database connection"""
    await engine.dispose()
    logger.info("Database connection closed")