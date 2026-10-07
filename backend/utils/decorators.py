from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from models import User, CompanyProfile, StudentProfile


def role_required(allowed_roles):
    if isinstance(allowed_roles, str):
        allowed_roles = [allowed_roles]

    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            jwt_data = get_jwt_identity()

            user_id = int(jwt_data["id"]) if isinstance(jwt_data, dict) else int(jwt_data)
            user = User.query.get(user_id)

            if not user or not user.is_active:
                return jsonify({"error": "User account is deactivated or not found"}), 403

            if user.role not in allowed_roles:
                return jsonify({"error": f"Access restricted to {', '.join(allowed_roles)} users"}), 403

            if user.role == "company":
                cp = user.company_profile
                if not cp:
                    return jsonify({"error": "Company profile not found"}), 403
                if cp.is_blacklisted:
                    return jsonify({"error": "Your company has been blacklisted"}), 403

            return fn(*args, **kwargs)

        return wrapper

    return decorator


def admin_required(fn):
    return role_required("admin")(fn)


def company_required(fn):
    return role_required("company")(fn)


def student_required(fn):
    return role_required("student")(fn)
