from __future__ import annotations

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
SQLALCHEMY_DATABASE_URI: str = os.getenv(
    "DATABASE_URL", f"sqlite:///{BASE_DIR / 'fitness.db'}"
)
SQLALCHEMY_TRACK_MODIFICATIONS: bool = False
JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "dev-secret")
