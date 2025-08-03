from datetime import datetime

from flask_jwt_extended import create_access_token
from werkzeug.security import check_password_hash, generate_password_hash

from .extensions import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    sessions = db.relationship('WorkoutSession', backref='user', lazy=True)
    goals    = db.relationship('Goal',            backref='user', lazy=True)

    # -------- pomocnicze metody --------
    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    def create_token(self) -> str:
        """Zwraca JWT z identity w postaci string (wymóg v4)."""
        return create_access_token(identity=str(self.id))


class ExerciseType(db.Model):
    id   = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

    sessions = db.relationship('WorkoutSession', backref='type', lazy=True)


class WorkoutSession(db.Model):
    id               = db.Column(db.Integer, primary_key=True)
    user_id          = db.Column(db.Integer,
                                 db.ForeignKey('user.id'),
                                 nullable=False)
    exercise_type_id = db.Column(db.Integer,
                                 db.ForeignKey('exercise_type.id'),
                                 nullable=False)
    duration = db.Column(db.Integer, nullable=False)  # minuty
    calories = db.Column(db.Integer, nullable=False)
    date     = db.Column(db.DateTime, default=datetime.utcnow)


class Goal(db.Model):
    id           = db.Column(db.Integer, primary_key=True)
    user_id      = db.Column(db.Integer,
                             db.ForeignKey('user.id'),
                             nullable=False)
    description  = db.Column(db.String(140), nullable=False)
    target_value = db.Column(db.Integer,      nullable=False)
    period       = db.Column(db.String(20),   nullable=False)  # daily / weekly
