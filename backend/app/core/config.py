import os
from pathlib import Path
from urllib.parse import quote_plus

from dotenv import load_dotenv


env_path = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(env_path)


def _build_database_url() -> str:
    # If a full DATABASE_URL is provided, prefer it (assumed to be properly
    # encoded by the environment). Otherwise build one from individual parts
    # and safely encode the password.
    env_url = os.getenv("DATABASE_URL")
    if env_url:
        return env_url

    user = os.getenv("POSTGRES_USER", "postgres")
    password = os.getenv("POSTGRES_PASSWORD", "admin123")
    host = os.getenv("POSTGRES_HOST", "localhost")
    port = os.getenv("POSTGRES_PORT", "5432")
    db = os.getenv("POSTGRES_DB", "ai_medical")

    encoded_password = quote_plus(password)
    return f"postgresql+psycopg://{user}:{encoded_password}@{host}:{port}/{db}"


class Settings:
    APP_NAME: str = "AI Medical Platform"
    DATABASE_URL: str = _build_database_url()
    SECRET_KEY: str = os.getenv(
        "SECRET_KEY",
        "dev-secret-change-me",
    )
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
        os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60")
    )


settings = Settings()
