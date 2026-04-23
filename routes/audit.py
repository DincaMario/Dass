from flask import Blueprint, request, jsonify, render_template
from models import AuditLog
from routes.auth import login_required, manager_required

audit_bp = Blueprint("audit", __name__)


@audit_bp.route("/audit")
@manager_required
def audit_page():
    return render_template("audit.html", user=request.current_user)


@audit_bp.route("/api/audit-logs", methods=["GET"])
@manager_required
def list_audit_logs():
    logs = AuditLog.query.order_by(AuditLog.timestamp.desc()).limit(100).all()
    return jsonify([{
        "id": l.id,
        "user_id": l.user_id,
        "action": l.action,
        "resource": l.resource,
        "resource_id": l.resource_id,
        "timestamp": l.timestamp.isoformat(),
        "ip_address": l.ip_address
    } for l in logs])
