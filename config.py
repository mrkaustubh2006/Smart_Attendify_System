"""
config.py — Application configuration classes.
"""

import os
from urllib.parse import quote_plus
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "jwt-secret-key")

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    WTF_CSRF_ENABLED = True

    QR_CODES_DIR = os.path.join(
        os.path.dirname(__file__),
        os.getenv("QR_CODES_DIR", "qr_codes"),
    )

    EXPORTS_DIR = os.path.join(
        os.path.dirname(__file__),
        os.getenv("EXPORTS_DIR", "exports"),
    )

    RATELIMIT_STORAGE_URL = os.getenv("RATELIMIT_STORAGE_URL", "memory://")
    RATELIMIT_DEFAULT = "200 per day;50 per hour"

    @staticmethod
    def _db_uri():
        host = os.getenv("MYSQLHOST", "localhost")
        port = os.getenv("MYSQLPORT", "3306")
        user = os.getenv("MYSQLUSER", "root")
        password = quote_plus(os.getenv("MYSQLPASSWORD", ""))
        database = os.getenv("MYSQLDATABASE", "smart_attendance")

        uri = (
            f"mysql+pymysql://{user}:{password}"
            f"@{host}:{port}/{database}?charset=utf8mb4"
        )

        print("DB_HOST =", host)
        print("DB_PORT =", port)
        print("DB_USER =", user)
        print("DB_NAME =", database)
        print("Database URI =", uri)

        return uri


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = Config._db_uri()
    SESSION_COOKIE_SECURE = False


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False


class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = Config._db_uri()
    SESSION_COOKIE_SECURE = True


config_map = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}
