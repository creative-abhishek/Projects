from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    student_profile = db.relationship(
        "StudentProfile", backref="user", uselist=False, cascade="all, delete-orphan"
    )
    company_profile = db.relationship(
        "CompanyProfile", backref="user", uselist=False, cascade="all, delete-orphan"
    )

    def set_password(self, raw_password: str) -> None:
        self.password_hash = generate_password_hash(raw_password)

    def check_password(self, raw_password: str) -> bool:
        return check_password_hash(self.password_hash, raw_password)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "role": self.role,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat(),
        }


class StudentProfile(db.Model):
    __tablename__ = "student_profiles"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), unique=True, nullable=False)

    branch = db.Column(db.String(80), nullable=True)
    cgpa = db.Column(db.Float, nullable=True)
    graduation_year = db.Column(db.Integer, nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    resume_link = db.Column(db.String(255), nullable=True)

    applications = db.relationship(
        "Application", backref="student", cascade="all, delete-orphan"
    )

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "name": self.user.name,
            "email": self.user.email,
            "branch": self.branch,
            "cgpa": self.cgpa,
            "graduation_year": self.graduation_year,
            "phone": self.phone,
            "resume_link": self.resume_link,
            "is_active": self.user.is_active,
        }


class CompanyProfile(db.Model):
    __tablename__ = "company_profiles"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), unique=True, nullable=False)

    company_name = db.Column(db.String(150), nullable=False)
    hr_contact = db.Column(db.String(120), nullable=True)
    website = db.Column(db.String(255), nullable=True)
    approval_status = db.Column(db.String(20), default="pending", nullable=False)
    is_blacklisted = db.Column(db.Boolean, default=False, nullable=False)

    drives = db.relationship(
        "PlacementDrive", backref="company", cascade="all, delete-orphan"
    )

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "company_name": self.company_name,
            "hr_contact": self.hr_contact,
            "website": self.website,
            "approval_status": self.approval_status,
            "is_blacklisted": self.is_blacklisted,
            "is_active": self.user.is_active,
        }


class PlacementDrive(db.Model):
    __tablename__ = "placement_drives"

    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey("company_profiles.id"), nullable=False)

    job_title = db.Column(db.String(150), nullable=False)
    job_description = db.Column(db.Text, nullable=True)
    eligible_branches = db.Column(db.String(255), nullable=True)
    min_cgpa = db.Column(db.Float, default=0.0)
    eligible_year = db.Column(db.Integer, nullable=True)
    application_deadline = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default="pending", nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    applications = db.relationship(
        "Application", backref="drive", cascade="all, delete-orphan"
    )

    def to_dict(self):
        return {
            "id": self.id,
            "company_id": self.company_id,
            "company_name": self.company.company_name,
            "job_title": self.job_title,
            "job_description": self.job_description,
            "eligible_branches": self.eligible_branches,
            "min_cgpa": self.min_cgpa,
            "eligible_year": self.eligible_year,
            "application_deadline": self.application_deadline.isoformat(),
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "applicant_count": len(self.applications),
        }


class Application(db.Model):
    __tablename__ = "applications"

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("student_profiles.id"), nullable=False)
    drive_id = db.Column(db.Integer, db.ForeignKey("placement_drives.id"), nullable=False)
    application_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default="applied", nullable=False)

    __table_args__ = (
        db.UniqueConstraint("student_id", "drive_id", name="uq_student_drive"),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "student_id": self.student_id,
            "student_name": self.student.user.name,
            "student_email": self.student.user.email,
            "student_branch": self.student.branch,
            "student_cgpa": self.student.cgpa,
            "student_year": self.student.graduation_year,
            "student_phone": self.student.phone,
            "resume_link": self.student.resume_link,
            "drive_id": self.drive_id,
            "job_title": self.drive.job_title,
            "company_id": self.drive.company_id,
            "company_name": self.drive.company.company_name,
            "application_date": self.application_date.isoformat(),
            "status": self.status,
        }

