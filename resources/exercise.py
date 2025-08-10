from __future__ import annotations

from flask import abort
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_restful import Resource, reqparse

from ..extensions import db
from ..models import ExerciseType

_parser = reqparse.RequestParser()
_parser.add_argument("name", required=True, help="name is required")

def _get_owned_or_404(type_id: int, owner_id: int) -> ExerciseType:
    typ = ExerciseType.query.filter_by(id=type_id, user_id=owner_id).first()
    if typ is None:
        abort(404, description="Exercise type not found")
    return typ

class ExerciseTypeList(Resource):
    @jwt_required()
    def get(self):
        uid = int(get_jwt_identity())
        types = ExerciseType.query.filter_by(user_id=uid).all()
        return [{"id": t.id, "name": t.name} for t in types], 200

    @jwt_required()
    def post(self):
        uid = int(get_jwt_identity())
        args = _parser.parse_args()

        exists = ExerciseType.query.filter_by(
            user_id=uid, name=args["name"]
        ).first()
        if exists:
            return {"message": "Exercise type already exists"}, 400

        typ = ExerciseType(user_id=uid, name=args["name"])
        db.session.add(typ)
        db.session.commit()
        return {"id": typ.id, "name": typ.name}, 201

class ExerciseTypeDetail(Resource):
    @jwt_required()
    def put(self, type_id: int):
        uid = int(get_jwt_identity())
        args = _parser.parse_args()
        typ = _get_owned_or_404(type_id, uid)

        typ.name = args["name"]
        db.session.commit()
        return {"id": typ.id, "name": typ.name}, 200

    @jwt_required()
    def delete(self, type_id: int):
        uid = int(get_jwt_identity())
        typ = _get_owned_or_404(type_id, uid)

        db.session.delete(typ)
        db.session.commit()
        return {"message": "deleted"}, 204
