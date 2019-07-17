from decouple import config


class Config:
    """Set Flask configuration vars from .env file."""

    # General
    TESTING = config('TESTING', default=False, cast=bool)
    FLASK_DEBUG = config('FLASK_DEBUG', default=False, cast=bool)
    SECRET_KEY = config('SECRET_KEY')

    # Database
    SQLALCHEMY_DATABASE_URI = config('SQLALCHEMY_DATABASE_URI', default="sqlite:///slides.db", cast=str)
    SQLALCHEMY_TRACK_MODIFICATIONS = config('SQLALCHEMY_TRACK_MODIFICATIONS', default=False, cast=bool)
