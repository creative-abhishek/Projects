import os
from flask import Blueprint, jsonify, send_from_directory, current_app
from celery.result import AsyncResult
from utils.decorators import admin_required, student_required
from tasks import celery_app, daily_deadline_reminders, monthly_activity_report

jobs_bp = Blueprint("jobs", __name__, url_prefix="/api/jobs")


@jobs_bp.route("/status/<task_id>", methods=["GET"])
def get_task_status(task_id):
    try:
        res = AsyncResult(task_id, app=celery_app)
        if res.ready():
            task_res = res.result
            if isinstance(task_res, Exception):
                task_res = str(task_res)
            return jsonify({
                "task_id": task_id,
                "status": res.status,
                "result": task_res
            }), 200
        else:
            return jsonify({
                "task_id": task_id,
                "status": res.status,
                "result": None
            }), 202
    except Exception as e:
        return jsonify({
            "task_id": task_id,
            "status": "PENDING",
            "result": None
        }), 200


@jobs_bp.route("/download-csv/<filename>", methods=["GET"])
def download_csv(filename):
    return send_from_directory(current_app.config["EXPORTS_FOLDER"], filename, as_attachment=True)


@jobs_bp.route("/download-report/<filename>", methods=["GET"])
def download_report(filename):
    return send_from_directory(current_app.config["REPORTS_FOLDER"], filename)


@jobs_bp.route("/trigger-daily-reminders", methods=["POST"])
@admin_required
def trigger_daily_reminders():
    task = daily_deadline_reminders.delay()
    result = task.get() if current_app.config.get("CELERY_TASK_ALWAYS_EAGER") else None
    return jsonify({
        "message": "Daily deadline reminders job triggered",
        "task_id": task.id,
        "result": result
    }), 200


@jobs_bp.route("/trigger-monthly-report", methods=["POST"])
@admin_required
def trigger_monthly_report():
    task = monthly_activity_report.delay()
    result = task.get() if current_app.config.get("CELERY_TASK_ALWAYS_EAGER") else None
    return jsonify({
        "message": "Monthly activity report job triggered",
        "task_id": task.id,
        "result": result
    }), 200
