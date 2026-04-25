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
from app.services.auth_service import logout_all_sessions
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

    user, error = authenticate_user(
        data.get("email"),
        data.get("password")
    )

    if error:
        return error_response(error, 401, error)

    access_token = create_access_token(identity=str(user.uuid))
    refresh_token = create_refresh_token(identity=str(user.uuid))

    store_session(
        user_uuid=user.uuid,
        refresh_token=refresh_token,
        device_info=request.headers.get("User-Agent"),
        ip_address=request.remote_addr
    )

    return success_response(
        data={
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user": {
                "uuid": str(user.uuid),
                "name": user.client_name,
                "email": user.client_email
            }
        },
        message="Login successful"
    )


# ---------------- REFRESH ----------------
@auth_bp.route("/refresh", methods=["POST"])
def refresh():
    data = request.get_json()

    if not data:
        return error_response("Request body required", 400, "BAD_REQUEST")

    access_token, error = refresh_session(data.get("refresh_token"))

    if error:
        return error_response(error, 401, "INVALID_REFRESH")

    return success_response(
        data={"access_token": access_token},
        message="Token refreshed"
    )


# ---------------- LOGOUT ----------------

@auth_bp.route("/logout", methods=["POST"])
@jwt_required()
def logout():

    data = request.get_json()
    refresh_token = data.get("refresh_token")

    if not refresh_token:
        return error_response("refresh_token required", 400, "BAD_REQUEST")

    jwt_data = get_jwt()
    jti = jwt_data["jti"]
    user_id = get_jwt_identity()

    revoke_session(
        refresh_token,
        access_jti=jti,
        user_id=user_id
    )

    return success_response(message="Logged out successfully")


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
    data = request.get_json()

    if not data:
        return error_response("Request body required", 400, "BAD_REQUEST")

    result, error = reset_password(
        data.get("email"),
        data.get("token"),
        data.get("new_password")
    )

    if error:
        return error_response(error, 400, error)

    return success_response(
        data=result,
        message="Password updated successfully"
    )


# ---------------- LOGOUT ALL SESSIONS ----------------
@auth_bp.route("/logout-all", methods=["POST"])
@jwt_required()
def logout_all():

    user_id = get_jwt_identity()

    success, error = logout_all_sessions(user_id)

    if error:
        return error_response(error, 400, "LOGOUT_ALL_FAILED")

    return success_response(
        message="All sessions logged out successfully"
    )