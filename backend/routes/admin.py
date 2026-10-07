from flask import Blueprint, request, jsonify
from extensions import db, cache
from models import User, StudentProfile, CompanyProfile, PlacementDrive, Application
from utils.decorators import admin_required

admin_bp = Blueprint("admin", __name__, url_prefix="/api/admin")


@admin_bp.route("/stats", methods=["GET"])
@admin_required
def get_admin_stats():
    total_students = User.query.filter_by(role="student").count()
    total_companies = CompanyProfile.query.count()
    pending_companies = CompanyProfile.query.filter_by(approval_status="pending").count()
    approved_companies = CompanyProfile.query.filter_by(approval_status="approved").count()

    total_drives = PlacementDrive.query.count()
    pending_drives = PlacementDrive.query.filter_by(status="pending").count()
    approved_drives = PlacementDrive.query.filter_by(status="approved").count()

    total_applications = Application.query.count()
    selected_applications = Application.query.filter_by(status="selected").count()
    shortlisted_applications = Application.query.filter_by(status="shortlisted").count()
    rejected_applications = Application.query.filter_by(status="rejected").count()
    applied_applications = Application.query.filter_by(status="applied").count()

    drive_stats = {
        "Pending": pending_drives,
        "Approved": approved_drives,
        "Rejected": PlacementDrive.query.filter_by(status="rejected").count(),
        "Closed": PlacementDrive.query.filter_by(status="closed").count(),
    }

    app_stats = {
        "Applied": applied_applications,
        "Shortlisted": shortlisted_applications,
        "Selected": selected_applications,
        "Rejected": rejected_applications,
    }

    top_companies_query = db.session.query(
        CompanyProfile.company_name, db.func.count(PlacementDrive.id)
    ).join(PlacementDrive, PlacementDrive.company_id == CompanyProfile.id)\
     .group_by(CompanyProfile.id)\
     .order_by(db.func.count(PlacementDrive.id).desc()).limit(5).all()

    top_companies = [{"name": row[0], "drives": row[1]} for row in top_companies_query]

    return jsonify({
        "summary": {
            "total_students": total_students,
            "total_companies": total_companies,
            "pending_companies": pending_companies,
            "approved_companies": approved_companies,
            "total_drives": total_drives,
            "pending_drives": pending_drives,
            "approved_drives": approved_drives,
            "total_applications": total_applications,
            "selected_applications": selected_applications,
        },
        "charts": {
            "drives_distribution": drive_stats,
            "applications_distribution": app_stats,
            "top_companies": top_companies
        }
    }), 200


@admin_bp.route("/companies", methods=["GET"])
@admin_required
def get_companies():
    status_filter = request.args.get("status", "").strip()
    search = request.args.get("search", "").strip()

    query = CompanyProfile.query.join(User, User.id == CompanyProfile.user_id)

    if status_filter:
        query = query.filter(CompanyProfile.approval_status == status_filter)

    if search:
        query = query.filter(
            (CompanyProfile.company_name.ilike(f"%{search}%")) |
            (User.email.ilike(f"%{search}%"))
        )

    companies = [c.to_dict() for c in query.all()]
    return jsonify({"companies": companies}), 200


@admin_bp.route("/companies/<int:company_id>/approve", methods=["POST"])
@admin_required
def approve_company(company_id):
    company = CompanyProfile.query.get_or_404(company_id)
    company.approval_status = "approved"
    db.session.commit()
    cache.clear()
    return jsonify({"message": f"Company '{company.company_name}' approved successfully"}), 200


@admin_bp.route("/companies/<int:company_id>/reject", methods=["POST"])
@admin_required
def reject_company(company_id):
    company = CompanyProfile.query.get_or_404(company_id)
    company.approval_status = "rejected"
    db.session.commit()
    cache.clear()
    return jsonify({"message": f"Company '{company.company_name}' registration rejected"}), 200


@admin_bp.route("/companies/<int:company_id>/toggle-blacklist", methods=["POST"])
@admin_required
def toggle_blacklist_company(company_id):
    company = CompanyProfile.query.get_or_404(company_id)
    company.is_blacklisted = not company.is_blacklisted
    db.session.commit()
    cache.clear()
    status_str = "blacklisted" if company.is_blacklisted else "whitelisted"
    return jsonify({"message": f"Company '{company.company_name}' is now {status_str}"}), 200


@admin_bp.route("/drives", methods=["GET"])
@admin_required
def get_all_drives():
    status_filter = request.args.get("status", "").strip()
    search = request.args.get("search", "").strip()

    query = PlacementDrive.query.join(CompanyProfile, PlacementDrive.company_id == CompanyProfile.id)

    if status_filter:
        query = query.filter(PlacementDrive.status == status_filter)

    if search:
        query = query.filter(
            (PlacementDrive.job_title.ilike(f"%{search}%")) |
            (CompanyProfile.company_name.ilike(f"%{search}%"))
        )

    drives = [d.to_dict() for d in query.all()]
    return jsonify({"drives": drives}), 200


@admin_bp.route("/drives/<int:drive_id>/approve", methods=["POST"])
@admin_required
def approve_drive(drive_id):
    drive = PlacementDrive.query.get_or_404(drive_id)
    drive.status = "approved"
    db.session.commit()
    cache.clear()
    return jsonify({"message": f"Placement drive '{drive.job_title}' approved"}), 200


@admin_bp.route("/drives/<int:drive_id>/reject", methods=["POST"])
@admin_required
def reject_drive(drive_id):
    drive = PlacementDrive.query.get_or_404(drive_id)
    drive.status = "rejected"
    db.session.commit()
    cache.clear()
    return jsonify({"message": f"Placement drive '{drive.job_title}' rejected"}), 200


@admin_bp.route("/drives/<int:drive_id>/close", methods=["POST"])
@admin_required
def close_drive(drive_id):
    drive = PlacementDrive.query.get_or_404(drive_id)
    drive.status = "closed"
    db.session.commit()
    cache.clear()
    return jsonify({"message": f"Placement drive '{drive.job_title}' closed"}), 200


@admin_bp.route("/students", methods=["GET"])
@admin_required
def get_all_students():
    search = request.args.get("search", "").strip()

    query = StudentProfile.query.join(User, User.id == StudentProfile.user_id)

    if search:
        query = query.filter(
            (User.name.ilike(f"%{search}%")) |
            (User.email.ilike(f"%{search}%")) |
            (StudentProfile.branch.ilike(f"%{search}%"))
        )

    students = [s.to_dict() for s in query.all()]
    return jsonify({"students": students}), 200


@admin_bp.route("/users/<int:user_id>/toggle-active", methods=["POST"])
@admin_required
def toggle_user_active(user_id):
    user = User.query.get_or_404(user_id)
    if user.role == "admin":
        return jsonify({"error": "Cannot deactivate the superuser Admin"}), 400

    user.is_active = not user.is_active
    db.session.commit()
    cache.clear()
    state_str = "activated" if user.is_active else "deactivated"
    return jsonify({"message": f"User '{user.name}' has been {state_str}"}), 200


@admin_bp.route("/applications", methods=["GET"])
@admin_required
def get_all_applications():
    applications = [a.to_dict() for a in Application.query.order_by(Application.application_date.desc()).all()]
    return jsonify({"applications": applications}), 200
