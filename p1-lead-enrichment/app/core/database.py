from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.core.settings import get_settings

settings = get_settings()

# Replace postgresql:// with postgresql+asyncpg:// for async support
database_url = settings.database_url.replace(
    "postgresql://", "postgresql+asyncpg://"
)

engine = create_async_engine(
    database_url,
    pool_size=10,       # max 10 persistent connections
    max_overflow=20,    # up to 20 extra connections under load
    echo=settings.app_env == "local",  # log SQL queries in local only
)

# Session factory — used to create DB sessions per request
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncSession:
    # Dependency injected into routes — provides a DB session per request
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            # Rollback transaction if anything goes wrong in the route
            await session.rollback()
            raise
