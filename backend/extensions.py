# Extensions are created here (not in app.py) so that models.py and tasks.py
# can import `db` without triggering a circular import with app.py.

from flask_sqlalchemy import SQLAlchemy
from flask_caching import Cache
from flask_jwt_extended import JWTManager

db = SQLAlchemy()
cache = Cache()
jwt = JWTManager()
