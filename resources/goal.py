from datetime import datetime

from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_restful import Resource, abort, reqparse
from sqlalchemy import or_

from ..extensions import db
from ..models import ExerciseType, Goal


def _positive_int(v):
    try:
        i = int(v)
    except Exception:
        abort(400, message="target_value must be an integer")
    if i <= 0:
        abort(400, message="target_value must be > 0")
    return i


def _parse_iso(d: str):
    if not d:
        return None
    try:
        if len(d) == 10:
            return datetime.fromisoformat(d + "T00:00:00")
        return datetime.fromisoformat(d)
    except Exception:
        abort(
            400,
            message="Invalid date format. Use YYYY-MM-DD or full ISO 8601.",
        )


create_parser = reqparse.RequestParser()
create_parser.add_argument(
    "description",
    type=str,
    required=True,
    location=("json", "form"),
)
create_parser.add_argument(
    "target_value",
    type=_positive_int,
    required=True,
    location=("json", "form"),
)
create_parser.add_argument(
    "period",
    type=str,
    required=True,
    location=("json", "form"),
)
create_parser.add_argument(
    "metric",
    type=str,
    required=True,
    location=("json", "form"),
)
create_parser.add_argument(
    "exercise_type_id",
    type=int,
    required=False,
    location=("json", "form"),
)
create_parser.add_argument(
    "start_date",
    type=str,
    required=False,
    location=("json", "form"),
)
create_parser.add_argument(
    "end_date",
    type=str,
    required=False,
    location=("json", "form"),
)

list_parser = reqparse.RequestParser()
list_parser.add_argument("page", type=int, default=1, location="args")
list_parser.add_argument("page_size", type=int, default=10, location="args")
list_parser.add_argument("metric", type=str, location="args")
list_parser.add_argument("period", type=str, location="args")
list_parser.add_argument("exercise_type_id", type=int, location="args")
list_parser.add_argument("from", type=str, dest="date_from", location="args")
list_parser.add_argument("to", type=str, dest="date_to", location="args")


update_parser = reqparse.RequestParser()
update_parser.add_argument(
    "description",
    type=str,
    required=False,
    location=("json", "form"),
)
update_parser.add_argument(
    "target_value",
    type=_positive_int,
    required=False,
    location=("json", "form"),
)
update_parser.add_argument(
    "period",
    type=str,
    required=False,
    location=("json", "form"),
)
update_parser.add_argument(
    "metric",
    type=str,
    required=False,
    location=("json", "form"),
)
update_parser.add_argument(
    "exercise_type_id",
    type=int,
    required=False,
    location=("json", "form"),
)
update_parser.add_argument(
    "start_date",
    type=str,
    required=False,
    location=("json", "form"),
)
update_parser.add_argument(
    "end_date",
    type=str,
    required=False,
    location=("json", "form"),
)


def _etype_owned_or_404(type_id: int, owner_id: int):
    et = ExerciseType.query.filter_by(id=type_id, user_id=owner_id).first()
    if et is None:
        abort(404, message="Exercise type not found")
    return et


