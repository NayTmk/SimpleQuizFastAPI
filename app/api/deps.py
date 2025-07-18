import jwt

from fastapi import HTTPException, status
from fastapi.params import Depends
from fastapi.security import OAuth2PasswordBearer
from typing import Annotated, AsyncGenerator
from jwt.exceptions import InvalidTokenError
from pydantic import ValidationError
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.config import settings
from app.core.db import engine
from app.models import User, TokenPayload


oauth2_token = OAuth2PasswordBearer(tokenUrl='/login/access-token')

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSession(engine) as session:
        yield session


SessionDep = Annotated[AsyncSession, Depends(get_db)]
TokenDep = Annotated[str, Depends(oauth2_token)]


async def get_current_user(session: SessionDep, token: TokenDep) -> User:
    try:
        token_data = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        token_data = TokenPayload(**token_data)
    except (InvalidTokenError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Could not validate credentials'
        )
    user = await session.get(User, token_data.sub)
    if not user:
        raise HTTPException(status_code=404, detail='User not found')
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def get_current_active_super_user(current_user: CurrentUser) -> User:
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=403, detail='The user doesn\'t have enough privileges'
        )
    return current_user