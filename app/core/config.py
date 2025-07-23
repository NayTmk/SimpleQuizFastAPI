from pydantic import EmailStr
from pydantic_settings import BaseSettings
import sqlmodel


class Settings(BaseSettings):
    PROJECT_NAME: str

    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_HOST: str
    POSTGRES_PORT: str

    DATABASE_URL: str

    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    FIRST_USER: str
    FIRST_USER_EMAIL: EmailStr
    FIRST_USER_PASSWORD: str
    class Config:
        env_file = '.env'


settings = Settings()