from datetime import datetime
from flask import Blueprint, request, jsonify, get_flashed_messages
from flask_jwt_extended import get_jwt_identity
from extensions import db, cache
from models import User, CompanyProfile, PlacementDrive, Application
from utils.decorators import company_required

company_bp = Blueprint("company", __name__, url_prefix="/api/company")


@company_bp.route("/drives", methods=["GET"])
@company_required
def get_company_drives():
    jwt_data = get_jwt_identity()
    user_id = int(jwt_data["id"]) if isinstance(jwt_data, dict) else int(jwt_data)
    user = User.query.get(user_id)

    if not user or not user.company_profile:
        return jsonify({"error": "Company profile not found"}), 404

    drives = [d.to_dict() for d in user.company_profile.drives]
    return jsonify({
        "company_status": user.company_profile.approval_status,
        "is_blacklisted": user.company_profile.is_blacklisted,
        "drives": drives
    }), 200


@company_bp.route("/drives", methods=["POST"])
@company_required
def create_drive():
    jwt_data = get_jwt_identity()
    user_id = int(jwt_data["id"]) if isinstance(jwt_data, dict) else int(jwt_data)
    user = User.query.get(user_id)

    cp = user.company_profile
    if not cp:
        return jsonify({"error": "Company profile not found"}), 404

    if cp.approval_status != "approved":
        return jsonify({"error": "Company registration is not approved yet. Cannot create drives."}), 403

    if cp.is_blacklisted:
        return jsonify({"error": "Company is blacklisted. Creation prohibited."}), 403

    data = request.get_json() or {}
    job_title = data.get("job_title", "").strip()
    job_description = data.get("job_description", "").strip()
    eligible_branches = data.get("eligible_branches", "").strip()
    min_cgpa = float(data.get("min_cgpa", 0.0))
    eligible_year = int(data.get("eligible_year", 0)) if data.get("eligible_year") else None
    deadline_str = data.get("application_deadline", "")

    if not job_title or not deadline_str:
        return jsonify({"error": "Job title and application deadline are required"}), 400

    try:
        application_deadline = datetime.fromisoformat(deadline_str.replace("Z", "+00:00"))
    except ValueError:
        return jsonify({"error": "Invalid date format. Use ISO format YYYY-MM-DDTHH:MM:SS"}), 400

    drive = PlacementDrive(
        company_id=cp.id,
        job_title=job_title,
        job_description=job_description,
        eligible_branches=eligible_branches,
        min_cgpa=min_cgpa,
        eligible_year=eligible_year,
        application_deadline=application_deadline,
        status="pending"
    )

    db.session.add(drive)
    db.session.commit()
    cache.clear()

    return jsonify({
        "message": "Placement drive created successfully. Submitted for Admin approval.",
        "drive": drive.to_dict()
    }), 201


@company_bp.route("/drives/<int:drive_id>/applications", methods=["GET"])
@company_required
def get_drive_applications(drive_id):
    jwt_data = get_jwt_identity()
    user_id = int(jwt_data["id"]) if isinstance(jwt_data, dict) else int(jwt_data)
    user = User.query.get(user_id)

    drive = PlacementDrive.query.get_or_404(drive_id)

    if drive.company_id != user.company_profile.id:
        return jsonify({"error": "Unauthorized to view applications for this drive"}), 403

    applications = [a.to_dict() for a in drive.applications]
    return jsonify({
        "drive": drive.to_dict(),
        "applications": applications
    }), 200


@company_bp.route("/applications/<int:app_id>/status", methods=["PUT"])
@company_required
def update_application_status(app_id):
    jwt_data = get_jwt_identity()
    user_id = int(jwt_data["id"]) if isinstance(jwt_data, dict) else int(jwt_data)
    user = User.query.get(user_id)

    app_record = Application.query.get_or_404(app_id)

    if app_record.drive.company_id != user.company_profile.id:
        return jsonify({"error": "Unauthorized to modify this application"}), 403

    data = request.get_json() or {}
    new_status = data.get("status", "").strip().lower()

    if new_status not in ["applied", "shortlisted", "selected", "rejected"]:
        return jsonify({"error": "Invalid status value"}), 400

    app_record.status = new_status
    db.session.commit()

    return jsonify({
        "message": f"Application status updated to '{new_status}'",
        "application": app_record.to_dict()
    }), 200


@company_bp.route("/generate-offer-letter", methods=["POST"])
@company_required
def generate_offer_letter():
    data = request.get_json() or {}
    app_id = data.get("application_id")
    salary = data.get("salary", "₹8,00,000 LPA")
    joining_date = data.get("joining_date", "2026-07-01")
    location = data.get("location", "Bangalore / Remote")

    if not app_id:
        return jsonify({"error": "application_id is required"}), 400

    app_record = Application.query.get_or_404(app_id)

    if app_record.status != "selected":
        return jsonify({"error": "Offer letters can only be generated for 'selected' candidates"}), 400

    offer_letter_details = {
        "candidate_name": app_record.student.user.name,
        "email": app_record.student.user.email,
        "company_name": app_record.drive.company.company_name,
        "job_title": app_record.drive.job_title,
        "salary": salary,
        "joining_date": joining_date,
        "location": location,
        "issue_date": datetime.utcnow().strftime("%Y-%m-%d"),
        "reference_no": f"OFFER-{app_record.id:04d}-{datetime.utcnow().year}"
    }

    return jsonify({
        "message": "Offer letter details generated successfully",
        "offer_letter": offer_letter_details
    }), 200
