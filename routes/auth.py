import re
import time
import secrets
import bcrypt
import jwt
from datetime import datetime, timedelta
from functools import wraps
from flask import Blueprint, request, jsonify, make_response, current_app, render_template, redirect, url_for

from models import db, User, PasswordReset, AuditLog

auth_bp = Blueprint("auth", __name__)


def validate_password(password):
    errors = []
    cfg = current_app.config
    if len(password) < cfg.get("PASSWORD_MIN_LENGTH", 8):
        errors.append(f"Parola trebuie sa aiba minim {cfg['PASSWORD_MIN_LENGTH']} caractere")
    if cfg.get("PASSWORD_REQUIRE_UPPERCASE") and not re.search(r"[A-Z]", password):
        errors.append("Parola trebuie sa contina cel putin o litera mare")
    if cfg.get("PASSWORD_REQUIRE_LOWERCASE") and not re.search(r"[a-z]", password):
        errors.append("Parola trebuie sa contina cel putin o litera mica")
    if cfg.get("PASSWORD_REQUIRE_DIGIT") and not re.search(r"\d", password):
        errors.append("Parola trebuie sa contina cel putin o cifra")
    if cfg.get("PASSWORD_REQUIRE_SPECIAL") and not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        errors.append("Parola trebuie sa contina cel putin un caracter special")
    return errors


def hash_password(password):
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password, password_hash):
    return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))


def get_current_user():
    token = request.cookies.get("session_token")
    if not token:
        return None
    try:
        if token in current_app.config.get("JWT_BLACKLIST", set()):
            return None
        payload = jwt.decode(token, current_app.config["SECRET_KEY"], algorithms=["HS256"])
        user = User.query.get(payload["user_id"])
        return user
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None


def check_account_lock(user):
    if user.locked and user.locked_until:
        if datetime.utcnow() > user.locked_until:
            user.locked = False
            user.failed_attempts = 0
            user.locked_until = None
            db.session.commit()
            return False
        return True
    return False


def increment_failed_attempts(user):
    user.failed_attempts += 1
    max_attempts = current_app.config.get("MAX_LOGIN_ATTEMPTS", 5)
    if user.failed_attempts >= max_attempts:
        lockout_seconds = current_app.config.get("LOCKOUT_DURATION_SECONDS", 900)
        user.locked = True
        user.locked_until = datetime.utcnow() + timedelta(seconds=lockout_seconds)
        db.session.commit()
        return True
    db.session.commit()
    return False


def _enforce_min_response_time(start_time, min_seconds=0.3):
    elapsed = time.time() - start_time
    if elapsed < min_seconds:
        time.sleep(min_seconds - elapsed)


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


@auth_bp.route("/forgot-password", methods=["GET"])
def forgot_password_page():
    return render_template("forgot_password.html")


@auth_bp.route("/reset-password/<token>", methods=["GET"])
def reset_password_page(token):
    return render_template("reset_password.html", token=token)


@auth_bp.route("/api/register", methods=["POST"])
def register():
    data = request.get_json()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")
    confirmPassword = data.get("confirmPassword", "")
    role = data.get("role", "ANALYST")

    if not email or not re.match(r"^[^@]+@[^@]+\.[^@]+$", email):
        return jsonify({"error": "Adresa de email invalida"}), 400

    if role not in ("ANALYST", "MANAGER"):
        return jsonify({"error": "Rol invalid"}), 400

    if password != confirmPassword:
        return jsonify({"error": "Cele 2 parole nu sunt la fel"}), 401

    password_errors = validate_password(password)
    if password_errors:
        return jsonify({"error": "Parola nu indeplineste cerintele", "details": password_errors}), 400

    existing = User.query.filter_by(email=email).first()
    if existing:
        return jsonify({"message": "Daca adresa este valida, contul va fi creat. Verifica email-ul."}), 201

    password_hash = hash_password(password)

    user = User(email=email, password_hash=password_hash, role=role)
    db.session.add(user)
    db.session.commit()

    log = AuditLog(
        user_id=user.id, action="REGISTER", resource="auth",
        ip_address=request.remote_addr
    )
    db.session.add(log)
    db.session.commit()

    return jsonify({"message": "Daca adresa este valida, contul va fi creat. Verifica email-ul."}), 201


