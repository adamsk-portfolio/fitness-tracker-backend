from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..extensions import db
from ..models import Goal

# --- parsery ---
create_parser = reqparse.RequestParser()
create_parser.add_argument('description',  required=True, help='description required')
create_parser.add_argument('target_value', type=int,   required=True)
create_parser.add_argument('period',       choices=('daily', 'weekly'), required=True)

update_parser = reqparse.RequestParser()
update_parser.add_argument('description')
update_parser.add_argument('target_value', type=int)
update_parser.add_argument('period',       choices=('daily', 'weekly'))

# --- zasoby ---
class GoalList(Resource):
    @jwt_required()
    def get(self):
        user_id = int(get_jwt_identity())
        goals = Goal.query.filter_by(user_id=user_id).all()
        return [{
            'id': g.id, 'description': g.description,
            'target_value': g.target_value, 'period': g.period
        } for g in goals], 200

    @jwt_required()
    def post(self):
        args = create_parser.parse_args()
        goal = Goal(
            user_id=int(get_jwt_identity()),
            description=args['description'],
            target_value=args['target_value'],
            period=args['period']
        )
        db.session.add(goal)
        db.session.commit()
        return {'id': goal.id}, 201


class GoalDetail(Resource):
    @jwt_required()
    def put(self, goal_id):
        args = update_parser.parse_args()
        goal = Goal.query.get_or_404(goal_id)

        if args['description'] is not None:
            goal.description = args['description']
        if args['target_value'] is not None:
            goal.target_value = args['target_value']
        if args['period'] is not None:
            goal.period = args['period']

        db.session.commit()
        return {'message': 'updated'}, 200

    @jwt_required()
    def delete(self, goal_id):
        goal = Goal.query.get_or_404(goal_id)
        db.session.delete(goal)
        db.session.commit()
        return {'message': 'deleted'}, 204
