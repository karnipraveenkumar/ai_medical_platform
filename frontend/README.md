# Careflow Hospital Platform — Frontend

Responsive React + TypeScript + Vite frontend designed to integrate with the uploaded FastAPI backend.

## Features

- Admin, Doctor, and Patient dashboard previews (role switcher in the top bar)
- Hospital overview with KPI cards, visits trends, department breakdown, revenue chart, and appointment table
- Login and registration connected to the current FastAPI auth endpoints
- Patients and Doctors directories connected to `GET /patients/` and `GET /doctors/`
- AI assistant connected to `POST /ai/complete`
- Responsive desktop and mobile sidebar
- Clear sample-data labels and API error/loading states

## Requirements

- Node.js 20+ recommended
- FastAPI backend running at `http://127.0.0.1:8000`

## Start the frontend

```bash
cd frontend
npm install
copy .env.example .env
npm run dev
```

Open the Vite URL, usually `http://localhost:5173`.

On macOS/Linux, copy the environment file with `cp .env.example .env` instead of `copy`.

Set `VITE_API_URL` in `.env` if the backend runs at a different URL:

```env
VITE_API_URL=http://127.0.0.1:8000
```

## Start the backend

From the existing backend directory, activate its virtual environment and run:

```bash
uvicorn app.main:app --reload --port 8000
```

API docs: `http://127.0.0.1:8000/docs`

## Current API integration

| Frontend feature | Backend endpoint | Integration |
|---|---|---|
| Login | `POST /auth/login` | Connected using OAuth2 form fields `username` and `password` |
| Registration | `POST /auth/register` | Connected using JSON |
| Patient directory | `GET /patients/` | Connected; backend requires a valid bearer token |
| Doctor directory | `GET /doctors/` | Connected; based on the current uploaded backend this endpoint is not authenticated |
| AI assistant | `POST /ai/complete` | Connected using `{ "prompt": "..." }` |
| Health indicator | `GET /health` | API utility available |

## Important backend integration notes

1. The current login response only contains `access_token` and `token_type`. It does not return the user's role or a `/auth/me` endpoint. The top-bar role selector is therefore a **UI preview only**, not an authentication or authorization boundary.
2. Registration currently accepts `full_name`, `email`, and `password`; there is no role field in the schema. Role-based authorization must be implemented and enforced by FastAPI before production use.
3. Appointment, billing, medical-record, analytics and lab-report screens are frontend foundations with clearly identified sample UI. The uploaded backend does not yet expose all the APIs needed to persist those features.
4. Dashboard KPI values and charts are illustrative sample data, not actual hospital metrics. Directory pages and AI responses use live backend requests.
5. The backend currently has both `backend/api/...` and `backend/app/api/...` trees. Its README says `app.main:app` is the active application; this frontend was integrated against the routes in `backend/app/main.py`.
6. The backend must configure CORS for `http://localhost:5173` (and `http://127.0.0.1:5173` if used). If browser requests fail with a CORS message, add FastAPI `CORSMiddleware` to `app/main.py` and allow the development origin.
7. Healthcare data is sensitive. Use synthetic data during development and enforce server-side authorization, audit logging, HTTPS, and secure token handling before deployment.

## Build for production

```bash
npm run build
npm run preview
```

The production bundle is generated in `dist/`.
