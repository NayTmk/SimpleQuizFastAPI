import uuid
from fastapi import APIRouter, HTTPException

from app import crud
from app.api.deps import SessionDep, CurrentUser
from app.models import QuizCreate, QuizRead, Quiz, Message

router = APIRouter(prefix='/quizzes', tags=['quizzes'])


@router.post('/create-quiz', response_model=QuizRead)
async def create_quiz(
        session: SessionDep, quiz_in: QuizCreate,
        current_user: CurrentUser
):
    try:
        quiz = await crud.create_quiz_with_question(
            session=session, quiz=quiz_in,
            owner_id=current_user.id
        )
        return quiz
    except:
        raise HTTPException(400, 'Quiz can\'t be created')

@router.delete('/delete/{quiz_id}')
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
        raise HTTPException(status_code=404, detail='Quiz not found')
    return quizzes