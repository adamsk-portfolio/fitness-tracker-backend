from datetime import datetime, timedelta, timezone

from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_restful import Resource, abort, reqparse

from ..extensions import db
from ..models import ExerciseType, WorkoutSession


def _positive_int(v):
    if v is None:
        return None
    try:
        v = int(v)
    except (TypeError, ValueError):
        abort(400, message="Value must be an integer.")
    if v <= 0:
        abort(400, message="Value must be > 0.")
    return v


create_parser = reqparse.RequestParser()
create_parser.add_argument(
    "exercise_type_id",
    type=int,
    required=True,
    location=("json", "form"),
)
create_parser.add_argument(
    "duration",
    type=_positive_int,
    required=True,
    location=("json", "form"),
)
create_parser.add_argument(
    "calories",
    type=_positive_int,
    required=True,
    location=("json", "form"),
)
create_parser.add_argument(
    "date",
    type=str,
    required=False,
    location=("json", "form"),
)

update_parser = reqparse.RequestParser()
update_parser.add_argument(
    "duration",
    type=_positive_int,
    location=("json", "form"),
)
update_parser.add_argument(
    "calories",
    type=_positive_int,
    location=("json", "form"),
)

list_parser = reqparse.RequestParser()
list_parser.add_argument("page",      type=int, default=1,  location="args")
list_parser.add_argument("page_size", type=int, default=10, location="args")
list_parser.add_argument("type_id",   type=int, location="args")
list_parser.add_argument("date_from", type=str, location="args")
list_parser.add_argument("date_to",   type=str, location="args")



def _get_or_404_owned(session_id: int, owner_id: int) -> WorkoutSession:
    session = WorkoutSession.query.filter_by(id=session_id, user_id=owner_id).first()
    if session is None:
        abort(404, message="Session not found")
    return session


def _etype_owned_or_404(type_id: int, owner_id: int) -> ExerciseType:
    et = ExerciseType.query.filter_by(id=type_id, user_id=owner_id).first()
    if et is None:
        abort(404, message="Exercise type not found")
    return et


def _parse_iso(d: str) -> datetime:
    try:
        if len(d) == 10:
            dt = datetime.fromisoformat(d + "T00:00:00")
        else:
            dt = datetime.fromisoformat(d)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        else:
            dt = dt.astimezone(timezone.utc)
        return dt
    except Exception:
        abort(400, message="Invalid date format. Use ISO 8601 (YYYY-MM-DD or full ISO).")


def _to_iso(val):
    if not val:
        return None
    if isinstance(val, datetime):
        dt = val
    else:
        try:
            dt = datetime.fromisoformat(str(val))
        except Exception:
            return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    else:
        dt = dt.astimezone(timezone.utc)
    return dt.replace(microsecond=0).isoformat()


class SessionList(Resource):
    @jwt_required()
    def get(self):
        user_id = int(get_jwt_identity())
        args = list_parser.parse_args()

        page = max(1, args["page"] or 1)
        page_size = min(max(1, args["page_size"] or 10), 100)

        q = (
            db.session.query(WorkoutSession, ExerciseType.name.label("etype_name"))
            .join(ExerciseType, WorkoutSession.exercise_type_id == ExerciseType.id)
            .filter(WorkoutSession.user_id == user_id)
        )

        if args.get("type_id") is not None:
            q = q.filter(WorkoutSession.exercise_type_id == args["type_id"])

        if args.get("date_from"):
            q = q.filter(WorkoutSession.date >= _parse_iso(args["date_from"]))
        if args.get("date_to"):
            dt = _parse_iso(args["date_to"])
            q = q.filter(WorkoutSession.date < (dt + timedelta(days=1)))

        total = q.count()
        rows = (
            q.order_by(WorkoutSession.date.desc())
            .limit(page_size)
            .offset((page - 1) * page_size)
            .all()
        )

        items = [
            {
                "id": s.id,
                "exercise_type": etype_name,
                "duration": s.duration,
                "calories": s.calories,
                "date": _to_iso(s.date),
            }
            for (s, etype_name) in rows
        ]

        return {
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
        }, 200

    @jwt_required()
    def post(self):
        user_id = int(get_jwt_identity())
        args = create_parser.parse_args()

        _etype_owned_or_404(args["exercise_type_id"], user_id)

        dt = _parse_iso(args["date"]) if args.get("date") else None

        session = WorkoutSession(
            user_id=user_id,
            exercise_type_id=args["exercise_type_id"],
            duration=args["duration"],
            calories=args["calories"],
            date=dt or datetime.now(timezone.utc),
        )
        db.session.add(session)
        db.session.commit()

        return {"id": session.id}, 201


class SessionDetail(Resource):
    @jwt_required()
    def put(self, session_id: int):
        user_id = int(get_jwt_identity())
        args = update_parser.parse_args()

        session = _get_or_404_owned(session_id, user_id)

        if args["duration"] is not None:
            session.duration = args["duration"]
        if args["calories"] is not None:
            session.calories = args["calories"]

        db.session.commit()
        return {"message": "updated"}, 200

    @jwt_required()
    def delete(self, session_id: int):
        user_id = int(get_jwt_identity())
        session = _get_or_404_owned(session_id, user_id)

        db.session.delete(session)
        db.session.commit()
        return "", 204