class GoalList(Resource):
    @jwt_required()
    def get(self):
        user_id = int(get_jwt_identity())
        args = list_parser.parse_args()
        page = max(1, args["page"] or 1)
        page_size = min(max(1, args["page_size"] or 10), 100)

        q_obj = (
            db.session.query(Goal, ExerciseType.name.label("etype_name"))
            .outerjoin(ExerciseType, Goal.exercise_type_id == ExerciseType.id)
            .filter(Goal.user_id == user_id)
        )

        if args.get("metric"):
            metric = (args["metric"] or "").lower()
            if metric in {"duration", "calories", "sessions"}:
                q_obj = q_obj.filter(Goal.metric == metric)

        if args.get("period"):
            period = (args["period"] or "").lower()
            if period in {"weekly", "monthly", "yearly"}:
                q_obj = q_obj.filter(Goal.period == period)

        if args.get("exercise_type_id") is not None:
            q_obj = q_obj.filter(Goal.exercise_type_id == args["exercise_type_id"])

        df = args.get("date_from")
        dt = args.get("date_to")
        start_f = _parse_iso(df) if df else None
        end_t = _parse_iso(dt) if dt else None
        if start_f or end_t:
            if start_f and end_t:
                q_obj = q_obj.filter(
                    or_(Goal.start_date == None, Goal.start_date <= end_t)  # noqa: E711
                )
                q_obj = q_obj.filter(
                    or_(Goal.end_date == None, Goal.end_date >= start_f)  # noqa: E711
                )
            elif start_f:
                q_obj = q_obj.filter(
                    or_(Goal.end_date == None, Goal.end_date >= start_f)  # noqa: E711
                )
            elif end_t:
                q_obj = q_obj.filter(
                    or_(Goal.start_date == None, Goal.start_date <= end_t)  # noqa: E711
                )

        total = q_obj.count()

        rows = (
            q_obj.order_by(Goal.id.desc())
            .limit(page_size)
            .offset((page - 1) * page_size)
            .all()
        )

        items = [
            {
                "id": g.id,
                "description": g.description,
                "target_value": g.target_value,
                "period": g.period,
                "metric": g.metric,
                "start_date": g.start_date.isoformat() if g.start_date else None,
                "end_date": g.end_date.isoformat() if g.end_date else None,
                "exercise_type_id": g.exercise_type_id,
                "exercise_type": etype_name,
            }
            for (g, etype_name) in rows
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

        period = (args["period"] or "").lower()
        if period not in {"weekly", "monthly", "yearly"}:
            abort(400, message="period must be one of: weekly, monthly, yearly")

        metric = (args["metric"] or "").lower()
        if metric not in {"duration", "calories", "sessions"}:
            abort(400, message="metric must be one of: duration, calories, sessions")

        start_dt = _parse_iso(args.get("start_date")) if args.get("start_date") else None
        end_dt = _parse_iso(args.get("end_date")) if args.get("end_date") else None
        if start_dt and end_dt and start_dt > end_dt:
            abort(400, message="start_date must be <= end_date")

        etype_id = args.get("exercise_type_id")
        if etype_id is not None:
            _etype_owned_or_404(etype_id, user_id)

        goal = Goal(
            user_id=user_id,
            description=args["description"],
            target_value=args["target_value"],
            period=period,
            metric=metric,
            start_date=start_dt,
            end_date=end_dt,
            exercise_type_id=etype_id,
        )
        db.session.add(goal)
        db.session.commit()

        return {"id": goal.id}, 201


class GoalDetail(Resource):
    @jwt_required()
    def put(self, goal_id: int):
        user_id = int(get_jwt_identity())
        g = Goal.query.filter_by(id=goal_id, user_id=user_id).first()
        if not g:
            abort(404, message="Goal not found")

        args = update_parser.parse_args()

        if args.get("period") is not None:
            period = (args["period"] or "").lower()
            if period not in {"weekly", "monthly", "yearly"}:
                abort(400, message="period must be one of: weekly, monthly, yearly")
            g.period = period

        if args.get("metric") is not None:
            metric = (args["metric"] or "").lower()
            if metric not in {"duration", "calories", "sessions"}:
                abort(400, message="metric must be one of: duration, calories, sessions")
            g.metric = metric

        if args.get("description") is not None:
            g.description = args["description"]

        if args.get("target_value") is not None:
            g.target_value = args["target_value"]

        if args.get("exercise_type_id") is not None:
            etid = args.get("exercise_type_id")
            if etid is not None:
                _etype_owned_or_404(etid, user_id)
            g.exercise_type_id = etid

        new_start = g.start_date
        new_end = g.end_date
        if args.get("start_date") is not None:
            new_start = _parse_iso(args.get("start_date"))
        if args.get("end_date") is not None:
            new_end = _parse_iso(args.get("end_date"))
        if new_start and new_end and new_start > new_end:
            abort(400, message="start_date must be <= end_date")
        g.start_date = new_start
        g.end_date = new_end

        db.session.commit()

        et_name = None
        if g.exercise_type_id:
            et = ExerciseType.query.filter_by(
                id=g.exercise_type_id,
                user_id=user_id,
            ).first()
            et_name = et.name if et else None

        return {
            "id": g.id,
            "description": g.description,
            "target_value": g.target_value,
            "period": g.period,
            "metric": g.metric,
            "start_date": g.start_date.isoformat() if g.start_date else None,
            "end_date": g.end_date.isoformat() if g.end_date else None,
            "exercise_type_id": g.exercise_type_id,
            "exercise_type": et_name,
        }, 200

    @jwt_required()
    def delete(self, goal_id: int):
        user_id = int(get_jwt_identity())
        g = Goal.query.filter_by(id=goal_id, user_id=user_id).first()
        if not g:
            abort(404, message="Goal not found")
        db.session.delete(g)
        db.session.commit()
        return "", 204
