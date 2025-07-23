from datetime import timedelta
from fastapi import APIRouter, HTTPException
from typing import Annotated
from fastapi.params import Depends
from fastapi.security import OAuth2PasswordRequestForm
from app import crud, models
from app.core import security
from app.core.config import settings
from app.api.deps import SessionDep
from app.models import Token


router = APIRouter(tags=['login'])

@router.post('/login/access-token', response_model=Token)
async def get_access_token(
        session: SessionDep,
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
):
    user = await crud.authenticate(
        session=session, username=form_data.username,
        password=form_data.password
    )
    if not user:
        raise HTTPException(
            401,
            detail='Incorrect username or password'
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return models.Token(
        access_token=security.create_access_token(
            str(user.id), expires_delta=access_token_expires
        ),
        token_type='bearer'
    )