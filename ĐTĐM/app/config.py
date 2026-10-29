# app/config.py
import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


def normalize_db_url(url: str | None) -> str:
    """Ensure DATABASE_URL uses postgresql+psycopg driver and handle Render postgres:// scheme."""
    if not url:
        return "postgresql+psycopg://task_user:task_password@localhost:5432/task_db"
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql+psycopg://", 1)
    elif url.startswith("postgresql://") and not url.startswith("postgresql+psycopg://"):
        url = url.replace("postgresql://", "postgresql+psycopg://", 1)
    return url


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-fallback-secret-key-change-me")
    APP_VERSION = os.getenv("APP_VERSION", "v1.0.0")
    GROUP_INVITE_CODE = os.getenv("GROUP_INVITE_CODE", "CLOUDTASK-GROUP-8")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = normalize_db_url(os.getenv("DATABASE_URL"))
    WTF_CSRF_ENABLED = True

    # Cookie & Session Security
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = os.getenv("SESSION_COOKIE_SECURE", "false").lower() in ("true", "1", "yes")


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = normalize_db_url(
        os.getenv(
            "TEST_DATABASE_URL",
            "postgresql+psycopg://task_user:task_password@localhost:5432/task_test_db",
        )
    )
    WTF_CSRF_ENABLED = False  # Allows cleaner programmatic testing while forms remain tested


class ProductionConfig(Config):
    DEBUG = False

    def __init__(self):
        super().__init__()
        secret = os.getenv("SECRET_KEY")
        if not secret or secret == "replace-with-a-secure-random-key-in-production":
            raise ValueError("SECRET_KEY environment variable must be set securely in production")
        self.SECRET_KEY = secret

        db_url = os.getenv("DATABASE_URL")
        if not db_url:
            raise ValueError("DATABASE_URL environment variable must be set in production")
        self.SQLALCHEMY_DATABASE_URI = normalize_db_url(db_url)
        self.SESSION_COOKIE_SECURE = True


config = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
