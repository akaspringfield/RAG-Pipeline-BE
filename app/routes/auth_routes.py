'''
Author : Akash Mambally
GitHub: https://github.com/akaspringfield
'''

from flask import Blueprint, request, jsonify
from app.services.auth_service import reset_password_service

auth_bp = Blueprint("auth_bp", __name__)


@auth_bp.route("/auth/reset-password", methods=["POST"])
def reset_password():
    try:
        data = request.get_json()

        user_uuid = data.get("user_uuid")
        current_password = data.get("current_password")
        new_password = data.get("new_password")

        # Validate input
        if not user_uuid or not current_password or not new_password:
            return jsonify({
                "success": False,
                "error_code": "VALIDATION_ERROR",
                "message": "user_uuid, current_password and new_password are required"
            }), 400

        success, error = reset_password_service(
            user_uuid, current_password, new_password
        )

        if error == "USER_NOT_FOUND":
            return jsonify({
                "success": False,
                "error_code": error,
                "message": "User not found"
            }), 404

        if error == "USER_INACTIVE":
            return jsonify({
                "success": False,
                "error_code": error,
                "message": "User is inactive"
            }), 403

        if error == "PASSWORD_RECORD_NOT_FOUND":
            return jsonify({
                "success": False,
                "error_code": error,
                "message": "Password record not found"
            }), 404

        if error == "INVALID_CURRENT_PASSWORD":
            return jsonify({
                "success": False,
                "error_code": error,
                "message": "Current password is incorrect"
            }), 401

        if error == "INTERNAL_ERROR":
            return jsonify({
                "success": False,
                "error_code": error,
                "message": "Internal server error"
            }), 500

        return jsonify({
            "success": True,
            "message": "Password updated successfully"
        }), 200

    except Exception as e:
        print("🔥 UNHANDLED ERROR:", str(e))
        return jsonify({
            "success": False,
            "error_code": "INTERNAL_ERROR",
            "message": "Internal server error"
        }), 500