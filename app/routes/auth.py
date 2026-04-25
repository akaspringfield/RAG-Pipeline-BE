'''
Author : Akash Mambally
GitHub: https://github.com/akaspringfield
'''

from flask import Blueprint, request
from flask_jwt_extended import create_access_token, create_refresh_token
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity
from app.services.auth_service import (
    register_user,
    authenticate_user,
    store_session,
    refresh_session,
    revoke_session,
    forgot_password,
    reset_password
)

from app.utils.response import success_response, error_response
from app.services.auth_service import logout_all_sessions,login_user
from app.models.session import ClientSession
from app.models.user import Client
from app.extensions import db
from app.models.token_blacklist import TokenBlacklist
from datetime import datetime
auth_bp = Blueprint("auth", __name__)


# ---------------- HEALTH ----------------
@auth_bp.route("/health", methods=["GET"])
def health():
    return {"message": "application is healthy"}


# ---------------- REGISTER ----------------
@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()

    if not data:
        return error_response("Request body required", 400, "BAD_REQUEST")

    user, error = register_user(
        data.get("name"),
        data.get("email"),
        data.get("password")
    )

    if error:
        return error_response(error, 400, "REGISTER_FAILED")

    return success_response(
        data={"user_id": str(user.uuid)},
        message="User created"
    )


# ---------------- LOGIN ----------------
@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    if not data:
        return error_response("Request body required", 400, "BAD_REQUEST")

    access_token, refresh_token, error = login_user(
        data.get("email"),
        data.get("password")
    )

    if error:
        return error_response(error, 401, error)

    return success_response(
        data={
            "access_token": access_token,
            "refresh_token": refresh_token
        },
        message="Login successful"
    )

# hasing function for refresh token
import hashlib

def hash_refresh_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


# ---------------- REFRESH TOKEN ----------------
@auth_bp.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh_token():
    try:
        print("🔄 Refresh requested")
        # JWT already validated by decorator
        client_uuid = get_jwt_identity()
        jwt_data = get_jwt()

        # Extract refresh token from header
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return error_response("Authorization header missing", 401, "INVALID_REFRESH")

        refresh_token = auth_header.split(" ")[1]

        print("🔄 Refresh for user:", client_uuid)

        # 1️⃣ Check client exists
        client = Client.query.get(client_uuid)
        if not client:
            return error_response("User not found", 404, "USER_NOT_FOUND")

        # hash incoming refresh token
        incoming_hash = hash_refresh_token(refresh_token)
        print(f"User {client_uuid} ---  red - {refresh_token} incoming_hash - {incoming_hash}")

        # 2️⃣ Check refresh token in DB session table
        session = ClientSession.query.filter_by(
            client_uuid=client_uuid,
            refresh_token_hash=incoming_hash,
            is_revoked=False
        ).first()

        if not session:
            print("❌ Refresh token not found in DB")
            return error_response("Invalid refresh token", 401, "INVALID_REFRESH")

        # 3️⃣ Generate new access token
        new_access_token = create_access_token(identity=str(client.uuid))

        print("✅ New access token issued")

        return success_response(
            data={"access_token": new_access_token},
            message="Token refreshed successfully"
        )

    except Exception as e:
        print("🔥 REFRESH ERROR:", str(e))
        return error_response("Internal server error", 500, "INVALID_REFRESH")


@auth_bp.route("/logout", methods=["POST"])
@jwt_required()
def logout():
    try:
        data = request.get_json() or {}
        refresh_token = data.get("refresh_token")

        if not refresh_token:
            return error_response("refresh_token required", 400, "BAD_REQUEST")

        # JWT data
        jwt_data = get_jwt()
        jti = jwt_data["jti"]

        # user id from JWT
        user_uuid = get_jwt_identity()

        # blacklist access token WITH user_id
        revoked_token = TokenBlacklist(
            jti=jti,
            user_id=user_uuid,
            revoked_at=datetime.utcnow()
        )

        db.session.add(revoked_token)

        # optional: revoke session logic
        incoming_hash = hash_refresh_token(refresh_token)

        session_obj = ClientSession.query.filter_by(
            client_uuid=user_uuid,
            refresh_token_hash=incoming_hash,
            is_revoked=False
        ).first()

        if not session_obj:
            return error_response("Session not found", 404, "SESSION_NOT_FOUND")

        session_obj.is_revoked = True

        db.session.commit()

        return success_response(message="Logged out successfully")

    except Exception as e: 
        import traceback
        print("LOGOUT ERROR:", traceback.format_exc())
        return error_response("Internal server error", 500, "LOGOUT_FAILED")


