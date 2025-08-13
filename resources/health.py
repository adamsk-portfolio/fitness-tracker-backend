from __future__ import annotations

from datetime import datetime, timezone

from flask import Blueprint, jsonify
from sqlalchemy import text

from ..extensions import db
from . import __name__ as pkg_name

bp = Blueprint("health", __name__)


@bp.get("/api/health")
def health():
    db_ok = True
    db_error = None
    try:
        db.session.execute(text("SELECT 1"))
    except Exception as exc:  # pragma: no cover
        db_ok = False
        db_error = str(exc)

    payload = {
        "status": "ok" if db_ok else "degraded",
        "time": datetime.now(tz=timezone.utc).isoformat(),
        "service": pkg_name or "fitness-tracker",
        "checks": {
            "database": {"ok": db_ok, "error": db_error},
        },
    }
    return jsonify(payload), (200 if db_ok else 503)
