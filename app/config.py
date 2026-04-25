import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "super-secret")

    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:postgres@localhost:5432/flask_ai"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "jwt-secret")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=15)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=7)

    AI_API_URL = os.getenv("AI_API_URL", "http://localhost:8000/ai/response-gemma")
    AI_RESPONSE_TIMEOUT = int(os.getenv("AI_RESPONSE_TIMEOUT", 600))
    REDIS_HOST = "localhost"
    REDIS_PORT = 6379


