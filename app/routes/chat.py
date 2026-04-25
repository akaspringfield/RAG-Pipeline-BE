'''
Author : Akash Mambally
GitHub: https://github.com/akaspringfield
'''

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.services.chat_service import create_chat, send_message
from app.utils.response import success_response, error_response
from app.constants.error_codes import ERROR_MAP
chat_bp = Blueprint("chat", __name__)


# ---------------- CREATE CHAT ----------------
@chat_bp.route("/create", methods=["POST"]) 
@jwt_required()
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
@jwt_required()
def message():
    try:
        client_uuid = get_jwt_identity()
        data = request.get_json()

        # -------- VALIDATION --------
        if not data:
            return error_response(
                "Request body required", 400, "BAD_REQUEST"
            )

        if not data.get("chat_id") or not data.get("message"):
            return error_response(
                "chat_id and message are required", 400, "VALIDATION_ERROR"
            )

        # -------- SERVICE CALL --------
        reply, error_code, error_msg, custom_msg = send_message(
            client_uuid,
            data.get("chat_id"),
            data.get("message")
        )

        # -------- ERROR HANDLING --------
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

        # -------- SUCCESS --------
        return success_response(
            data={"reply": reply},
            message="Message processed"
        )

    except Exception as e:
        print("🔥 CHAT MESSAGE ERROR:", str(e))
        return error_response(
            "Internal server error", 500, "INTERNAL_ERROR"
        )