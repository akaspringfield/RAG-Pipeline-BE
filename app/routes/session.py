'''
Author : Akash Mambally
GitHub: https://github.com/akaspringfield
'''

from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.middleware.protected import protected
from app.services.auth_service import (
    revoke_session,
    revoke_all_sessions,
    list_sessions
)
from app.utils.response import success_response
from app.services.session_service import get_active_sessions
session_bp = Blueprint("session", __name__)


# ---------------- LOGOUT ALL DEVICES ----------------
@session_bp.route("/logout-all", methods=["POST"])
@protected("USER_READ")
def logout_all():

    user_id = get_jwt_identity()

    revoke_all_sessions(user_id)

    return success_response(message="Logged out from all devices")


# ---------------- LIST ACTIVE SESSIONS ----------------
@session_bp.route("/", methods=["GET"])
@protected("USER_READ")
def sessions():

    user_id = get_jwt_identity()

    return success_response(
        data=list_sessions(user_id),
        message="Active sessions fetched"
    )


# ---------------- ACTIVE SESSIONS ----------------
@session_bp.route("/active", methods=["GET"])
@jwt_required()
def active_sessions():

    user_id = get_jwt_identity()

    sessions = get_active_sessions(user_id)

    return success_response(
        data={"sessions": sessions},
        message="Active sessions fetched"
    )

from app.services.session_service import revoke_session_by_uuid
from flask_jwt_extended import jwt_required, get_jwt_identity


# ---------------- REVOKE SINGLE SESSION ----------------
@session_bp.route("/<session_id>/revoke", methods=["POST"])
@jwt_required()
def revoke_single(session_id):

    user_id = get_jwt_identity()

    result, error = revoke_session_by_uuid(user_id, session_id)

    if error:
        return {"error": True, "message": error}, 404

    return {
        "message": "Session revoked successfully",
        "data": result
    }, 200