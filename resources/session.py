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

def _get_or_404_owned(session_id: int, owner_id: int) -> WorkoutSession:
    session = WorkoutSession.query.filter_by(id=session_id, user_id=owner_id).first()
    if session is None:
        from flask_restful import abort
        abort(404, message="Session not found")
    return session

class SessionList(Resource):
    @jwt_required()
    def get(self):
        user_id = int(get_jwt_identity())

        sessions = (
            WorkoutSession.query
            .filter_by(user_id=user_id)
            .join(ExerciseType, WorkoutSession.exercise_type_id == ExerciseType.id)
            .add_columns(ExerciseType.name.label("etype_name"))
            .order_by(WorkoutSession.date.desc())
            .all()
        )

        return [
            {
                'id': s.WorkoutSession.id,
                'exercise_type': s.etype_name,
                'duration': s.WorkoutSession.duration,
                'calories': s.WorkoutSession.calories,
                'date': s.WorkoutSession.date.isoformat(),
            }
            for s in sessions
        ], 200

    @jwt_required()
    def post(self):
        user_id = int(get_jwt_identity())
        args = create_parser.parse_args()

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
        user_id = int(get_jwt_identity())
        args = update_parser.parse_args()

        session = _get_or_404_owned(session_id, user_id)

        if args['duration'] is not None:
            session.duration = args['duration']
        if args['calories'] is not None:
            session.calories = args['calories']

        db.session.commit()
        return {'message': 'updated'}, 200

    @jwt_required()
    def delete(self, session_id):
        user_id = int(get_jwt_identity())
        session = _get_or_404_owned(session_id, user_id)

        db.session.delete(session)
        db.session.commit()
        return {'message': 'deleted'}, 204
