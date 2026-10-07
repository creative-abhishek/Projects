import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    BASE_DIR = BASE_DIR
    SECRET_KEY = os.environ.get("SECRET_KEY", "change-this-in-production-ppa-secret")

    UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
    EXPORTS_FOLDER = os.path.join(BASE_DIR, "exports")
    REPORTS_FOLDER = os.path.join(BASE_DIR, "reports")
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024

    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(BASE_DIR, 'placement_portal.sqlite3')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "change-this-jwt-secret-ppa-v2-secure-key-32bytes!")
    JWT_ACCESS_TOKEN_EXPIRES = 60 * 60 * 8

    CACHE_TYPE = os.environ.get("CACHE_TYPE", "SimpleCache")
    CACHE_REDIS_HOST = os.environ.get("CACHE_REDIS_HOST", "localhost")
    CACHE_REDIS_PORT = int(os.environ.get("CACHE_REDIS_PORT", 6379))
    CACHE_REDIS_DB = 0
    CACHE_DEFAULT_TIMEOUT = 300

    CELERY_BROKER_URL = os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379/1")
    CELERY_RESULT_BACKEND = os.environ.get("CELERY_RESULT_BACKEND", "redis://localhost:6379/2")
    CELERY_TASK_ALWAYS_EAGER = os.environ.get("CELERY_TASK_ALWAYS_EAGER", "True").lower() == "true"

    MAIL_SERVER = "smtp.gmail.com"
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = "admin@ppa.com"
    MAIL_PASSWORD = "your_app_password"
    MAIL_DEFAULT_SENDER = "admin@ppa.com"

    ADMIN_EMAIL = "admin@ppa.com"
    ADMIN_PASSWORD = "admin123"

