from __future__ import annotations

import logging

from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

log = logging.getLogger(__name__)

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()

oauth = None
try:
    from authlib.integrations.flask_client import OAuth as AuthlibOAuth  # type: ignore

    oauth = AuthlibOAuth()
    log.info("Authlib OAuth: initialized")
except Exception as exc:
    log.warning("Authlib OAuth not available: %r", exc)
    oauth = None
