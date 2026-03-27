# ACCESSRIDE

Web app to connect people with disabilities with volunteer helpers.

This project has:
- `back/` - Python FastAPI backend
- `front/` - SvelteKit frontend

---

## Prerequisites

- Python 3.10+ (3.12 recommended)
- Node.js 18+ and npm
- A PostgreSQL database (Supabase Postgres works)

---

## 1) Backend setup (`back/`)

### Install dependencies

```bash
cd back
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install bcrypt<4.0.0 # ENSURE FORCING OLDER BCRYPT
```

### Create backend `.env`

Create `back/.env`:

```env
DATABASE_URL=postgresql://<user>:<password>@<host>:<port>/<db>

JWT_SECRET=change-me
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=60

# Optional: only needed if AI helper endpoint is enabled
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-1.5-flash
```

### Run backend

```bash
cd back
source .venv/bin/activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be available at:
- API: `http://localhost:8000`
- Swagger docs: `http://localhost:8000/docs`

---

## 2) Frontend setup (`front/`)

### Install dependencies

```bash
cd front
npm install
```

### Create frontend `.env`

Create `front/.env`:

```env
PUBLIC_API_URL=http://localhost:8000

# Optional for Supabase client usage in frontend
PUBLIC_SUPABASE_URL=https://<your-project-ref>.supabase.co
PUBLIC_SUPABASE_ANON_KEY=<your-anon-key>
```

### Run frontend

```bash
cd front
npm run dev
```

Frontend will be available at:
- App: `http://localhost:5173`

---

## 3) Running both services

Use two terminals:

- Terminal A:
  - `cd efn/back`
  - `source .venv/bin/activate`
  - `uvicorn main:app --reload --host 0.0.0.0 --port 8000`

- Terminal B:
  - `cd efn/front`
  - `npm run dev`

---

## Useful commands

### Frontend

```bash
cd front
npm run check
npm run build
```

### Backend quick syntax check

```bash
cd back
python3 -m py_compile main.py
```

---

## Common issues

- `DATABASE_URL is missing`:
  - Verify `back/.env` exists and contains `DATABASE_URL`.

- Frontend cannot call backend:
  - Verify backend is running on port `8000`.
  - Verify `PUBLIC_API_URL=http://localhost:8000` in `front/.env`.
  - Restart frontend after editing `.env`.

- `ModuleNotFoundError` in backend:
  - Activate venv and re-run `pip install -r requirements.txt`.

- Svelte env var errors:
  - Make sure all `PUBLIC_*` vars used in code are defined in `front/.env`.

---

## Security note

Do not commit real secrets in `.env` files.  
If any key/token was accidentally committed, rotate it in Supabase/Gemini and replace it locally.

