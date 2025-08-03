from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required
from ..extensions import db
from ..models import ExerciseType

parser = reqparse.RequestParser()
parser.add_argument('name', required=True, help='name is required')

class ExerciseTypeList(Resource):
    @jwt_required()
    def get(self):
        types = ExerciseType.query.all()
        return [{'id': t.id, 'name': t.name} for t in types], 200

    @jwt_required()
    def post(self):
        args = parser.parse_args()
        if ExerciseType.query.filter_by(name=args['name']).first():
            return {'message': 'Exercise type already exists'}, 400
        typ = ExerciseType(name=args['name'])
        db.session.add(typ)
        db.session.commit()
        return {'id': typ.id, 'name': typ.name}, 201


class ExerciseTypeDetail(Resource):
    @jwt_required()
    def put(self, type_id):
        args = parser.parse_args()
        typ = ExerciseType.query.get_or_404(type_id)
        typ.name = args['name']
        db.session.commit()
        return {'id': typ.id, 'name': typ.name}, 200

    @jwt_required()
    def delete(self, type_id):
        typ = ExerciseType.query.get_or_404(type_id)
        db.session.delete(typ)
        db.session.commit()
        return {'message': 'deleted'}, 204
