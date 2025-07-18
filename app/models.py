import uuid
from sqlmodel import SQLModel, Field, Relationship
from pydantic import EmailStr


class UserBase(SQLModel):
    email: EmailStr = Field(index=True, max_length=255)
    is_superuser: bool = False
    username: str = Field(max_length=256)


class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=64)


class UserRegister(SQLModel):
    email: EmailStr = Field(max_length=255)
    username: str = Field(max_length=64)
    password: str = Field(min_length=6)


class UserUpdatePassword(SQLModel):
    current_password: str = Field(min_length=8, max_length=64)
    new_password: str = Field(min_length=8, max_length=64)


class User(UserBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str
    quizzes: list['Quiz'] = Relationship(
        back_populates='owner', cascade_delete=True
    )


class UserPublic(UserBase):
    id: uuid.UUID


class QuizBase(SQLModel):
    title: str = Field(min_length=6, max_length=64)
    description: str | None = Field(
        nullable=True, default=None, max_length=64
    )


class QuizCreate(QuizBase):
    owner_id: uuid.UUID
    questions: list['QuestionCreate']


class QuizRead(QuizBase):
    owner_id: uuid.UUID
    questions: list['QuestionRead']


class QuizUpdate(QuizBase):
    title: str | None = Field(default=None, min_length=6, max_length=64)


class Quiz(QuizBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    owner_id: uuid.UUID = Field(foreign_key='user.id', ondelete='CASCADE')
    owner: 'User' = Relationship(back_populates='quizzes')
    questions: list['Question'] = Relationship(
        back_populates='quiz', cascade_delete=True
    )


class QuestionBase(SQLModel):
    question: str = Field(min_length=4, max_length=2048)


class QuestionCreate(QuestionBase):
    answers: list['AnswerCreate']

class QuestionRead(QuestionBase):
    id: uuid.UUID
    answers: list['AnswerRead']

class QuestionUpdate(QuestionBase):
    question: str | None = Field(
        default=None, min_length=4, max_length=2048
    )


class Question(QuestionBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    quiz_id: uuid.UUID = Field(foreign_key='quiz.id', ondelete='CASCADE')
    quiz: 'Quiz' = Relationship(back_populates='questions')
    answers: list['Answer'] = Relationship(back_populates='question')


class AnswerBase(SQLModel):
    text: str = Field(min_length=4, max_length=2048)
    is_correct: bool = Field(default=False)


class AnswerCreate(AnswerBase):
    pass

class AnswerRead(AnswerBase):
    id: uuid.UUID

class AnswerUpdate(AnswerBase):
    text: str | None = Field(default=None, min_length=4, max_length=2048)


class Answer(AnswerBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    question_id: uuid.UUID = Field(foreign_key='question.id', ondelete='CASCADE')
    question: 'Question' = Relationship(back_populates='answers')


class Token(SQLModel):
    access_token: str
    token_type: str = 'bearer'


class TokenPayload(SQLModel):
    sub: str | None = None


class Message(SQLModel):
    message: str