import uuid
from app.core.security import get_hashed_password, verify_password
from sqlmodel import select
from app.api.deps import SessionDep
from app.models import (
    User, UserCreate, UserUpdatePassword,
    QuizCreate, Quiz,
    QuestionCreate, Question,
    AnswerCreate, Answer
)


async def create_user(*, session: SessionDep, user_create: UserCreate) -> User:
    db_obj = User.model_validate(
        user_create, update={
            'hashed_password': get_hashed_password(user_create.password)
        }
    )
    session.add(db_obj)
    await session.commit()
    await session.refresh(db_obj)
    return db_obj

async def user_update_password(
        *, session: SessionDep, db_user: User,
        user_update_password: UserUpdatePassword
):
    user_data = user_update_password.model_dump(exclude_unset=True)
    extra_data = {}
    if 'new_password' in user_data:
        password = user_data['new_password']
        hashed_password = get_hashed_password(password)
        extra_data['hashed_password'] = hashed_password
    db_user.sqlmodel_update(user_data, update=extra_data)
    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)
    return db_user

async def get_user_by_username(*, session: SessionDep, username: str) -> User | None:
    db_statement = select(User).where(User.username == username)
    result = await session.exec(db_statement)
    return result.first()

async def authenticate(
        *, session: SessionDep, username: str, password: str
) -> User | None:
    db_user = await get_user_by_username(session=session, username=username)
    if not db_user:
        return None
    if not verify_password(password, db_user.hashed_password):
        return None
    return db_user

async def quiz_create(
        *, session: SessionDep,
        quiz: QuizCreate, owner_id: uuid.UUID
) -> Quiz:
    db_obj = Quiz.model_validate(quiz, update={'owner_id': owner_id})
    session.add(db_obj)
    await session.commit()
    await session.refresh(db_obj)
    return db_obj

async def question_create(
        *, session: SessionDep, question: QuestionCreate,
        quiz_id: uuid.UUID
) -> Question:
    db_obj = Question.model_validate(
        question, update={'quiz_id': quiz_id}
    )
    session.add(db_obj)
    await session.commit()
    await session.refresh(db_obj)
    return db_obj

async def answer_create(
        *, session: SessionDep, answer: AnswerCreate,
        question_id: uuid.UUID
) -> Answer:
    db_obj = Answer.model_validate(
        answer, update={'question_id': question_id}
    )
    session.add(db_obj)
    await session.commit()
    await session.refresh(db_obj)
    return db_obj