from flask import Blueprint, request, jsonify, render_template
from datetime import datetime

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
        "title": t.title,
        "description": t.description,  
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

    title = data.get("title", "")
    description = data.get("description", "")
    severity = data.get("severity", "LOW")

    if not title:
        return jsonify({"error": "Titlul este obligatoriu"}), 400

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


    return jsonify({
        "id": ticket.id,
        "title": ticket.title,
        "description": ticket.description,
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

    data = request.get_json()
    if "title" in data:
        ticket.title = data["title"]
    if "description" in data:
        ticket.description = data["description"]
    if "severity" in data:
        ticket.severity = data["severity"]
    if "status" in data:
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
    query = request.args.get("q", "")
    user = request.current_user

    
    tickets = Ticket.query.filter(
        Ticket.title.ilike(f"%{query}%")
    ).all()

    return jsonify([{
        "id": t.id,
        "title": t.title,
        "description": t.description,
        "severity": t.severity,
        "status": t.status,
        "owner_id": t.owner_id
    } for t in tickets])
