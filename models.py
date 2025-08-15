import secrets
from datetime import datetime

from flask_jwt_extended import create_access_token
from werkzeug.security import check_password_hash, generate_password_hash

from .extensions import db


class User(db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)

    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    provider = db.Column(db.String(20), nullable=True, index=True)
    provider_sub = db.Column(db.String(255), unique=True, nullable=True)
    name = db.Column(db.String(120), nullable=True)
    avatar_url = db.Column(db.String(255), nullable=True)

    sessions = db.relationship("WorkoutSession", backref="user", lazy=True)
    goals = db.relationship("Goal", backref="user", lazy=True)
    types = db.relationship("ExerciseType", backref="user", lazy=True)

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def set_unusable_password(self) -> None:
        random_pwd = "!" + secrets.token_urlsafe(32)
        self.password_hash = generate_password_hash(random_pwd)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    def create_token(self) -> str:
        return create_access_token(identity=str(self.id))


class ExerciseType(db.Model):
    __tablename__ = "exercise_type"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    name = db.Column(db.String(50), nullable=False)

    __table_args__ = (
        db.UniqueConstraint("user_id", "name", name="uq_exercise_type_user_name"),
        db.Index("ix_exercise_type_user_id", "user_id"),
    )

    sessions = db.relationship("WorkoutSession", backref="type", lazy=True)
    goals = db.relationship("Goal", backref="exercise_type", lazy=True)


class WorkoutSession(db.Model):
    __tablename__ = "workout_session"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    exercise_type_id = db.Column(db.Integer, db.ForeignKey("exercise_type.id"), nullable=False)
    duration = db.Column(db.Integer, nullable=False)
    calories = db.Column(db.Integer, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)


class Goal(db.Model):
    __tablename__ = "goal"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    description = db.Column(db.String(140), nullable=False)
    target_value = db.Column(db.Integer, nullable=False)
    period = db.Column(db.String(20), nullable=False)

    metric = db.Column(db.String(20), nullable=False, default="duration")
    start_date = db.Column(db.DateTime, nullable=True)
    end_date = db.Column(db.DateTime, nullable=True)
    exercise_type_id = db.Column(db.Integer, db.ForeignKey("exercise_type.id"), nullable=True)
