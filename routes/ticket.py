from flask import Blueprint, request, jsonify, render_template
from datetime import datetime
from markupsafe import escape

from models import db, Ticket, AuditLog
from routes.auth import login_required, get_current_user

tickets_bp = Blueprint("tickets", __name__)


@tickets_bp.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html", user=request.current_user)


@tickets_bp.route("/api/tickets", methods=["GET"])
@login_required
def list_tickets():
    user = request.current_user

    if user.role == "MANAGER":
        tickets = Ticket.query.all()
    else:
        tickets = Ticket.query.filter_by(owner_id=user.id).all()

    return jsonify([{
        "id": t.id,
        "title": escape(t.title),
        "description": escape(t.description) if t.description else "",
        "severity": t.severity,
        "status": t.status,
        "owner_id": t.owner_id,
        "created_at": t.created_at.isoformat(),
        "updated_at": t.updated_at.isoformat() if t.updated_at else None
    } for t in tickets])


@tickets_bp.route("/api/tickets", methods=["POST"])
@login_required
def create_ticket():
    data = request.get_json()
    user = request.current_user

    title = data.get("title", "").strip()
    description = data.get("description", "").strip()
    severity = data.get("severity", "LOW")

    if not title or len(title) > 255:
        return jsonify({"error": "Titlul este obligatoriu (max 255 caractere)"}), 400
    if severity not in ("LOW", "MED", "HIGH"):
        return jsonify({"error": "Severitate invalida"}), 400
    if len(description) > 5000:
        return jsonify({"error": "Descrierea este prea lunga (max 5000 caractere)"}), 400

    ticket = Ticket(
        title=title,
        description=description,
        severity=severity,
        owner_id=user.id
    )
    db.session.add(ticket)
    db.session.commit()

    log = AuditLog(
        user_id=user.id, action="CREATE_TICKET", resource="ticket",
        resource_id=str(ticket.id), ip_address=request.remote_addr
    )
    db.session.add(log)
    db.session.commit()

    return jsonify({"message": "Ticket creat", "id": ticket.id}), 201


@tickets_bp.route("/api/tickets/<int:ticket_id>", methods=["GET"])
@login_required
def get_ticket(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)
    user = request.current_user

    if user.role != "MANAGER" and ticket.owner_id != user.id:
        return jsonify({"error": "Acces interzis"}), 403

    return jsonify({
        "id": ticket.id,
        "title": escape(ticket.title),
        "description": escape(ticket.description) if ticket.description else "",
        "severity": ticket.severity,
        "status": ticket.status,
        "owner_id": ticket.owner_id,
        "created_at": ticket.created_at.isoformat()
    })


@tickets_bp.route("/api/tickets/<int:ticket_id>", methods=["PUT"])
@login_required
def update_ticket(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)
    user = request.current_user

    if user.role != "MANAGER" and ticket.owner_id != user.id:
        return jsonify({"error": "Acces interzis"}), 403

    data = request.get_json()
    if "title" in data:
        title = data["title"].strip()
        if not title or len(title) > 255:
            return jsonify({"error": "Titlu invalid"}), 400
        ticket.title = title
    if "description" in data:
        desc = data["description"].strip()
        if len(desc) > 5000:
            return jsonify({"error": "Descriere prea lunga"}), 400
        ticket.description = desc
    if "severity" in data:
        if data["severity"] not in ("LOW", "MED", "HIGH"):
            return jsonify({"error": "Severitate invalida"}), 400
        ticket.severity = data["severity"]
    if "status" in data:
        if data["status"] not in ("OPEN", "IN_PROGRESS", "RESOLVED"):
            return jsonify({"error": "Status invalid"}), 400
        ticket.status = data["status"]

    ticket.updated_at = datetime.utcnow()
    db.session.commit()

    log = AuditLog(
        user_id=user.id, action="UPDATE_TICKET", resource="ticket",
        resource_id=str(ticket.id), ip_address=request.remote_addr
    )
    db.session.add(log)
    db.session.commit()

    return jsonify({"message": "Ticket actualizat"})


@tickets_bp.route("/api/tickets/<int:ticket_id>", methods=["DELETE"])
@login_required
def delete_ticket(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)
    user = request.current_user

    if user.role != "MANAGER" and ticket.owner_id != user.id:
        return jsonify({"error": "Acces interzis"}), 403

    db.session.delete(ticket)
    db.session.commit()

    log = AuditLog(
        user_id=user.id, action="DELETE_TICKET", resource="ticket",
        resource_id=str(ticket_id), ip_address=request.remote_addr
    )
    db.session.add(log)
    db.session.commit()

    return jsonify({"message": "Ticket sters"})


@tickets_bp.route("/api/tickets/search", methods=["GET"])
@login_required
def search_tickets():
    query = request.args.get("q", "").strip()
    user = request.current_user

    if not query or len(query) > 200:
        return jsonify([])

    base_query = Ticket.query.filter(Ticket.title.ilike(f"%{query}%"))
    if user.role != "MANAGER":
        base_query = base_query.filter_by(owner_id=user.id)

    tickets = base_query.limit(50).all()

    return jsonify([{
        "id": t.id,
        "title": escape(t.title),
        "description": escape(t.description) if t.description else "",
        "severity": t.severity,
        "status": t.status,
        "owner_id": t.owner_id
    } for t in tickets])