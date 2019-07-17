import logging

import sentry_sdk
from decouple import config
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sentry_sdk.integrations.flask import FlaskIntegration

db = SQLAlchemy()
SENTRY_DNS = config("SENTRY_DNS", default=None, cast=str)


def create_app():
    """Construct the core application."""
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object('config.Config')
    db.init_app(app)

    if SENTRY_DNS and not app.debug:
        # In production mode, track all errors with sentry.
        sentry_sdk.init(
            dsn=SENTRY_DNS,
            integrations=[FlaskIntegration()]
        )

    # Add log handler to sys.stderr.
    app.logger.addHandler(logging.StreamHandler())
    app.logger.setLevel(logging.INFO)

    with app.app_context():
        # Add routes to app context.
        from application import routes

        # Create tables for our models
        db.create_all()

        return app
