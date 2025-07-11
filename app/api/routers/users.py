from fastapi import APIRouter, HTTPException

from app import crud
from app.api.deps import SessionDep
from app.models import UserBase, UserRegister, UserCreate

router = APIRouter(prefix='/users', tags=['users'])

@router.post('/sigh-up', response_model=UserBase)
async def register_user(session: SessionDep, user_in: UserRegister):
    user = await crud.get_user_by_username(
        session=session, username=user_in.username
    )
    if user:
        raise HTTPException(
            status_code=400,
            detail='The user with this username already exists'
        )
    user_create = UserCreate.model_validate(user_in)
    user = await crud.create_user(
        session=session, user_create=user_create
    )
    return user