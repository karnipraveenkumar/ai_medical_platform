**Overview**
- **Description:** AI Medical Platform backend (FastAPI) providing patient and authentication APIs.

**Prerequisites**
- **Python:** 3.10+ installed.
- **Database:** PostgreSQL (recommended) or SQLite for quick local testing.

**Dependency Installation**
- **Install from requirements:**

```bash
python -m venv backend/venv
backend\venv\Scripts\Activate.ps1    # PowerShell (Windows)
pip install -r backend/requirements.txt
```

**Environment Setup**
- Copy `.env.example` to `.env` in the `backend` folder and update the values for your local PostgreSQL instance.

```text
DATABASE_URL=postgresql+psycopg://postgres:password@localhost:5432/ai_medical_db
SECRET_KEY=your-secure-secret
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
APP_ENV=development
```

- Do not commit `.env`; it is local developer configuration only. The project loads environment variables using `python-dotenv` from `app/core/config.py`.

**Database Setup**
- The application is intended to run against PostgreSQL in development and production.
- Current configuration is active in `backend/app/core/config.py` and reads `DATABASE_URL` from `.env`.
- `app/main.py` imports all models before `Base.metadata.create_all(bind=engine)`, so table creation uses the configured PostgreSQL database.
- In production, prefer Alembic migrations instead of `create_all()`; `alembic` is already listed in requirements and `alembic.ini` exists, but migration configuration should be completed separately.

Postgres example (create DB and user):
```bash
# create database and user as needed (example using psql)
psql -U postgres -c "CREATE DATABASE ai_medical_db;"
```

**Running the Project**
- Start with Uvicorn (from repository root):

```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

API docs will be available at `http://127.0.0.1:8000/docs`.

**Running Tests**
- Run `pytest` from the `backend` directory after installing dev dependencies:

```bash
cd backend
pytest
```

**Notes**
- There are two directory trees present in this repository (`backend/api/...` and `backend/app/api/...`). The running application uses the `app` package (see `app/main.py`). Some files under `backend/api` appear to be duplicates or legacy copies—do not remove them without review.
