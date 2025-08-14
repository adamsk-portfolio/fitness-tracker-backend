from __future__ import annotations

from flask import current_app
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_restful import Resource, abort, reqparse
from sqlalchemy import func
from sqlalchemy.sql import literal

from ..extensions import db
from ..models import WorkoutSession
from ..utils.dates import current_window


def _map_range_to_period(rng: str) -> str:
    r = (rng or "").lower()
    if r in ("week", "weekly", "w"):
        return "weekly"
    if r in ("month", "monthly", "m"):
        return "monthly"
    abort(400, message="range must be one of: week, month")


DATE_FIELDS = (
    "created_at",
    "performed_at",
    "date",
    "session_date",
    "timestamp",
    "logged_at",
    "started_at",
    "start_time",
    "when",
    "dt",
)
MINUTES_FIELDS = (
    "minutes",
    "duration",
    "duration_min",
    "duration_minutes",
    "time_min",
    "time_minutes",
    "mins",
)
CALORIES_FIELDS = (
    "calories",
    "kcal",
    "kcals",
    "cal",
    "calories_burned",
    "cals",
)


def _pick_column(candidates: tuple[str, ...]):
    for name in candidates:
        col = getattr(WorkoutSession, name, None)
        if col is not None:
            return col, name
    return None, None


summary_parser = reqparse.RequestParser()
summary_parser.add_argument("range", type=str, default="week", location="args")
summary_parser.add_argument("exercise_type_id", type=int, required=False, location="args")


class SummaryReport(Resource):
    @jwt_required()
    def get(self):
        try:
            user_id = int(get_jwt_identity())
            args = summary_parser.parse_args()

            period = _map_range_to_period(args["range"])
            start_dt, end_dt = current_window(period)

            filters = [WorkoutSession.user_id == user_id]

            date_col, date_name = _pick_column(DATE_FIELDS)
            if date_col is not None:
                current_app.logger.info("SummaryReport: using date column '%s'", date_name)
                filters += [date_col >= start_dt, date_col <= end_dt]
            else:
                current_app.logger.warning(
                    "SummaryReport: NO date column found on WorkoutSession; "
                    "falling back to totals without date filtering."
                )

            etid = args.get("exercise_type_id")
            if etid is not None:
                filters.append(WorkoutSession.exercise_type_id == etid)

            minutes_col, minutes_name = _pick_column(MINUTES_FIELDS)
            if minutes_col is not None:
                current_app.logger.info("SummaryReport: using minutes column '%s'", minutes_name)
                minutes_expr = minutes_col
            else:
                current_app.logger.warning(
                    "SummaryReport: NO minutes-like column found; minutes will be 0."
                )
                minutes_expr = literal(0)

            calories_col, calories_name = _pick_column(CALORIES_FIELDS)
            if calories_col is not None:
                current_app.logger.info("SummaryReport: using calories column '%s'", calories_name)
                calories_expr = calories_col
            else:
                current_app.logger.warning(
                    "SummaryReport: NO calories-like column found; calories will be 0."
                )
                calories_expr = literal(0)

            minutes_sum = (
                db.session.query(func.coalesce(func.sum(minutes_expr), 0)).filter(*filters).scalar()
                or 0
            )
            calories_sum = (
                db.session.query(func.coalesce(func.sum(calories_expr), 0))
                .filter(*filters)
                .scalar()
                or 0
            )
            sessions_count = (
                db.session.query(func.count(WorkoutSession.id)).filter(*filters).scalar() or 0
            )

            return {
                "range": "week" if period == "weekly" else "month",
                "window": {"start": start_dt.isoformat(), "end": end_dt.isoformat()},
                "totals": {
                    "minutes": int(minutes_sum),
                    "calories": int(calories_sum),
                    "sessions": int(sessions_count),
                },
            }, 200

        except Exception:
            current_app.logger.exception("SummaryReport failed")
            abort(500, message="Internal Server Error")
