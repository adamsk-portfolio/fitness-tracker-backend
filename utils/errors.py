from __future__ import annotations

import logging

from flask import jsonify, request
from werkzeug.exceptions import HTTPException

log = logging.getLogger(__name__)


def register_error_handlers(app) -> None:
    @app.errorhandler(HTTPException)
    def _http_error(exc: HTTPException):
        payload = {
            "error": exc.name,
            "message": exc.description,
            "status": exc.code,
            "path": request.path,
        }
        return jsonify(payload), exc.code

    @app.errorhandler(Exception)
    def _unhandled(exc: Exception):  # pragma: no cover
        log.exception("Unhandled error on %s", request.path)
        payload = {
            "error": "Internal Server Error",
            "message": "Unexpected server error.",
            "status": 500,
            "path": request.path,
        }
        return jsonify(payload), 500
