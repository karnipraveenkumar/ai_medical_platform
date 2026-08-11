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
        if env_url.startswith("postgresql://"):
            return env_url.replace("postgresql://", "postgresql+psycopg://", 1)
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

# Validate SECRET_KEY only for non-development environments to avoid
# breaking local dev or tests. Consumers should set APP_ENV to
# "production" or "staging" in those deployments.
_app_env = os.getenv("APP_ENV", "development").lower()
if _app_env in ("production", "staging"):
    # Do not expose the secret value in error messages or logs.
    _secret = settings.SECRET_KEY
    if not _secret or _secret == "dev-secret-change-me" or len(_secret) < 32:
        raise RuntimeError(
            "SECRET_KEY is not configured for production/staging. "
            "Set a strong SECRET_KEY via environment variables."
        )
