from fastapi import APIRouter, HTTPException

from app import crud
from app.api.deps import SessionDep, CurrentUser
from app.models import QuizCreate, QuizRead

router = APIRouter(prefix='/quizzes', tags=['quizzes'])


@router.post('/create-quiz', response_model=QuizRead)
async def create_quiz(
        session: SessionDep, quiz_in: QuizCreate,
        current_user: CurrentUser
):
    quiz_create = quiz_in.model_validate(quiz_in)
    quiz = await crud.create_quiz_with_question(
        session=session, quiz=quiz_create,
        owner_id=current_user.id
    )
    return quiz
    # try:
    #     quiz_create = quiz_in.model_validate(quiz_in)
    #     quiz = await crud.create_quiz_with_question(
    #         session=session, quiz=quiz_create,
    #         owner_id=current_user.id
    #     )
    #     return quiz
    # except Exception as e:
    #     print(e)
    #     raise HTTPException(400, 'Quiz can\'t be created')

@router.delete('/delete/{quiz_id}')
async def delete_quiz():
    ...

@router.get('/{user_id}', response_model='')
async def get_user_quizzes():
    ...