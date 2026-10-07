from datetime import datetime
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import get_jwt_identity
from extensions import db, cache
from models import User, StudentProfile, PlacementDrive, Application
from utils.decorators import student_required
from tasks import export_student_applications_csv

student_bp = Blueprint("student", __name__, url_prefix="/api/student")


def evaluate_eligibility(student, drive):
    reasons = []
    is_eligible = True

    if not student.branch or student.cgpa is None or not student.graduation_year:
        return False, ["Please complete your student profile (Branch, CGPA, Graduation Year) before applying."]

    if drive.min_cgpa and student.cgpa < drive.min_cgpa:
        is_eligible = False
        reasons.append(f"Requires minimum CGPA of {drive.min_cgpa} (Your CGPA: {student.cgpa})")

    if drive.eligible_branches:
        allowed_branches = [b.strip().lower() for b in drive.eligible_branches.split(",")]
        if student.branch.strip().lower() not in allowed_branches:
            is_eligible = False
            reasons.append(f"Eligible branches: {drive.eligible_branches} (Your branch: {student.branch})")

    if drive.eligible_year and student.graduation_year != drive.eligible_year:
        is_eligible = False
        reasons.append(f"Eligible year: {drive.eligible_year} (Your graduation year: {student.graduation_year})")

    if drive.application_deadline < datetime.utcnow():
        is_eligible = False
        reasons.append("Application deadline has passed")

    return is_eligible, reasons


@student_bp.route("/drives", methods=["GET"])
@student_required
def get_approved_drives():
    jwt_data = get_jwt_identity()
    user_id = int(jwt_data["id"]) if isinstance(jwt_data, dict) else int(jwt_data)
    user = User.query.get(user_id)
    student = user.student_profile

    search = request.args.get("search", "").strip()

    query = PlacementDrive.query.filter_by(status="approved")

    if search:
        query = query.filter(
            (PlacementDrive.job_title.ilike(f"%{search}%")) |
            (PlacementDrive.job_description.ilike(f"%{search}%"))
        )

    all_drives = query.order_by(PlacementDrive.created_at.desc()).all()

    applied_drive_ids = set()
    if student:
        applied_drive_ids = {a.drive_id for a in student.applications}

    results = []
    for d in all_drives:
        d_dict = d.to_dict()
        is_eligible, reasons = evaluate_eligibility(student, d)
        d_dict["is_eligible"] = is_eligible
        d_dict["eligibility_reasons"] = reasons
        d_dict["has_applied"] = d.id in applied_drive_ids
        results.append(d_dict)

    return jsonify({"drives": results}), 200


@student_bp.route("/drives/<int:drive_id>/apply", methods=["POST"])
@student_required
def apply_for_drive(drive_id):
    jwt_data = get_jwt_identity()
    user_id = int(jwt_data["id"]) if isinstance(jwt_data, dict) else int(jwt_data)
    user = User.query.get(user_id)
    student = user.student_profile

    if not student:
        return jsonify({"error": "Student profile missing"}), 404

    drive = PlacementDrive.query.get_or_404(drive_id)

    if drive.status != "approved":
        return jsonify({"error": "Applications can only be submitted to approved placement drives"}), 400

    existing_app = Application.query.filter_by(student_id=student.id, drive_id=drive.id).first()
    if existing_app:
        return jsonify({"error": "You have already applied to this placement drive"}), 409

    is_eligible, reasons = evaluate_eligibility(student, drive)
    if not is_eligible:
        return jsonify({
            "error": "You do not meet the eligibility requirements for this drive",
            "reasons": reasons
        }), 403

    app_record = Application(
        student_id=student.id,
        drive_id=drive.id,
        status="applied"
    )

    db.session.add(app_record)
    db.session.commit()
    cache.clear()

    return jsonify({
        "message": f"Successfully applied for '{drive.job_title}' at {drive.company.company_name}",
        "application": app_record.to_dict()
    }), 201


@student_bp.route("/applications", methods=["GET"])
@student_required
def get_student_applications():
    jwt_data = get_jwt_identity()
    user_id = int(jwt_data["id"]) if isinstance(jwt_data, dict) else int(jwt_data)
    user = User.query.get(user_id)
    student = user.student_profile

    if not student:
        return jsonify({"error": "Student profile not found"}), 404

    applications = [a.to_dict() for a in student.applications]
    return jsonify({
        "student": student.to_dict(),
        "applications": applications
    }), 200


@student_bp.route("/export-csv", methods=["POST"])
@student_required
def export_csv():
    jwt_data = get_jwt_identity()
    user_id = int(jwt_data["id"]) if isinstance(jwt_data, dict) else int(jwt_data)
    user = User.query.get(user_id)
    student = user.student_profile

    if not student:
        return jsonify({"error": "Student profile not found"}), 404

    task = export_student_applications_csv.delay(student.id)
    result = task.get() if current_app.config.get("CELERY_TASK_ALWAYS_EAGER") else None

    return jsonify({
        "message": "CSV export background job triggered successfully",
        "task_id": task.id,
        "status_url": f"/api/jobs/status/{task.id}",
        "result": result
    }), 202


@student_bp.route("/ats-check", methods=["POST"])
@student_required
def ats_check():
    return jsonify({
        "ats_score": 85,
        "matched_keywords": ["python", "sql", "communication"],
        "missing_keywords": ["docker"],
        "message": "ATS Feature Preview: Static dummy evaluation complete."
    }), 200
