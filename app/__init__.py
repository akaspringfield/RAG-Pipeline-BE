import sys

from flask import Flask, app
from app.config import Config
from app.extensions import db, migrate, jwt
from app.utils.response import error_response
from werkzeug.exceptions import HTTPException
from flask_jwt_extended import JWTManager
from app.models.token_blacklist import TokenBlacklist


jwt = JWTManager()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # ---------------- INIT EXTENSIONS ----------------
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    # TO BLOCK AFTER LOGOUT
    @jwt.token_in_blocklist_loader
    def check_if_token_revoked(jwt_header, jwt_payload):
        jti = jwt_payload["jti"]
        token = TokenBlacklist.query.filter_by(jti=jti).first()
        return token is not None

    # ---------------- IMPORT MODELS (SAFE IMPORT) ----------------
    # Import once to register metadata (avoid circular imports carefully)
    with app.app_context():
        from app.routes.user import user_bp
        from app.routes.auth import auth_bp
        from app.routes.session import session_bp
        from app.routes.chat import chat_bp
        from app.routes.admin_rbac import admin_rbac_bp
        from app.routes.admin import admin_bp

    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(user_bp, url_prefix="/user")
    app.register_blueprint(admin_rbac_bp, url_prefix="/admin/rbac")
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(chat_bp, url_prefix="/chat")
    app.register_blueprint(session_bp, url_prefix="/session")

    # ---------------- SEED DATA (RUN ONLY ON FIRST DEPLOY) ----------------
    import os

    if (
        os.getenv("SEED_DATA") == "true"
        and "flask" not in sys.argv[0]   # 🔥 prevents during CLI
    ):
        from app.scripts.seed_superadmin import seed_superadmin
        with app.app_context():
            seed_superadmin()

    # ---------------- JWT ERROR HANDLERS ----------------
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return error_response("Authorization token is required", 401, "TOKEN_MISSING")

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return error_response("Token has expired", 401, "TOKEN_EXPIRED")

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return error_response("Invalid token", 401, "INVALID_TOKEN")

    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        return error_response("Token has been revoked", 401, "TOKEN_REVOKED")

    # ---------------- GLOBAL ERROR HANDLER ----------------
    @app.errorhandler(Exception)
    def handle_exception(e):

        if isinstance(e, HTTPException):
            return e

        print("🔥 UNHANDLED ERROR:", str(e))

        return error_response(
            message="Internal server error1",
            status=500,
            error_code="INTERNAL_ERROR"
        )

    return app
