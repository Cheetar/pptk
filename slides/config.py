from secrets import token_hex

from decouple import config

DEFAULT_SECRET_KEY_LENGTH = 40


class Config:
    """Set Flask configuration vars from .env file."""

    # General
    TESTING = config('TESTING', default=False, cast=bool)
    DEBUG = config('FLASK_DEBUG', default=False, cast=bool)
    SECRET_KEY = config('SECRET_KEY', default=token_hex(DEFAULT_SECRET_KEY_LENGTH), cast=str)

    # Database
    SQLALCHEMY_DATABASE_URI = config('SQLALCHEMY_DATABASE_URI', default="sqlite:///slides.db", cast=str)
    SQLALCHEMY_TRACK_MODIFICATIONS = config('SQLALCHEMY_TRACK_MODIFICATIONS', default=False, cast=bool)
