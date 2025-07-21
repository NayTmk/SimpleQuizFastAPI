import uuid
from fastapi import APIRouter, HTTPException
from app import crud
from app.api.deps import SessionDep, CurrentUser
from app.models import (
    QuestionRead, Question, QuestionUpdate, QuizQuestions,
    QuestionCreate, Message,
)

router = APIRouter(prefix='/questions', tags=['question'])

@router.get('/{question_id}', response_model=QuestionRead)
async def get_question(
        session: SessionDep, question_id: uuid.UUID,
        current_user: CurrentUser
):
    question = await crud.get_question_by_id(
        session=session, question_id=question_id
    )
    if not question:
        raise HTTPException(
            status_code=404, detail='Question not found'
        )
    if (
            not current_user.is_superuser
            and question.quiz.owner_id != current_user.id
    ):
        raise HTTPException(
            status_code=403, detail='The user doesn\'t have enough privileges'
        )
    return question

@router.get('/quiz/{quiz_id}', response_model=QuizQuestions)
async def get_questions_in_quiz(
        session: SessionDep, quiz_id: uuid.UUID,
        current_user: CurrentUser
):
    quiz = await crud.get_quiz_by_id(
        session=session, quiz_id=quiz_id
    )
    if not quiz:
        raise HTTPException(
            status_code=404, detail='Quiz not found'
        )
    if (
            not current_user.is_superuser
            and quiz.owner_id != current_user.id
    ):
        raise HTTPException(
            status_code=403, detail='The user doesn\'t have enough privileges'
        )
    return quiz

@router.post('/', response_model=QuestionRead)
async def create_question(
        session: SessionDep, question_in: QuestionCreate,
        current_user: CurrentUser
):
    quiz = await crud.get_quiz_by_id(
        session=session, quiz_id=question_in.quiz_id
    )
    if not quiz:
        raise HTTPException(
            status_code=404, detail='Quiz not found'
        )
    if current_user.id != quiz.owner_id:
        raise HTTPException(
            status_code=403, detail='The user doesn\'t have enough privileges'
        )
    new_question = await crud.question_create(
        session=session, question_data=question_in
    )
    return new_question

@router.delete('/{question_id}', response_model=Message)
async def delete_question(
        *, session: SessionDep, question_id: uuid.UUID,
        current_user: CurrentUser
):
    question_db = await crud.get_question_by_id(
        session=session, question_id=question_id
    )
    if not question_db:
        raise HTTPException(
            status_code=404, detail='Question not found'
        )
    if (
            question_db.quiz.owner_id != current_user.id
            and not current_user.is_superuser
    ):
        raise HTTPException(
            status_code=403,
            detail='The user doesn\'t have enough privileges'
        )
    await session.delete(question_db)
    await session.commit()
    return Message(message='Question deleted successfully')

@router.patch('/{question_id}', response_model=QuestionRead)
async def edit_question(
        session: SessionDep, question_id: uuid.UUID,
        update_data: QuestionUpdate, current_user: CurrentUser
):
    db_question = await crud.get_question_by_id(
        session=session, question_id=question_id
    )
    if not db_question:
        raise HTTPException(
            status_code=404, detail='Question not found'
        )
    if (
            db_question.quiz.owner_id != current_user.id
            and not current_user.is_superuser
    ):
        raise HTTPException(
            status_code=403, detail='The user doesn\'t have enough privileges'
        )
    db_question = await crud.update_question(
        session=session, db_question=db_question, update_data=update_data
    )
    return db_question