from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.middleware.protected import protected

from app.services.chat_service import create_chat, send_message
from app.utils.response import success_response, error_response
from app.constants.error_codes import ERROR_MAP

from app.models.user import Client
from app.models.acl import ClientACL
from app.utils.permissions import has_access


chat_bp = Blueprint("chat", __name__)


# ---------------- CREATE CHAT ----------------
@chat_bp.route("/create", methods=["POST"])
@protected("USER_READ")
def create():
    client_uuid = get_jwt_identity()
    data = request.json

    chat = create_chat(client_uuid, data.get("title", "New Chat"))

    return jsonify({
        "chat_id": str(chat.uuid),
        "title": chat.chat_title
    })


# ---------------- SEND MESSAGE ----------------
@chat_bp.route("/message", methods=["POST"])
@protected("USER_READ")
def message():
    client_uuid = get_jwt_identity()
    data = request.get_json()

    # ---------------- USER FETCH ----------------
    user = Client.query.filter_by(uuid=client_uuid).first()
    if not user:
        return error_response(
            message="User not found",
            status=404,
            error_code="USER_NOT_FOUND"
        )

    # ---------------- ACL FETCH ----------------
    acl = ClientACL.query.filter_by(acl_title="CHAT_SEND").first()
    if not acl:
        return error_response(
            message="ACL not configured",
            status=500,
            error_code="ACL_NOT_FOUND"
        )

    # ---------------- PERMISSION CHECK ----------------
    if not has_access(user.role_uuid, acl.uuid):
        return error_response(
            message="Access denied",
            status=403,
            error_code="FORBIDDEN"
        )

    # ---------------- VALIDATION ----------------
    if not data:
        return error_response(
            message="Request body required",
            status=400,
            error_code="BAD_REQUEST"
        )

    if not data.get("chat_id") or not data.get("message"):
        return error_response(
            message="chat_id and message are required",
            status=400,
            error_code="VALIDATION_ERROR"
        )

    # ---------------- SERVICE CALL ----------------
    reply, error_code, error_msg, custom_msg = send_message(
        client_uuid,
        data.get("chat_id"),
        data.get("message")
    )

    # ---------------- ERROR HANDLING ----------------
    if error_code:
        meta = ERROR_MAP.get(error_code, {
            "status": 500,
            "message": "Unknown error"
        })

        return error_response(
            message=custom_msg or meta["message"],
            status=meta["status"],
            error_code=error_code,
            error=error_msg
        )

    # ---------------- SUCCESS ----------------
    return success_response(
        data={"reply": reply},
        message="Message processed"
    )