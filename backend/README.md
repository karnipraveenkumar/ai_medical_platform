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
- Copy `.env.example` to `.env` in the `backend` folder and set values:

```text
DATABASE_URL=postgresql://postgres:password@localhost:5432/ai_medical_db
SECRET_KEY=your-secure-secret
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

**Database Setup**
- The application will create tables automatically on startup using SQLAlchemy `Base.metadata.create_all` (for the `app` entrypoint). For production, use Alembic migrations.

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
