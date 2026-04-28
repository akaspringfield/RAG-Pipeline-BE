'''
Author : Akash Mambally
GitHub: https://github.com/akaspringfield
'''

from flask import Blueprint, request
from flask_jwt_extended import jwt_required

from app.middleware.rbac import require_acl
from app.services.admin_service import (
    list_all_users,
    list_all_acls,
    toggle_user_status
)
from app.utils.response import success_response, error_response
from app.utils.decorators import protected

admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/users", methods=["GET"])
@jwt_required()
@protected("CHAT_SEND")
def get_users():

    users = list_all_users()

    return success_response(
        data=users,
        message="Users fetched successfully"
    )


@admin_bp.route("/acls", methods=["GET"])
@jwt_required()
@protected("CHAT_SEND")
def get_acls():

    data = list_all_acls()

    return success_response(
        data=data,
        message="ACLs fetched successfully"
    )


@admin_bp.route("/user/status", methods=["POST"])
@jwt_required()
@protected("CHAT_SEND")
def update_user_status():

    data = request.get_json()

    user_id = data.get("user_id")
    status = data.get("status")  # ACTIVE / INACTIVE

    result, error = toggle_user_status(user_id, status)

    if error:
        return error_response(error, 400, "UPDATE_FAILED")

    return success_response(
        data=result,
        message="User status updated"
    )

