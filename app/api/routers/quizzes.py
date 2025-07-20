import uuid
from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import selectinload
from sqlmodel import select

from app import crud
from app.api.deps import SessionDep, CurrentUser
from app.models import (
    QuizCreate, QuizUpdate, QuizRead, Quiz,
    Message, Question
)

router = APIRouter(prefix='/quizzes', tags=['quizzes'])


@router.delete('/{quiz_id}')
async def delete_quiz(
        session: SessionDep, quiz_id: uuid.UUID,
        current_user: CurrentUser
):
    db_quiz = await session.get(Quiz, quiz_id)
    if not db_quiz:
        raise HTTPException(
            status_code=404, detail='Quiz not found'
        )
    if not current_user.is_superuser and current_user.id != db_quiz.owner_id:
        raise HTTPException(
            status_code=400,
            detail='The user doesn\'t have enough privileges'
        )
    await session.delete(db_quiz)
    await session.commit()
    return Message(message='Quiz deleted successfully')

@router.post('/create-quiz', response_model=QuizRead)
async def create_quiz(
        session: SessionDep, quiz_in: QuizCreate,
        current_user: CurrentUser
):
    quiz = await crud.create_quiz_with_question(
        session=session, quiz=quiz_in,
        owner_id=current_user.id
    )
    return quiz

@router.get('/{quiz_id}', response_model=QuizRead)
async def get_quiz_by_id(
        session: SessionDep, quiz_id: uuid.UUID,
        current_user: CurrentUser
):
    quiz = await crud.get_quiz_by_id(session=session, quiz_id=quiz_id)
    if not quiz:
        raise HTTPException(status_code=404, detail='Quiz not found')
    if not current_user.is_superuser and current_user.id != quiz.owner_id:
        raise HTTPException(
            status_code=403,
            detail='The user doesn\'t have enough privileges'
        )
    return quiz

@router.patch('/{quiz_id}', response_model=QuizRead)
async def edit_quiz(
        session: SessionDep, quiz_id: uuid.UUID,
        update_data: QuizUpdate, current_user: CurrentUser
):
    stmt = (select(Quiz).where(Quiz.id == quiz_id)
            .options(selectinload(Quiz.questions)
                     .selectinload(Question.answers)))
    result = await session.exec(stmt)
    quiz = result.one_or_none()
    if not quiz:
        raise HTTPException(status_code=404, detail='Quiz not found')
    if current_user.id != quiz.owner_id and not current_user.is_superuser:
        raise HTTPException(
            status_code=403,
            detail='The user doesn\'t have enough privileges'
        )
    db_quiz = await crud.update_quiz(
        session=session, db_quiz=quiz, update_data=update_data
    )
    return db_quiz

@router.get('/user/{user_id}', response_model=list[QuizRead])
async def get_user_quizzes(
        session: SessionDep, user_id: uuid.UUID,
        current_user: CurrentUser
):
    quizzes = await crud.get_user_quizzes(
        session=session, user_id=user_id
    )
    if current_user.id != user_id:
        raise HTTPException(
            status_code=403,
            detail='The user doesn\'t have enough privileges'
        )
    if not quizzes:
        raise HTTPException(
            status_code=404, detail='Quizzes not found'
        )
    return quizzes