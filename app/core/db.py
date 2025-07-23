from sqlalchemy.ext.asyncio import (
    create_async_engine, async_session
)
from sqlalchemy.orm import sessionmaker
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from app.models import User, UserCreate
from app.core.config import settings

DATABASE_URL = settings.DATABASE_URL

engine = create_async_engine(DATABASE_URL, echo=False)
async_session_maker = sessionmaker(
    engine,
    expire_on_commit=False,
    clas_=AsyncSession
)

async def init_db(session: AsyncSession) -> None:
    from app import crud
    result = await session.exec(
        select(User).where(User.username==settings.FIRST_USER)
    )
    user = result.first()
    if not user:
        user_in = UserCreate(
            username=settings.FIRST_USER,
            email=settings.FIRST_USER_EMAIL,
            password=settings.FIRST_USER_PASSWORD,
            is_superuser=True
        )
        user = await crud.create_user(session=session, user_create=user_in)