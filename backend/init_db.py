import os
from flask import Flask
from config import Config
from extensions import db
from models import User, StudentProfile, CompanyProfile, PlacementDrive, Application


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    os.makedirs(app.config["EXPORTS_FOLDER"], exist_ok=True)
    os.makedirs(app.config["REPORTS_FOLDER"], exist_ok=True)

    db.init_app(app)
    return app


def init_database():
    app = create_app()

    with app.app_context():
        db.create_all()
        print("Database tables created successfully.")

        existing_admin = User.query.filter_by(role="admin").first()
        if existing_admin:
            print(f"Admin already exists: {existing_admin.email}")
            return

        admin = User(
            name="Institute Placement Admin",
            email=app.config["ADMIN_EMAIL"],
            role="admin",
            is_active=True,
        )
        admin.set_password(app.config["ADMIN_PASSWORD"])

        db.session.add(admin)
        db.session.commit()

        print(f"Admin account created programmatically: {app.config['ADMIN_EMAIL']} / {app.config['ADMIN_PASSWORD']}")


if __name__ == "__main__":
    init_database()
