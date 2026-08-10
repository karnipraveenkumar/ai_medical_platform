# AI Medical Platform — Frontend/Backend Integration Notes

This frontend (`index.html` / `script.js` / `styles.css`) has been connected to the
real FastAPI backend at `backend/app/main.py`. The UI layout/design was **not**
changed — only a login/register screen was added (there was none before), and
existing buttons/forms were rewired to call real endpoints where a matching
backend route exists.

## 1. How to run

### Backend
```bash
cd ai_medical_platform/backend
python -m venv venv
# Windows: venv\Scripts\Activate.ps1        macOS/Linux: source venv/bin/activate
pip install -r requirements.txt

# Copy .env.example -> .env and fill in DATABASE_URL, SECRET_KEY, GROQ_API_KEY, etc.
# (Postgres is expected: postgresql+psycopg://user:pass@localhost:5432/ai_medical_db)

uvicorn app.main:app --reload --port 8000
```
API docs: http://127.0.0.1:8000/docs

### Frontend
This is a static site — any static file server works. From the frontend folder:
```bash
python -m http.server 5500
# then open http://127.0.0.1:5500
```
Or just double-click `index.html` (file:// also works, since CORS is now open).

If your backend runs somewhere other than `http://127.0.0.1:8000`, set it before
`script.js` loads by adding this in `index.html`'s `<head>`:
```html
<script>window.API_BASE_URL = "http://your-backend-host:8000";</script>
```

## 2. What's actually connected to the backend now

| Feature | Backend route used | Notes |
|---|---|---|
| Register | `POST /auth/register` | JSON body `{full_name, email, password}` |
| Login | `POST /auth/login` | Backend uses `OAuth2PasswordRequestForm` → sent as `application/x-www-form-urlencoded` with `username`/`password`, not JSON. JWT stored in `localStorage`. |
| Logout | (client-side only) | Clears the stored token. Available from the Patient Profile modal. |
| Patient Profile (view/edit) | `GET/POST/PUT /patients` | On login, the app fetches the user's own patient record. Saving the Edit Profile form creates it (`POST`) if it doesn't exist yet, or updates it (`PUT`) if it does. Records are scoped to the logged-in user via JWT. |
| My Doctors (sidebar) | `GET /doctors` | Renders the real doctor list from the DB. |
| Book Appointment — doctor dropdown | `GET /doctors` | The dropdown options are populated from real doctors; **the booking submit itself is still local-only** (see below — no backend route exists for it). |
| AI Symptom Checker | `POST /ai/complete` | Sends your symptoms as a prompt to the single generic completion endpoint (Groq-backed) and renders the real model output. There's no dedicated symptom-checker endpoint that returns structured "% match" data, so the old fake progress bars were replaced with the actual AI text response. |
| AI Chat Assistant | `POST /ai/complete` | Same generic endpoint, called per-message (no server-side conversation memory exists). |

All requests attach `Authorization: Bearer <token>` automatically once you're logged in.

## 3. What is still frontend-only / mocked (no backend route exists)

The original demo used local mock data / `setTimeout` fakes for these features.
They were **left as-is** rather than faking a "connected" look, per the instruction
not to invent backend APIs. Wiring them up requires backend work first:

- **Appointments** (booking, reschedule, cancel) — no `/appointments` router is
  mounted in `app/main.py`. There *is* an unused `backend/api/appointments/`
  folder in the repo, but it is legacy/dead code (confirmed by the backend's own
  README: "the running application uses the `app` package"). Needs a real
  `appointments` router wired into `app/main.py`, backed by a DB model/table.
- **Medical Records** — a `MedicalRecord` SQLAlchemy model exists
  (`app/models/medical_record.py`) but there is **no route/service/schema** for
  it anywhere in the active `app` package. Needs CRUD endpoints added.
- **Lab Reports** — no model, route, or table at all.
- **Prescriptions** — no model, route, or table at all.
- **Billing & Payments** — no model, route, or table at all.
- **Notifications** — no model, route, or table at all.
- **Health Trend chart** — purely presentational demo data; no time-series
  health-metric endpoint exists to source it from.

## 4. Other gaps worth knowing about

- **No `GET /auth/me` (current-user) endpoint.** After login we only know what's
  in the JWT (`user_id`, `email`) — there's no way to fetch the logged-in user's
  `full_name`/`role`/`is_active` from a dedicated endpoint. The app currently
  falls back to the linked Patient record's name once one exists. Adding
  `GET /auth/me` would make this more robust (e.g. for the Doctor/Admin role
  switcher, which is still cosmetic — the backend has no role-based dashboards).
- **`GET /doctors` and doctor CRUD have no authentication.** Anyone can list,
  create, edit, or delete doctors without logging in. That's a backend
  authorization gap, not something the frontend can fix.
- **Blood group / emergency contact / address fields** shown in the Profile
  modal have no matching column on the `Patient` model — they're kept
  client-side only (not persisted) until the backend schema is extended.
- **CORS**: the backend had no CORS middleware at all, which would block every
  browser request from a static frontend. A minimal, permissive
  `CORSMiddleware` (`allow_origins=["*"]`) was added to `app/main.py` — the only
  backend change made, and required for the frontend to reach the API at all.
  Tighten this to your actual frontend origin before deploying.

## 5. Files changed
- `index.html` — added the login/register screen markup only; existing
  dashboard markup is unchanged (a `#app-container` id was added so JS can
  show/hide it after login).
- `styles.css` — added styles for the new auth screen only, reusing existing
  design tokens (`--primary-blue`, `--radius-*`, etc.). No existing rules were
  modified.
- `script.js` — added the API layer (`apiFetch`, auth flows) and rewired
  Symptom Checker, AI Chat, Profile, My Doctors, and the Book Appointment
  doctor list to call real endpoints. Everything else is untouched.
- `../ai_medical_platform/backend/app/main.py` — added CORS middleware only
  (see above). No other backend files were modified.
