import uuid

import sqlmodel

from app.core.security import get_hashed_password, verify_password
from sqlmodel import select
from sqlalchemy.orm import selectinload, joinedload
from app.api.deps import SessionDep
from app.models import (
    User, UserCreate, UserUpdatePassword,
    QuizCreate, Quiz, QuizUpdate, QuestionUpdate,
    QuestionCreate, Question,
    AnswerCreate, Answer, AnswerUpdate
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

async def clean_quiz_create(
        *, session: SessionDep,
        quiz: QuizCreate, owner_id: uuid.UUID
) -> Quiz:
    db_obj = Quiz.model_validate(quiz, update={'owner_id': owner_id})
    session.add(db_obj)
    await session.commit()
    await session.refresh(db_obj)
    return db_obj

async def create_quiz_with_question(
        *, session: SessionDep, quiz: QuizCreate, owner_id: uuid.UUID
) -> Quiz:
    questions = []
    for question in quiz.questions:
        answers = [
            Answer(
                text=answer.text, is_correct=answer.is_correct
            ) for answer in question.answers
        ]
        questions.append(Question(question=question.question, answers=answers))
    db_quiz = Quiz(
        title=quiz.title, description=quiz.description,
        owner_id=owner_id, questions=questions
    )
    session.add(db_quiz)
    await session.commit()
    await session.refresh(db_quiz)
    quiz_id = db_quiz.id
    result = await session.exec(
        select(Quiz).where(Quiz.id==quiz_id)
        .options(
            selectinload(Quiz.questions).selectinload(Question.answers)
        )
    )
    quiz_with_question = result.one()
    return quiz_with_question

async def get_user_quizzes(
        *, session: SessionDep, user_id: uuid.UUID
) -> list[Quiz]:
    stmt = select(Quiz).where(
        Quiz.owner_id == user_id).options(
        selectinload(Quiz.questions).selectinload(Question.answers)
    )
    quizzes = await session.scalars(stmt)
    return quizzes

async def get_quiz_by_id(
        *, session: SessionDep, quiz_id: uuid.UUID
) -> Quiz:
    stmt = select(Quiz).where(Quiz.id==quiz_id).options(
        selectinload(Quiz.questions).selectinload(Question.answers)
    )
    result = await session.exec(stmt)
    quiz = result.one()
    return quiz

async def update_quiz(
        *, session: SessionDep, db_quiz: Quiz,
        update_data: QuizUpdate
) -> Quiz:
    quiz_data = update_data.model_dump(exclude_unset=True)
    db_quiz.sqlmodel_update(quiz_data)
    session.add(db_quiz)
    await session.commit()
    await session.refresh(db_quiz)
    return db_quiz

async def question_create(
        *, session: SessionDep, question_data: QuestionCreate,
) -> Question:
    answers = []
    if question_data.answers:
        for ans in question_data.answers:
            answer = Answer(
                text=ans.text, is_correct=ans.is_correct
            )
            answers.append(answer)
    question = Question(
        question=question_data.question,
        quiz_id=question_data.quiz_id,
        answers=answers
    )
    session.add(question)
    await session.commit()
    await session.refresh(question)
    return await get_question_by_id(
        session=session, question_id=question.id
    )

async def get_question_by_id(
        *, session: SessionDep, question_id: uuid.UUID
) -> Question | None:
    stmt = (
        select(Question)
        .where(Question.id == question_id)
        .options(
            selectinload(Question.quiz),
            selectinload(Question.answers)
        )
    )
    result = await session.exec(stmt)
    question = result.one_or_none()
    return question

async def update_question(
        *, session: SessionDep, db_question: Question,
        update_data: QuestionUpdate
) -> Question:
    question_data = update_data.model_dump(exclude_unset=True)
    db_question.sqlmodel_update(question_data)
    session.add(db_question)
    await session.commit()
    await session.refresh(db_question)
    return db_question

async def get_answer_by_id(
        *, session: SessionDep, answer_id: uuid.UUID
) -> Answer | None:
    stmt = (
        select(Answer)
        .where(Answer.id == answer_id)
        .options(
            joinedload(Answer.question)
            .joinedload(Question.quiz)
        )
    )
    result = await session.exec(stmt)
    answer = result.one_or_none()
    return answer

async def update_answer(
        *, session: SessionDep, db_answer: Answer,
        update_data: AnswerUpdate
) -> Answer:
    answer_data = update_data.model_dump(exclude_unset=True)
    db_answer.sqlmodel_update(answer_data)
    session.add(db_answer)
    await session.commit()
    await session.refresh(db_answer)
    return db_answer

async def create_answer(
        *, session: SessionDep, answer_in: AnswerCreate,
) -> Answer:
    answer = Answer(
        text=answer_in.text,
        is_correct=answer_in.is_correct,
        question_id=answer_in.question_id
    )
    session.add(answer)
    await session.commit()
    await session.refresh(answer)
    return answer