# ---------------- FORGOT PASSWORD ----------------
@auth_bp.route("/forgot-password", methods=["POST"])
def forgot():
    data = request.get_json()

    if not data or not data.get("email"):
        return error_response("Email required", 400, "VALIDATION_ERROR")

    result, error = forgot_password(data.get("email"))

    if error:
        return error_response(error, 404, error)

    return success_response(
        data=result,
        message="Reset token generated"
    )


# ---------------- RESET PASSWORD ----------------
@auth_bp.route("/reset-password", methods=["POST"])
def reset():
    try:
        data = request.get_json()

        if not data:
            return error_response("Request body required", 400, "BAD_REQUEST")

        result, error = reset_password(
            data.get("user_uuid"),
            data.get("current_password"),
            data.get("new_password")
        )

        # ❌ service returned business error
        if error:
            return error_response(error, 400, error)

        # ✅ success
        return success_response(
            data=result,
            message="Password updated successfully"
        )

    except Exception as e:
        print("🔥 RESET ROUTE ERROR:", str(e))
        return error_response("Internal server error", 500, "INTERNAL_ERROR")


# ---------------- LOGOUT ALL SESSIONS ----------------
@auth_bp.route("/logout-all", methods=["POST"])
@jwt_required()
def logout_all():
    try:
        user_id = get_jwt_identity()
        print("USER_ID FROM JWT:", get_jwt_identity())
        if not user_id:
            return error_response("Invalid user session", 401, "INVALID_USER")

        jwt_data = get_jwt()
        jti = jwt_data["jti"]

        # blacklist current access token (optional but fine)
        db.session.add(TokenBlacklist(
            jti=jti,
            user_id=user_id,
            revoked_at=datetime.utcnow()
        ))

        # revoke ALL sessions for this user
        ClientSession.query.filter_by(
            client_uuid=user_id,
            is_revoked=False
        ).update({"is_revoked": True})

        db.session.commit()

        return success_response(message="All sessions logged out successfully")

    except Exception as e:
        import traceback
        print("LOGOUT-ALL ERROR:", traceback.format_exc())
        return error_response("Internal server error", 500, "LOGOUT_ALL_FAILED")


# ---------------- UPDATE PASSWORD (LOGGED IN USER) ----------------
from werkzeug.security import check_password_hash, generate_password_hash

@auth_bp.route("/update-password", methods=["POST"])
@jwt_required()
def update_password():
    try:
        client_uuid = get_jwt_identity()
        data = request.get_json()

        if not data:
            return error_response("Request body required", 400, "BAD_REQUEST")

        current_password = data.get("current_password")
        new_password = data.get("new_password")

        if not current_password or not new_password:
            return error_response(
                "current_password and new_password required",
                400,
                "VALIDATION_ERROR"
            )

        # 1️⃣ get user
        client = Client.query.get(client_uuid)
        if not client:
            return error_response("User not found", 404, "USER_NOT_FOUND")

        # 2️⃣ verify current password
        if not check_password_hash(client.password_hash, current_password):
            return error_response(
                "Current password is incorrect",
                401,
                "INVALID_PASSWORD"
            )

        # 3️⃣ update password
        client.password_hash = generate_password_hash(new_password)
        db.session.commit()

        return success_response(
            message="Password updated successfully"
        )

    except Exception as e:
        print("🔥 UPDATE PASSWORD ERROR:", str(e))
        return error_response("Internal server error", 500, "UPDATE_PASSWORD_FAILED")