# Fitness Tracker — Backend (Flask API)

A REST API for tracking workouts — exercise types, sessions, goals, and progress charts.  
**Backend:** Flask (REST, SQLAlchemy, JWT, Google OAuth) • **Infra:** Docker + Alembic


## Highlights

- Email/password auth (JWT) **and** Google Sign-In (OAuth2/OIDC)
- Workout sessions: date, duration (min), calories, exercise type
- Goals with metrics (`duration`, `calories`, `sessions`) and windows (week / month / year)
- Dashboard with charts and quick progress overview
- Clean REST API (Flask-RESTful), DB migrations with Alembic/Flask-Migrate
- Production build via Docker Compose (Nginx serves the SPA and proxies the API)

---

## Tech Stack

**Backend:** Python 3.12, Flask 3, Flask-RESTful, SQLAlchemy 2, Flask-JWT-Extended, Authlib (Google), Flask-Migrate, Gunicorn  
**Frontend:** React + TypeScript + Vite, Material UI, Axios, React Router, Recharts  
**Infra:** Docker & Docker Compose, Nginx, SQLite by default (easy to switch to Postgres)

---

## Quick start (Docker)

1) Create a `.env` file in the repo root (see **Environment variables** below).

2) Build and start the stack:
```bash
docker compose up -d --build
````

3. Apply DB migrations:

```bash
docker compose exec backend flask --app backend.app db upgrade
```

4. Open the app:

* UI: **[http://localhost:8080](http://localhost:8080)**
* API: **[http://localhost:5000/api/](http://localhost:5000/api/)**

---

## Google Sign-In (OAuth)

1. In **Google Cloud Console → APIs & Services → Credentials**, create an **OAuth 2.0 Client ID** of type *Web application* with:

   * **Authorized JavaScript origins:** `http://localhost:8080`
   * **Authorized redirect URIs:** `http://localhost:5000/api/auth/google/callback`

2. Put the issued values into `.env` (`GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`).

3. Rebuild the backend so env vars are picked up:

```bash
docker compose up -d --build backend
```

4. On the login page click **“Sign in with Google”**. After success the backend redirects to
   `FRONTEND_OAUTH_REDIRECT` (defaults to `/login/oauth`) with a JWT access token.

---

## Environment variables (`.env`)

Minimal dev setup:

```env
# JWT
JWT_SECRET_KEY=super-dev-jwt-secret

# Flask session (OAuth uses cookies for state/nonce)
SECRET_KEY=super-dev-session-secret
SESSION_SAMESITE=Lax
SESSION_SECURE=False
SESSION_COOKIE_NAME=session

# Google OAuth
GOOGLE_CLIENT_ID=xxx.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=yyy
FRONTEND_OAUTH_REDIRECT=http://localhost:8080/login/oauth

# CORS
CORS_ORIGINS=http://localhost:8080

# Optional: database (defaults to SQLite file in container)
# DATABASE_URL=sqlite:////app/db/fitness.db
```

> **Production tips:** set `SESSION_SECURE=True` (HTTPS), use strong secrets, and store secrets outside of Git.

---

## Database migrations

Whenever you change models (see `backend/models.py`):

```bash
# generate a new migration
docker compose exec backend \
  flask --app backend.app db migrate -m "describe your change"

# apply migrations
docker compose exec backend \
  flask --app backend.app db upgrade
```

> With SQLite, prefer explicit constraint names and `op.batch_alter_table(...)` inside migrations.

---

## API (quick overview)

**Auth**

* `POST /api/auth/register` — email/password signup
* `POST /api/auth/login` — login, returns JWT
* `GET  /api/auth/google/login` — start Google OAuth
* `GET  /api/auth/google/callback` — OAuth callback → issues JWT and redirects to the frontend

**Exercise Types**

* `GET/POST /api/exercise-types`
* `GET/PUT/DELETE /api/exercise-types/:id`

**Sessions**

* `GET/POST /api/sessions`
* `GET/PUT/DELETE /api/sessions/:id`

**Goals**

* `GET/POST /api/goals`
* `GET/PUT/DELETE /api/goals/:id`

**Reports**

* `GET /api/reports/summary`

> **Auth header:** `Authorization: Bearer <JWT>`.

---
