import os
import secrets

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", secrets.token_hex(32))
    JWT_EXPIRY = 30 * 60

    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///dass2.db")
    SQL_TRACK_MODIFICATIONS = False

    RESET_TOKEN_METHOD = "secure_random"
    RESET_TOKEN_EXPIRY_SECONDS = 15 * 60 

    MAX_LOGIN_ATTEMPTS = 5
    LOCKOUT_DURATION_SECONDS = 15 * 60 

    PASSWORD_MIN_LENGTH = 8
    PASSWORD_REQUIRE_UPPERCASE = True
    PASSWORD_REQUIRE_LOWERCASE = True
    PASSWORD_REQUIRE_DIGIT = True
    PASSWORD_REQUIRE_SPECIAL = True

    JWT_BLACKLIST = set()
