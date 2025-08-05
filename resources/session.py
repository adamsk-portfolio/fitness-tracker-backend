from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_restful import Resource, reqparse

from ..extensions import db
from ..models import ExerciseType, WorkoutSession

create_parser = reqparse.RequestParser()
create_parser.add_argument('exercise_type_id', type=int, required=True)
create_parser.add_argument('duration',         type=int, required=True)
create_parser.add_argument('calories',         type=int, required=True)

update_parser = reqparse.RequestParser()
update_parser.add_argument('duration', type=int)
update_parser.add_argument('calories', type=int)

class SessionList(Resource):
    @jwt_required()
    def get(self):
        user_id = int(get_jwt_identity())
        sessions = WorkoutSession.query.filter_by(user_id=user_id).all()
        return [
            {
                'id': s.id,
                'exercise_type': ExerciseType.query.get(s.exercise_type_id).name,
                'duration': s.duration,
                'calories': s.calories,
                'date': s.date.isoformat()
            } for s in sessions
        ], 200

    @jwt_required()
    def post(self):
        args = create_parser.parse_args()
        user_id = int(get_jwt_identity())

        session = WorkoutSession(
            user_id=user_id,
            exercise_type_id=args['exercise_type_id'],
            duration=args['duration'],
            calories=args['calories'],
        )
        db.session.add(session)
        db.session.commit()
        return {'id': session.id}, 201


class SessionDetail(Resource):
    @jwt_required()
    def put(self, session_id):
        args = update_parser.parse_args()
        session = WorkoutSession.query.get_or_404(session_id)

        if args['duration'] is not None:
            session.duration = args['duration']
        if args['calories'] is not None:
            session.calories = args['calories']

        db.session.commit()
        return {'message': 'updated'}, 200

    @jwt_required()
    def delete(self, session_id):
        session = WorkoutSession.query.get_or_404(session_id)
        db.session.delete(session)
        db.session.commit()
        return {'message': 'deleted'}, 204
