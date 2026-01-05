from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.models.user import Client
from app.extensions import db
from app.utils.response import success_response, error_response

user_bp = Blueprint("user", __name__)

# ---------------- UPDATE PROFILE ----------------
@user_bp.route("/profile", methods=["GET"])
@jwt_required()
def get_profile():
    user_id = get_jwt_identity()

    user = Client.query.filter_by(uuid=user_id).first()

    if not user:
        return error_response("User not found", 404, "USER_NOT_FOUND")

    return success_response(
        data={
            "id": str(user.uuid),
            "name": user.client_name,
            "email": user.client_email,
            "status": user.client_status
        },
        message="Profile fetched successfully"
    )

@user_bp.route("/profile", methods=["PUT"])
@jwt_required()
def update_profile():
    user_id = get_jwt_identity()
    data = request.get_json()

    if not data:
        return error_response("Request body required", 400, "BAD_REQUEST")

    user = Client.query.filter_by(uuid=user_id).first()

    if not user:
        return error_response("User not found", 404, "USER_NOT_FOUND")

    if "name" in data:
        user.client_name = data["name"]

    if "email" in data:
        user.client_email = data["email"]

    db.session.commit()

    return success_response(
        data={
            "id": str(user.uuid),
            "name": user.client_name,
            "email": user.client_email,
            "status": user.client_status
        },
        message="Profile updated successfully"
    )