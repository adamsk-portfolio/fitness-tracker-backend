from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

import pytest

_here = Path(__file__).resolve()
candidates = [_here.parents[2], _here.parents[1]]
for c in candidates:
    if c.exists() and str(c) not in sys.path:
        sys.path.insert(0, str(c))

try:
    from backend import models as _models
    from backend.app import create_app
    from backend.extensions import db as _db
except Exception:
    import models as _models
    from app import create_app
    from extensions import db as _db


@pytest.fixture(scope="function")
def app():
    fd, db_path = tempfile.mkstemp()
    app = create_app()
    app.config.update(
        TESTING=True,
        SQLALCHEMY_DATABASE_URI=f"sqlite:///{db_path}",
        JWT_SECRET_KEY="test-secret",
        WTF_CSRF_ENABLED=False,
    )
    with app.app_context():
        _ = _models
        _db.create_all()
    try:
        yield app
    finally:
        with app.app_context():
            _db.session.remove()
            _db.drop_all()
        os.close(fd)
        os.unlink(db_path)


@pytest.fixture(scope="function")
def client(app):
    return app.test_client()
