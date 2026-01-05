from flask import Flask
from app.config import Config
from app.extensions import db, migrate, jwt
from app.utils.response import error_response
from werkzeug.exceptions import HTTPException


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # ---------------- INIT EXTENSIONS ----------------
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    # ---------------- IMPORT MODELS (ONLY ONCE) ----------------
    from app.models import user
    from app.models import auth
    from app.models import session
    from app.models import chat
    from app.models import usage
    from app.models import role
    from app.models import acl
    from app.models import role_mapping

    # ---------------- REGISTER BLUEPRINTS ----------------
    from app.routes.user import user_bp
    from app.routes.admin_rbac import admin_rbac_bp
    from app.routes.auth import auth_bp
    from app.routes.chat import chat_bp

    app.register_blueprint(user_bp, url_prefix="/user")
    app.register_blueprint(admin_rbac_bp, url_prefix="/admin/rbac")
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(chat_bp, url_prefix="/chat")

    # ---------------- JWT ERROR HANDLERS ----------------
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return error_response(
            message="Authorization token is required",
            status=401,
            error_code="TOKEN_MISSING"
        )

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return error_response(
            message="Token has expired",
            status=401,
            error_code="TOKEN_EXPIRED"
        )

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return error_response(
            message="Invalid token",
            status=401,
            error_code="INVALID_TOKEN"
        )

    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        return error_response(
            message="Token has been revoked",
            status=401,
            error_code="TOKEN_REVOKED"
        )

    # ---------------- GLOBAL ERROR HANDLER ----------------
    @app.errorhandler(Exception)
    def handle_exception(e):
        if isinstance(e, HTTPException):
            return e

        print("🔥 UNHANDLED ERROR:", str(e))

        return error_response(
            message="Internal server error",
            status=500,
            error_code="INTERNAL_ERROR"
        )

    return app