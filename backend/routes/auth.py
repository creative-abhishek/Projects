import os
import werkzeug.utils
from flask import Blueprint, request, jsonify, current_app, send_from_directory
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from extensions import db, cache
from models import User, StudentProfile, CompanyProfile

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")

ALLOWED_EXTENSIONS = {"pdf", "doc", "docx"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@auth_bp.route("/register/student", methods=["POST"])
def register_student():
    data = request.get_json() or {}
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")
    name = data.get("name", "").strip()

    if not email or not password or not name:
        return jsonify({"error": "Name, email, and password are required"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email is already registered"}), 409

    user = User(name=name, email=email, role="student", is_active=True)
    user.set_password(password)

    student_profile = StudentProfile(
        user=user,
        branch=data.get("branch", "").strip(),
        cgpa=float(data.get("cgpa", 0.0)) if data.get("cgpa") else None,
        graduation_year=int(data.get("graduation_year", 0)) if data.get("graduation_year") else None,
        phone=data.get("phone", "").strip(),
    )

    db.session.add(user)
    db.session.add(student_profile)
    db.session.commit()
    cache.clear()

    token = create_access_token(identity=str(user.id))

    return jsonify({
        "message": "Student registration successful",
        "access_token": token,
        "user": user.to_dict(),
        "profile": student_profile.to_dict()
    }), 201


@auth_bp.route("/register/company", methods=["POST"])
def register_company():
    data = request.get_json() or {}
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")
    company_name = data.get("company_name", "").strip()

    if not email or not password or not company_name:
        return jsonify({"error": "Company name, email, and password are required"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email is already registered"}), 409

    user = User(name=company_name, email=email, role="company", is_active=True)
    user.set_password(password)

    company_profile = CompanyProfile(
        user=user,
        company_name=company_name,
        hr_contact=data.get("hr_contact", "").strip(),
        website=data.get("website", "").strip(),
        approval_status="pending"
    )

    db.session.add(user)
    db.session.add(company_profile)
    db.session.commit()
    cache.clear()

    token = create_access_token(identity=str(user.id))

    return jsonify({
        "message": "Company registered successfully. Registration pending Admin approval.",
        "access_token": token,
        "user": user.to_dict(),
        "profile": company_profile.to_dict()
    }), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    user = User.query.filter_by(email=email).first()

    if not user or not user.check_password(password):
        return jsonify({"error": "Invalid email or password"}), 401

    if not user.is_active:
        return jsonify({"error": "Your account has been deactivated by the Institute Admin"}), 403

    token = create_access_token(identity=str(user.id))

    profile_dict = None
    if user.role == "student" and user.student_profile:
        profile_dict = user.student_profile.to_dict()
    elif user.role == "company" and user.company_profile:
        profile_dict = user.company_profile.to_dict()

    return jsonify({
        "message": "Login successful",
        "access_token": token,
        "user": user.to_dict(),
        "profile": profile_dict
    }), 200


@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def get_me():
    jwt_data = get_jwt_identity()
    user_id = int(jwt_data["id"]) if isinstance(jwt_data, dict) else int(jwt_data)

    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 44

    profile_dict = None
    if user.role == "student" and user.student_profile:
        profile_dict = user.student_profile.to_dict()
    elif user.role == "company" and user.company_profile:
        profile_dict = user.company_profile.to_dict()

    return jsonify({
        "user": user.to_dict(),
        "profile": profile_dict
    }), 200


@auth_bp.route("/profile", methods=["PUT"])
@jwt_required()
def update_profile():
    jwt_data = get_jwt_identity()
    user_id = int(jwt_data["id"]) if isinstance(jwt_data, dict) else int(jwt_data)
    user = User.query.get(user_id)

    if not user:
        return jsonify({"error": "User not found"}), 404

    data = request.get_json() or {}

    if "name" in data and data["name"].strip():
        user.name = data["name"].strip()

    if user.role == "student" and user.student_profile:
        sp = user.student_profile
        if "branch" in data:
            sp.branch = data["branch"].strip()
        if "cgpa" in data and data["cgpa"] is not None:
            sp.cgpa = float(data["cgpa"])
        if "graduation_year" in data and data["graduation_year"] is not None:
            sp.graduation_year = int(data["graduation_year"])
        if "phone" in data:
            sp.phone = data["phone"].strip()

    elif user.role == "company" and user.company_profile:
        cp = user.company_profile
        if "company_name" in data and data["company_name"].strip():
            cp.company_name = data["company_name"].strip()
            user.name = cp.company_name
        if "hr_contact" in data:
            cp.hr_contact = data["hr_contact"].strip()
        if "website" in data:
            cp.website = data["website"].strip()

    db.session.commit()
    cache.clear()

    profile_dict = user.student_profile.to_dict() if user.role == "student" else (
        user.company_profile.to_dict() if user.role == "company" else None
    )

    return jsonify({
        "message": "Profile updated successfully",
        "user": user.to_dict(),
        "profile": profile_dict
    }), 200


@auth_bp.route("/upload-resume", methods=["POST"])
@jwt_required()
def upload_resume():
    jwt_data = get_jwt_identity()
    user_id = int(jwt_data["id"]) if isinstance(jwt_data, dict) else int(jwt_data)
    user = User.query.get(user_id)

    if not user or user.role != "student" or not user.student_profile:
        return jsonify({"error": "Only student accounts can upload resumes"}), 403

    if "resume" not in request.files:
        return jsonify({"error": "No resume file attached"}), 400

    file = request.files["resume"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    if file and allowed_file(file.filename):
        ext = file.filename.rsplit(".", 1)[1].lower()
        filename = werkzeug.utils.secure_filename(f"resume_student_{user.student_profile.id}.{ext}")
        filepath = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
        file.save(filepath)

        # Update profile link
        user.student_profile.resume_link = f"/uploads/{filename}"
        db.session.commit()

        return jsonify({
            "message": "Resume uploaded successfully",
            "resume_link": user.student_profile.resume_link
        }), 200

    return jsonify({"error": "Allowed file formats: PDF, DOC, DOCX"}), 400


@auth_bp.route("/uploads/<path:filename>", methods=["GET"])
def get_uploaded_file(filename):
    return send_from_directory(current_app.config["UPLOAD_FOLDER"], filename)
