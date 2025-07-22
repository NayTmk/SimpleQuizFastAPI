from fastapi import APIRouter, HTTPException
import uuid
from app import crud
from app.api.deps import SessionDep, CurrentUser
from app.crud import get_question_by_id
from app.models import (
    AnswerRead, AnswerUpdate, AnswerCreate,
    Message, QuestionAnswers,
)

router = APIRouter(prefix='/answers', tags=['answers'])

@router.post('/', response_model=AnswerRead)
async def create_answer(
        session: SessionDep, answer_in: AnswerCreate,
        current_user: CurrentUser
):
    question = await get_question_by_id(
        session=session, question_id=answer_in.question_id
    )
    if not question:
        raise HTTPException(
            status_code=404, detail='Question not found'
        )
    if question.quiz.owner_id != current_user.id:
        raise HTTPException(
            status_code=404,
            detail='The user doesn\'t have enough privileges'
        )
    answer = await crud.create_answer(
        session=session, answer_in=answer_in,
    )
    return answer

@router.get('/{answer_id}', response_model=AnswerRead)
async def get_answer(
        session: SessionDep, answer_id: uuid.UUID,
        current_user: CurrentUser
):
    answer = await crud.get_answer_by_id(
        session=session, answer_id=answer_id
    )
    if not answer:
        raise HTTPException(
            status_code=404, detail='Answer not found'
        )
    if (
            current_user.id != answer.question.quiz.owner_id
            and not current_user.is_superuser
    ):
        raise HTTPException(
            status_code=403,
            detail='The user doesn\'t have enough privileges'
        )
    return answer

@router.get('/question/{question_id}', response_model=QuestionAnswers)
async def get_answer_in_question(
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
    if question.quiz.owner_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=403,
            detail='The user doesn\'t have enough privileges'
        )
    return question

@router.delete('/{answer_id}', response_model=Message)
async def delete_answer(
        session: SessionDep, answer_id: uuid.UUID,
        current_user: CurrentUser
):
    answer = await crud.get_answer_by_id(
        session=session, answer_id=answer_id
    )
    if not answer:
        return HTTPException(
            status_code=404, detail='Answer not found'
        )
    if (
            current_user.id != answer.question.quiz.owner_id
            and not current_user.is_superuser
    ):
        return HTTPException(
            status_code=403,
            detail='The user doesn\'t have enough privileges'
        )
    await session.delete(answer)
    await session.commit()
    return Message(message='Answer deleted successfully')

@router.patch('/{answer_id}', response_model=AnswerRead)
async def edit_answer(
        session: SessionDep, answer_id: uuid.UUID,
        update_data: AnswerUpdate, current_user: CurrentUser
):
    db_answer = await crud.get_answer_by_id(
        session=session, answer_id=answer_id
    )
    if not db_answer:
        raise HTTPException(
            status_code=404, detail='Answer not found'
        )
    if (
            db_answer.question.quiz.owner_id != current_user.id
            and not current_user.is_superuser
    ):
        raise HTTPException(
            status_code=403,
            detail='The user doesn\'t have enough privileges'
        )
    answer = await crud.update_answer(
        session=session, db_answer=db_answer,
        update_data=update_data
    )
    return answer