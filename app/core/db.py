from sqlalchemy.ext.asyncio import (
    create_async_engine, AsyncSession
)
from sqlalchemy.orm import sessionmaker
from .config import settings


DATABASE_URL = settings.DATABASE_URL

engine = create_async_engine(DATABASE_URL, echo=False)

async_session = sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession,
)