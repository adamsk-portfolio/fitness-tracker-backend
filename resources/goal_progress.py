from __future__ import annotations

from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_restful import Resource, abort

from ..models import Goal
from ..utils.progress import compute_goal_progress


class GoalProgress(Resource):
    @jwt_required()
    def get(self, goal_id: int):
        user_id = int(get_jwt_identity())
        goal = Goal.query.filter_by(id=goal_id, user_id=user_id).first()
        if not goal:
            abort(404, message="Goal not found")

        pr = compute_goal_progress(goal)
        return {"goal_id": goal.id, "progress": pr.as_dict()}, 200
