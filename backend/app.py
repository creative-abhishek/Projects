import os
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS

from config import Config
from extensions import db, cache, jwt
from init_db import init_database

from routes.auth import auth_bp
from routes.admin import admin_bp
from routes.company import company_bp
from routes.student import student_bp
from routes.jobs import jobs_bp

DIST_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend", "dist"))


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    os.makedirs(app.config["EXPORTS_FOLDER"], exist_ok=True)
    os.makedirs(app.config["REPORTS_FOLDER"], exist_ok=True)

    db.init_app(app)
    cache.init_app(app)
    jwt.init_app(app)

    CORS(app, resources={r"/*": {"origins": "*"}})

    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(company_bp)
    app.register_blueprint(student_bp)
    app.register_blueprint(jobs_bp)

    @app.route("/uploads/<path:filename>")
    def serve_upload(filename):
        return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return jsonify({"error": "Authorization token missing"}), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({"error": "Invalid authorization token"}), 401

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({"error": "Authorization token has expired"}), 401

    @app.route("/", defaults={"path": ""})
    @app.route("/<path:path>")
    def serve_spa(path):
        if path.startswith("api/") or path == "api":
            return jsonify({"error": "API endpoint not found"}), 404

        if os.path.exists(DIST_DIR):
            file_path = os.path.join(DIST_DIR, path)
            if path != "" and os.path.exists(file_path):
                return send_from_directory(DIST_DIR, path)
            index_path = os.path.join(DIST_DIR, "index.html")
            if os.path.exists(index_path):
                return send_from_directory(DIST_DIR, "index.html")

        return jsonify({
            "name": "Placement Portal Application API (PPA V2)",
            "status": "online",
            "documentation": "Use /api endpoints",
            "warning": "Frontend dist folder not found. Please build frontend with npm run build."
        })

    return app


app = create_app()

if __name__ == "__main__":
    if not os.path.exists(os.path.join(Config.BASE_DIR, "placement_portal.sqlite3")):
        print("Database not found. Programmatically initializing database...")
        init_database()

    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", 5000))
    print(f"Starting Placement Portal API & Web App server on http://{host}:{port}")
    app.run(host=host, port=port, debug=True)