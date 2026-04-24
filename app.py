import bcrypt
from flask import Flask
from models import db, User
from config import Config
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address


from routes.auth import auth_bp
from routes.ticket import tickets_bp
from routes.audit import audit_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    limiter = Limiter(
        app=app,
        key_func=get_remote_address,
        default_limits=["200 per hour"],
        storage_uri="memory://"
    )

    app.register_blueprint(auth_bp)
    app.register_blueprint(tickets_bp)
    app.register_blueprint(audit_bp)

    limiter.limit("10 per minute")(auth_bp)

    with app.app_context():
        db.create_all()
        seed_data()

    return app


def seed_data():
    if User.query.count() == 0:
        users = [
            User(email="admin@test.ro",
            password_hash=bcrypt.hashpw("Admin@SecurePass1".encode(), bcrypt.gensalt()).decode(),
            role="MANAGER"),
            User(email="analyst@test.ro", password_hash=bcrypt.hashpw("Analyst#Strong2".encode(), bcrypt.gensalt()).decode(),
            role="ANALYST" 
            ),
            User(email="eu@test.ro", password_hash=bcrypt.hashpw("Eu#Strong2".encode(), bcrypt.gensalt()).decode(),
            role="ANALYST")
        ]
        db.session.add_all(users)
        db.session.commit()
        print("Seed")


app = create_app()
app.run(host="0.0.0.0", port=5000)
