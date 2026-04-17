import hashlib
from flask import Flask
from models import db, User
from config import Config

from routes.auth import auth_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    app.register_blueprint(auth_bp)

    with app.app_context():
        db.create_all()
        seed_data()

    return app


def seed_data():
    if User.query.count() == 0:
        users = [
            User(email="admin@test.ro",
            password_hash=hashlib.md5("admin".encode()).hexdigest(),
            role="MANAGER"),
            User(email="analyst@test.ro", password_hash=hashlib.md5("password".encode()).hexdigest(),
            role="ANALYST" 
            ),
            User(email="eu@test.ro", password_hash=hashlib.md5("123456".encode()).hexdigest(),
            role="ANALYST")
        ]
        db.session.add_all(users)
        db.session.commit()
        print("Seed")


app = create_app()
app.run(host="0.0.0.0", port=5000)
