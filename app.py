"""
app.py — Smart Attendance System main application entry point.
Initializes Flask, blueprints, authentication, rate limiting, and error handlers.
"""

import os
from flask import Flask, app, render_template, request
from flask_login import LoginManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from config import config_map
from models import db, User
from services import bcrypt
from middleware import admin_required, teacher_required, student_required


def create_app(env="development"):
    """Application factory."""
    app = Flask(__name__, template_folder="templates", static_folder="static")

    # Load configuration
    config = config_map.get(env, config_map["development"])
    app.config.from_object(config)
    print("CONFIG CLASS =", config)
    print("QR_CODES_DIR =", app.config.get("QR_CODES_DIR"))
    print("EXPORTS_DIR =", app.config.get("EXPORTS_DIR"))

    # Initialize extensions
    db.init_app(app)
    bcrypt.init_app(app)

    # Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Please log in to continue."

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Rate limiting
    limiter = Limiter(
        app=app,
        key_func=get_remote_address,
        default_limits=["200 per day", "50 per hour"],
        storage_uri=app.config["RATELIMIT_STORAGE_URL"],
    )

    # Create directories
    qr_dir = app.config.get("QR_CODES_DIR", "qr_codes")
    export_dir = app.config.get("EXPORTS_DIR", "exports")

    os.makedirs(qr_dir, exist_ok=True)
    os.makedirs(export_dir, exist_ok=True)

    # Register blueprints
    from routes.auth import auth_bp
    from routes.admin import admin_bp
    from routes.teacher import teacher_bp
    from routes.student import student_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(teacher_bp)
    app.register_blueprint(student_bp)

    # Error handlers
    @app.errorhandler(404)
    def not_found(e):
        return render_template("errors/404.html"), 404

    @app.errorhandler(403)
    def forbidden(e):
        return render_template("errors/403.html"), 403

    @app.errorhandler(500)
    def server_error(e):
        return render_template("errors/500.html"), 500

    # Rate limit error handler
    @app.errorhandler(429)
    def ratelimit_handler(e):
        return render_template("errors/429.html", message=str(e.description)), 429

    # Database initialization with context
    @app.before_request
    def before_request():
        """Ensure tables exist and seed initial data on first run."""
        if not app.config.get("_db_initialized"):
            with app.app_context():
                try:
                    db.create_all()
                    # Seed admin if not exists
                    if User.query.filter_by(role="admin").count() == 0:
                        admin_email = os.environ.get("ADMIN_EMAIL", "admin@school.edu")
                        admin_pass = os.environ.get("ADMIN_PASSWORD", "Admin@1234")
                        from services.auth_service import hash_password
                        admin = User(
                            email=admin_email,
                            password_hash=hash_password(admin_pass),
                            role="admin",
                        )
                        db.session.add(admin)
                        db.session.commit()
                    app.config["_db_initialized"] = True
                except Exception as e:
                    print(f"DB init error: {e}")

    return app


# Vercel needs a top-level Flask app instance


app = create_app(os.environ.get("FLASK_ENV", "development"))

if __name__ == "__main__":
    app.run(
        debug=True,
        host="0.0.0.0",
        port=5000
    )