@auth_bp.route("/api/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    generic_error = "Credentiale invalide"
    start_time = time.time()

    user = User.query.filter_by(email=email).first()

    if not user:
        bcrypt.hashpw(b"dummy_password", bcrypt.gensalt())
        _enforce_min_response_time(start_time)
        return jsonify({"error": generic_error}), 401

    if check_account_lock(user):
        remaining = int((user.locked_until - datetime.utcnow()).total_seconds())
        _enforce_min_response_time(start_time)
        log = AuditLog(
            user_id=user.id, action="LOGIN_BLOCKED", resource="auth",
            ip_address=request.remote_addr,
            details=f"Cont blocat, mai raman {remaining}s"
        )
        db.session.add(log)
        db.session.commit()
        return jsonify({"error": f"Contul este blocat temporar. Reincearca peste {remaining // 60 + 1} minute."}), 429

    if not verify_password(password, user.password_hash):
        locked = increment_failed_attempts(user)

        log = AuditLog(
            user_id=user.id, action="LOGIN_FAILED", resource="auth",
            ip_address=request.remote_addr,
            details=f"Tentativa {user.failed_attempts}/{current_app.config.get('MAX_LOGIN_ATTEMPTS', 5)}"
        )
        db.session.add(log)
        db.session.commit()

        _enforce_min_response_time(start_time)
        if locked:
            return jsonify({"error": "Prea multe incercari. Contul a fost blocat temporar."}), 429
        return jsonify({"error": generic_error}), 401

    user.failed_attempts = 0
    user.locked = False
    user.locked_until = None
    db.session.commit()

    payload = {
        "user_id": user.id,
        "email": user.email,
        "role": user.role,
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(seconds=current_app.config["JWT_EXPIRY"]),
        "jti": secrets.token_hex(16)
    }
    token = jwt.encode(payload, current_app.config["SECRET_KEY"], algorithm="HS256")

    log = AuditLog(
        user_id=user.id, action="LOGIN_SUCCESS", resource="auth",
        ip_address=request.remote_addr
    )
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
        httponly=True,
        secure=False,
        samesite="Lax"
    )

    _enforce_min_response_time(start_time)
    return response


@auth_bp.route("/api/logout", methods=["POST"])
def logout():
    token = request.cookies.get("session_token")
    user = get_current_user()

    if token:
        current_app.config.setdefault("JWT_BLACKLIST", set()).add(token)

    response = make_response(jsonify({"message": "Deconectat"}))
    response.delete_cookie("session_token")

    if user:
        log = AuditLog(
            user_id=user.id, action="LOGOUT", resource="auth",
            ip_address=request.remote_addr
        )
        db.session.add(log)
        db.session.commit()

    return response


@auth_bp.route("/api/forgot-password", methods=["POST"])
def forgot_password():
    data = request.get_json()
    email = data.get("email", "").strip().lower()

    generic_msg = "Daca adresa de email este inregistrata, vei primi un link de resetare."

    user = User.query.filter_by(email=email).first()
    if not user:
        time.sleep(0.1)
        return jsonify({"message": generic_msg})

    token = secrets.token_urlsafe(32)
    expires_at = datetime.utcnow() + timedelta(
        seconds=current_app.config.get("RESET_TOKEN_EXPIRY_SECONDS", 3600)
    )

    PasswordReset.query.filter_by(user_id=user.id, used=False).update({"used": True})

    reset = PasswordReset(user_id=user.id, token=token, expires_at=expires_at)
    db.session.add(reset)
    db.session.commit()

    reset_link = f"/reset-password/{token}"

    log = AuditLog(
        user_id=user.id, action="PASSWORD_RESET_REQUEST", resource="auth",
        ip_address=request.remote_addr
    )
    db.session.add(log)
    db.session.commit()

    return jsonify({
        "message": generic_msg,
        "reset_link": reset_link,
        "token": token
    })


@auth_bp.route("/api/reset-password", methods=["POST"])
def reset_password():
    data = request.get_json()
    token = data.get("token", "")
    new_password = data.get("new_password", "")

    if not token or not new_password:
        return jsonify({"error": "Token si parola noua sunt obligatorii"}), 400

    password_errors = validate_password(new_password)
    if password_errors:
        return jsonify({"error": "Parola nu indeplineste cerintele", "details": password_errors}), 400

    reset = PasswordReset.query.filter_by(token=token).first()
    if not reset:
        return jsonify({"error": "Token invalid sau expirat"}), 400

    if reset.used:
        return jsonify({"error": "Token invalid sau expirat"}), 400

    if datetime.utcnow() > reset.expires_at:
        return jsonify({"error": "Token invalid sau expirat"}), 400

    user = User.query.get(reset.user_id)
    if not user:
        return jsonify({"error": "Token invalid sau expirat"}), 400

    user.password_hash = hash_password(new_password)

    reset.used = True
    db.session.commit()

    log = AuditLog(
        user_id=user.id, action="PASSWORD_RESET", resource="auth",
        ip_address=request.remote_addr
    )
    db.session.add(log)
    db.session.commit()

    return jsonify({"message": f"Parola a fost resetata pt {user.email}"})


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        user = get_current_user()
        if not user:
            if request.is_json or request.path.startswith("/api/"):
                return jsonify({"error": "Nu esti autentificat"}), 401
            return redirect(url_for("auth.login_page"))
        request.current_user = user
        return f(*args, **kwargs)
    return decorated


def manager_required(f):
    @wraps(f)
    @login_required
    def decorated(*args, **kwargs):
        if request.current_user.role != "MANAGER":
            return jsonify({"error": "Acces Interzis"}), 403
        return f(*args, **kwargs)
    return decorated


@auth_bp.route("/api/me", methods=["GET"])
@login_required
def me():
    user = request.current_user
    return jsonify({
        "id": user.id,
        "email": user.email,
        "role": user.role,
        "created_at": user.created_at.isoformat()
    })