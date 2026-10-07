import os
import csv
from datetime import datetime, timedelta
from celery import Celery
from flask import render_template_string
from config import Config
from extensions import db
from models import User, StudentProfile, CompanyProfile, PlacementDrive, Application

celery_app = Celery("tasks", broker=Config.CELERY_BROKER_URL, backend=Config.CELERY_RESULT_BACKEND)
celery_app.conf.update(
    task_always_eager=Config.CELERY_TASK_ALWAYS_EAGER,
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Kolkata",
    enable_utc=True,
)


def get_flask_app():
    from app import app
    return app


@celery_app.task(name="tasks.daily_deadline_reminders")
def daily_deadline_reminders():
    app = get_flask_app()
    reminders_sent = 0

    with app.app_context():
        now = datetime.utcnow()
        three_days = now + timedelta(days=3)

        upcoming_drives = PlacementDrive.query.filter(
            PlacementDrive.status == "approved",
            PlacementDrive.application_deadline >= now,
            PlacementDrive.application_deadline <= three_days
        ).all()

        if not upcoming_drives:
            return {"status": "success", "message": "No upcoming deadlines in the next 3 days", "sent_count": 0}

        students = StudentProfile.query.all()
        for drive in upcoming_drives:
            for student in students:
                print(f"[DAILY REMINDER] To Student: {student.user.email} | Drive '{drive.job_title}' at {drive.company.company_name} expires on {drive.application_deadline.isoformat()}")
                reminders_sent += 1

    return {"status": "success", "drives_count": len(upcoming_drives), "reminders_sent": reminders_sent}


@celery_app.task(name="tasks.monthly_activity_report")
def monthly_activity_report():
    app = get_flask_app()

    with app.app_context():
        total_drives = PlacementDrive.query.count()
        approved_drives = PlacementDrive.query.filter_by(status="approved").count()
        total_students = StudentProfile.query.count()
        total_applications = Application.query.count()
        selected_students = Application.query.filter_by(status="selected").count()

        drives_list = PlacementDrive.query.order_by(PlacementDrive.created_at.desc()).all()

        report_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Monthly Placement Activity Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 30px; color: #333; }}
                h1 {{ color: #0d6efd; border-bottom: 2px solid #0d6efd; padding-bottom: 10px; }}
                .stats-grid {{ display: flex; gap: 20px; margin: 20px 0; }}
                .card {{ background: #f8f9fa; border: 1px solid #ddd; padding: 15px; border-radius: 8px; flex: 1; text-align: center; }}
                .card-val {{ font-size: 24px; font-weight: bold; color: #0d6efd; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
                th, td {{ border: 1px solid #ddd; padding: 10px; text-align: left; }}
                th {{ background: #0d6efd; color: white; }}
                tr:nth-child(even) {{ background: #f2f2f2; }}
            </style>
        </head>
        <body>
            <h1>Institute Placement Activity Monthly Report</h1>
            <p><strong>Report Date:</strong> {datetime.utcnow().strftime('%B %d, %Y')}</p>
            <p><strong>Generated For:</strong> Institute Placement Cell Admin</p>

            <div class="stats-grid">
                <div class="card"><div class="card-val">{total_drives}</div><div>Total Drives</div></div>
                <div class="card"><div class="card-val">{total_students}</div><div>Registered Students</div></div>
                <div class="card"><div class="card-val">{total_applications}</div><div>Total Applications</div></div>
                <div class="card"><div class="card-val">{selected_students}</div><div>Students Placed</div></div>
            </div>

            <h2>Placement Drives Overview</h2>
            <table>
                <thead>
                    <tr>
                        <th>Drive ID</th>
                        <th>Company Name</th>
                        <th>Job Title</th>
                        <th>Status</th>
                        <th>Applicants</th>
                        <th>Deadline</th>
                    </tr>
                </thead>
                <tbody>
        """

        for d in drives_list:
            report_html += f"""
                    <tr>
                        <td>#{d.id}</td>
                        <td>{d.company.company_name}</td>
                        <td>{d.job_title}</td>
                        <td>{d.status.upper()}</td>
                        <td>{len(d.applications)}</td>
                        <td>{d.application_deadline.strftime('%Y-%m-%d')}</td>
                    </tr>
            """

        report_html += """
                </tbody>
            </table>
        </body>
        </html>
        """

        filename = f"monthly_report_{datetime.utcnow().strftime('%Y_%m_%d')}.html"
        filepath = os.path.join(Config.REPORTS_FOLDER, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(report_html)

        print(f"[MONTHLY REPORT] Report generated successfully at {filepath}")

        return {
            "status": "success",
            "report_file": filename,
            "report_url": f"/api/jobs/download-report/{filename}",
            "stats": {
                "total_drives": total_drives,
                "approved_drives": approved_drives,
                "total_applications": total_applications,
                "selected_students": selected_students
            }
        }


@celery_app.task(name="tasks.export_student_applications_csv")
def export_student_applications_csv(student_profile_id):
    app = get_flask_app()

    with app.app_context():
        student = StudentProfile.query.get(student_profile_id)
        if not student:
            return {"status": "error", "message": "Student profile not found"}

        filename = f"applications_student_{student.id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"
        filepath = os.path.join(Config.EXPORTS_FOLDER, filename)

        with open(filepath, mode="w", newline="", encoding="utf-8") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow([
                "Application ID", "Student ID", "Student Name", "Student Email",
                "Company Name", "Job Title", "Application Date", "Status"
            ])

            for app_rec in student.applications:
                writer.writerow([
                    app_rec.id,
                    student.id,
                    student.user.name,
                    student.user.email,
                    app_rec.drive.company.company_name,
                    app_rec.drive.job_title,
                    app_rec.application_date.strftime("%Y-%m-%d %H:%M:%S"),
                    app_rec.status
                ])

        print(f"[CSV EXPORT] Export completed for student {student.id}: {filepath}")

        return {
            "status": "completed",
            "filename": filename,
            "download_url": f"/api/jobs/download-csv/{filename}",
            "total_records": len(student.applications)
        }
