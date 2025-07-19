import uuid
from pyexpat.errors import messages

from fastapi import APIRouter, HTTPException

from app import crud
from app.api.deps import SessionDep, CurrentUser
from app.core.security import verify_password
from app.models import (
    UserRegister,
    UserCreate,
    UserUpdatePassword,
    UserPublic,
    User,
    Message
)


router = APIRouter(prefix='/users', tags=['users'])

@router.post('/sign-up', response_model=UserPublic)
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

@router.patch('/update-password/{user_id}', response_model=UserPublic)
async def update_password(
        session: SessionDep, user_id: uuid.UUID,
        current_user: CurrentUser, user_update_password: UserUpdatePassword
):
    db_user = await session.get(User, user_id)
    if db_user is None:
        raise HTTPException(
            status_code=400, detail='User not found'
        )
    if db_user.id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail='The user doesn\'t have enough privileges'
        )
    if verify_password(
            user_update_password.current_password,
            db_user.hashed_password
    ):
        db_user = await crud.user_update_password(
            session=session, db_user=db_user,
            user_update_password=user_update_password
        )
    else:
        raise HTTPException(
            status_code=400, detail='Incorrect password'
        )
    return db_user

@router.get('/me', response_model=UserPublic)
async def read_current_user(current_user: CurrentUser):
    return current_user

@router.get('/{user_id}', response_model=UserPublic)
async def get_user_by_id(
        session: SessionDep, user_id: uuid.UUID,
        current_user: CurrentUser
):
    db_user = await session.get(User, user_id)
    if not db_user:
        return HTTPException(
            status_code=400, detail='User not found'
        )
    if db_user.id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=403,
            detail='The user doesn\'t have enough privileges'
        )
    return db_user

@router.delete('/{user_id}', response_model=Message)
async def delete_user(
        session: SessionDep, user_id: uuid.UUID,
        current_user: CurrentUser
):
    db_user = await session.get(User, user_id)
    if not db_user:
        raise HTTPException(
            status_code=400, detail='User not found'
        )
    if not current_user.is_superuser and current_user.id != db_user.id:
        raise HTTPException(
            status_code=400, detail='The user doesn\'t have enough privileges'
        )
    if db_user.is_superuser:
        raise HTTPException(
            status_code=403, detail='Superuser cannot be deleted'
        )
    await session.delete(db_user)
    await session.commit()
    return Message(message='User deleted successfully')