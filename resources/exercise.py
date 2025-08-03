from __future__ import annotations

from flask import abort
from flask_jwt_extended import jwt_required
from flask_restful import Resource, reqparse

from ..extensions import db
from ..models import ExerciseType

_parser = reqparse.RequestParser()
_parser.add_argument("name", required=True, help="name is required")

def _get_type_or_404(type_id: int) -> ExerciseType:
    instance: ExerciseType | None = db.session.get(ExerciseType, type_id)
    if instance is None:
        abort(404, description="Exercise type not found")
    return instance

class ExerciseTypeList(Resource):
    @jwt_required()
    def get(self):
        types = db.session.scalars(db.select(ExerciseType)).all()
        return [{"id": t.id, "name": t.name} for t in types], 200

    @jwt_required()
    def post(self):
        args = _parser.parse_args()

        exists = db.session.scalar(
            db.select(ExerciseType).filter_by(name=args["name"]).limit(1)
        )
        if exists:
            return {"message": "Exercise type already exists"}, 400

        typ = ExerciseType(name=args["name"])
        db.session.add(typ)
        db.session.commit()
        return {"id": typ.id, "name": typ.name}, 201


class ExerciseTypeDetail(Resource):
    @jwt_required()
    def put(self, type_id: int):
        args = _parser.parse_args()
        typ = _get_type_or_404(type_id)
        typ.name = args["name"]
        db.session.commit()
        return {"id": typ.id, "name": typ.name}, 200

    @jwt_required()
    def delete(self, type_id: int):
        typ = _get_type_or_404(type_id)
        db.session.delete(typ)
        db.session.commit()
        return {"message": "deleted"}, 204
