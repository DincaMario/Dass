import hashlib
import time
import jwt
from datetime import datetime, timedelta
from functools import wraps
from flask import Blueprint, request, jsonify, make_response, current_app, render_template, redirect, url_for

from models import db, User, PasswordReset, AuditLog

auth_bp = Blueprint("auth", __name__)

def get_current_user():
    token = request.cookies.get("session_token")
    if not token:
        return None
    try:
        payload = jwt.decode(token, current_app.config["SECRET_KEY"], algorithms=["HS256"])
        user = User.query.get(payload["user_id"])
        return user
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None

@auth_bp.route("/")
def index():
    user = get_current_user()
    if user:
        return redirect(url_for("tickets.dashboard"))
    return redirect(url_for("auth.login_page"))

@auth_bp.route("/register", methods=["GET"])
def register_page():
    return render_template("register.html")

@auth_bp.route("/login", methods=["GET"])
def login_page():
    return render_template("login.html")


@auth_bp.route("/api/register", methods=["POST"])
def register():
    data = request.get_json()
    email = data.get("email", "").strip()
    password = data.get("password", "")
    confirmPassword = data.get("confirmPassword", "")
    role = data.get("role", "ANALYST")

    if not email or not password and password == confirmPassword:
        return jsonify({"error": "Email-ul si parola sunt obligatorii"}), 400

    existing = User.query.filter_by(email=email).first()
    if existing:
        return jsonify({"error": f"Utilizatorul '{email}' deja exista"}), 409

    password_hash = hashlib.md5(password.encode()).hexdigest()

    user = User(email=email, password_hash=password_hash, role=role)
    db.session.add(user)
    db.session.commit()

    log = AuditLog(
        user_id=user.id, action="REGISTER", resource="auth",
        ip_address=request.remote_addr
    )
    db.session.add(log)
    db.session.commit()

    return jsonify({"message": f"Cont creat cu success pentru {email}", "user_id": user.id}),201





@auth_bp.route("/api/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email", "").strip()
    password = data.get("password", "")
    
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"error": "Utilizatorul nu exista"})
    
    if user.locked:
        return jsonify({"error":"Contul este blocat"}), 403

    password_hash = hashlib.md5(password.encode()).hexdigest()
    
    if user.password_hash != password_hash:
        log =AuditLog(user_id=user.id, action="LOGIN_FAILED", resource="auth",
                        ip_address=request.remote_addr)
        db.session.add(log)
        db.session.commit()
        return jsonify({"error": "Parola este gresita"})

    payload = {
        "user_id": user.id,
        "email": user.email,
        "role": user.role,
        "exp": datetime.utcnow() + timedelta(seconds=current_app.config["JWT_EXPIRY"])
    }
    token = jwt.encode(payload, current_app.config["SECRET_KEY"], algorithm="HS256")

    log =AuditLog(user_id=user.id, action="LOGIN_SUCCESS", resource="auth",
                        ip_address=request.remote_addr)
    
    db.session.add(log)
    db.session.commit()

    response = make_response(jsonify({
        "message": "Autentificare reusita",
        "user": {"id": user.id, "email": user.email, "role": user.role}
    }))

    response.set_cookie(
        "session_token",
        token,
        max_age=current_app.config["JWT_EXPIRY"],
        httponly=False,
        secure=False,
        samesite=None
    )

    return response