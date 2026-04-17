import os

class Config:
    SECRET_KEY = "1234"
    JWT_EXPIRY = 30 * 24 * 3600

    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///dass.db")
    SQL_TRACK_MODIFICATIONS = False
    RESET_TOKEN_METHOD = "predictable"

    MAX_LOGIN_ATTEMPTS = None
    LOCKOUT_DURATION = None