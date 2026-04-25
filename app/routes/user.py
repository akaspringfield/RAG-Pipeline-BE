'''
Author : Akash Mambally
GitHub: https://github.com/akaspringfield
'''

from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.models.user import Client
from app.extensions import db
from app.utils.response import success_response, error_response
from app.services.rbac_service import has_access
from app.middleware.protected import protected

from app.services.user_service import list_users
from app.middleware.rbac import require_acl

user_bp = Blueprint("user", __name__)


# ---------------- LIST USERS (SUPER ADMIN ONLY) ----------------
@user_bp.route("/all", methods=["GET"])
@jwt_required()
@require_acl("USER_READ")
def all_users():

    users = list_users()

    return success_response(
        data=users,
        message="Users fetched successfully"
    )

# ---------------- GET PROFILE ----------------
@user_bp.route("/profile", methods=["GET"])
@jwt_required()
def get_profile():
    try:
        client_uuid = get_jwt_identity()
        client = Client.query.get(client_uuid)

        if not client:
            return error_response("User not found", 404, "USER_NOT_FOUND")

        return success_response(
            data={
                "uuid": str(client.uuid),
                "name": client.client_name,
                "email": client.client_email,
                "status": client.client_status,
                "created_on": client.created_on.isoformat() if client.created_on else None
            },
            message="Profile fetched successfully"
        )

    except Exception as e:
        print("🔥 PROFILE ERROR:", str(e))
        return error_response("Internal server error", 500, "INTERNAL_ERROR")
    
@user_bp.route("/profile", methods=["PUT"])
@jwt_required()
def update_profile():
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        data = data.get('data')  # or data['data']

        print("📥 Incoming update data:", data)

        if not data:
            return error_response("Request body required", 400, "BAD_REQUEST")

        client = Client.query.filter_by(uuid=user_id).first()

        if not client:
            return error_response("User not found", 404, "USER_NOT_FOUND")

        updated = False  # track DB changes

        # Update name
        if "name" in data and str(data["name"]) != str(client.client_name):
            client.client_name = data["name"]
            updated = True

        # Update email
        if "email" in data and data["email"] != client.client_email:
            # check duplicate email
            existing = Client.query.filter_by(client_email=data["email"]).first()
            if existing and existing.uuid != client.uuid:
                return error_response("Email already exists", 409, "EMAIL_EXISTS")

            client.client_email = data["email"]
            updated = True

        if not updated:
            print("⚠️ No changes detected")
            return success_response(
                data={"message": "No changes made"},
                message="Nothing to update"
            )

        db.session.commit()
        print("✅ DB COMMIT SUCCESS")

        return success_response(
            data={
                "uuid": str(client.uuid),
                "name": client.client_name,
                "email": client.client_email,
                "status": client.client_status,
                "created_on": client.created_on.isoformat() if client.created_on else None
            },
            message="Profile updated successfully"
        )

    except Exception as e:
        db.session.rollback()
        print("🔥 UPDATE PROFILE ERROR:", str(e))
        return error_response("Internal server error", 500, "INTERNAL_ERROR")