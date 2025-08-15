from __future__ import annotations

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
SQLALCHEMY_DATABASE_URI: str = os.getenv(
    "DATABASE_URL",
    f"sqlite:///{BASE_DIR / 'fitness.db'}",
)
SQLALCHEMY_TRACK_MODIFICATIONS: bool = False

JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "dev-jwt-secret")

SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-session-secret")

SESSION_COOKIE_NAME: str = os.getenv("SESSION_COOKIE_NAME", "session")
SESSION_COOKIE_SAMESITE: str = os.getenv("SESSION_SAMESITE", "Lax")
SESSION_COOKIE_SECURE: bool = os.getenv("SESSION_SECURE", "False").lower() == "true"
SESSION_COOKIE_HTTPONLY: bool = True

GOOGLE_CLIENT_ID: str = os.getenv("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET: str = os.getenv("GOOGLE_CLIENT_SECRET", "")
FRONTEND_OAUTH_REDIRECT: str = os.getenv(
    "FRONTEND_OAUTH_REDIRECT",
    "http://localhost:8080/login/oauth",
)

CORS_ORIGINS: str = os.getenv("CORS_ORIGINS", "http://localhost:8080")

PREFERRED_URL_SCHEME: str = os.getenv("PREFERRED_URL_SCHEME", "http")
