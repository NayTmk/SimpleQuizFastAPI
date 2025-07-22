from fastapi import APIRouter
from .routers import (
    users, login, quizzes,
    questions, answers
)

api_router = APIRouter()
api_router.include_router(users.router)
api_router.include_router(login.router)
api_router.include_router(quizzes.router)
api_router.include_router(questions.router)
api_router.include_router(answers.router)