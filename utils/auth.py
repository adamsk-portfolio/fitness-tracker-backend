from flask_jwt_extended import get_jwt_identity
from flask_restful import abort


def current_user_id() -> int:
    ident = get_jwt_identity()
    try:
        return int(ident)
    except Exception:
        abort(401, message="Invalid token identity")
