from flask_cors import CORS
from flask_restful import Api

from . import config
from .extensions import db, jwt, migrate

from .models import ExerciseType, Goal, User, WorkoutSession  # noqa: F401

from .resources.auth import Login, Register
from .resources.exercise import ExerciseTypeDetail, ExerciseTypeList
from .resources.goal import GoalDetail, GoalList
from .resources.session import SessionDetail, SessionList

from flask import Flask


def create_app():
    app = Flask(__name__)
    app.config.from_object(config)

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    api = Api(app, prefix="/api")
    CORS(app)

    api.add_resource(GoalList, '/goals')
    api.add_resource(GoalDetail, '/goals/<int:goal_id>')
    api.add_resource(SessionList, '/sessions')
    api.add_resource(SessionDetail, '/sessions/<int:session_id>')
    api.add_resource(Register,           '/auth/register')
    api.add_resource(Login,              '/auth/login')
    api.add_resource(ExerciseTypeList,   '/exercise-types')
    api.add_resource(ExerciseTypeDetail, '/exercise-types/<int:type_id>')

    @app.route('/', methods=['GET'])
    def hello():
        return {'message': 'Fitness Tracker API działa!'}

    print('\n=== URL MAP ===')
    for rule in app.url_map.iter_rules():
        methods = ','.join(sorted(rule.methods))
        print(f'{rule.rule:35} -> {methods}')
    print('==============\n')

    return app


app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
