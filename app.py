from __future__ import annotations

from flask import Flask
from flask_cors import CORS
from flask_restful import Api

from . import config
from .extensions import db, jwt, migrate


def create_app() -> Flask:
    from .utils.logging import setup_logging

    setup_logging()

    app = Flask(__name__)
    app.config.from_object(config)

    app.json.ensure_ascii = False

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    CORS(
        app,
        resources={r"/api/*": {"origins": "*"}},
        supports_credentials=False,
        expose_headers=["Authorization", "Content-Type"],
    )

    api = Api(app, prefix="/api")

    from .models import ExerciseType, Goal, User, WorkoutSession  # noqa: F401
    from .utils.errors import register_error_handlers

    register_error_handlers(app)

    from .resources.auth import Login, Register
    from .resources.exercise import ExerciseTypeDetail, ExerciseTypeList
    from .resources.goal import GoalDetail, GoalList
    from .resources.health import bp as health_bp
    from .resources.report import SummaryReport
    from .resources.session import SessionDetail, SessionList

    api.add_resource(GoalList, "/goals")
    api.add_resource(GoalDetail, "/goals/<int:goal_id>")

    api.add_resource(SessionList, "/sessions")
    api.add_resource(SessionDetail, "/sessions/<int:session_id>")

    api.add_resource(Register, "/auth/register")
    api.add_resource(Login, "/auth/login")

    api.add_resource(ExerciseTypeList, "/exercise-types")
    api.add_resource(ExerciseTypeDetail, "/exercise-types/<int:type_id>")

    api.add_resource(SummaryReport, "/reports/summary")

    app.register_blueprint(health_bp)

    try:
        from .resources.stats import StatsOverview  # type: ignore
    except Exception:
        StatsOverview = None
    if StatsOverview is not None:
        api.add_resource(StatsOverview, "/stats/overview")

    @app.route("/", methods=["GET"])
    def hello():
        return {"message": "Fitness Tracker API działa!"}

    if app.config.get("DEBUG") or app.config.get("ENV") == "development":
        print("\n=== URL MAP ===")
        for rule in app.url_map.iter_rules():
            methods = ",".join(sorted(rule.methods))
            print(f"{rule.rule:35} -> {methods}")
        print("==============\n")

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
