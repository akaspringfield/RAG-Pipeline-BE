'''
Author : Akash Mambally
GitHub: https://github.com/akaspringfield
'''
# =========================================================
# ADMIN MANAGEMENT
# admin_rbac.py
#  ├── User management
#  ├── User session management
#  ├── User ↔ Role mapping
#  └── Dashboard management
# =========================================================

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from datetime import datetime
import uuid

from app.extensions import db
from app.models.user import Client
from app.models.role import ClientRole, ClientRoleMapping

from app.utils.response import success_response, error_response
from app.middleware.rbac import require_acl

from app.services.session_service import (
    revoke_all_sessions,
    revoke_session_by_uuid
)

from app.services.admin_service import (
    list_all_users,
    list_all_acls,
    toggle_user_status
)
from app.utils.decorators import protected
from app.audit_logs.decorator import audit
from app.audit_logs.constants import *
from app.models.role import (
    ClientACL,
    ClientRole,
    RoleACLMapping,
    ClientRoleMapping
)
admin_bp = Blueprint("admin", __name__)


# =========================================================
# LIST ALL USERS
# =========================================================
''' 
GET /admin/users
'''
@admin_bp.route("/users", methods=["GET"])
@jwt_required()
@protected("LIST_USERS")
@audit("USER_LIST_ALL", "USER", "UPDATE")
def list_users():
    users = Client.query.all()

    data = []
    for user in users:
        data.append({
            "uuid": str(user.uuid),
            "name": user.client_name,
            "email": user.client_email,
            "status": user.client_status,
            "created_on": user.created_on.isoformat() if user.created_on else None
        })

    return success_response(data=data, message="Users fetched successfully")


# =========================================================
# GET SINGLE USER
# =========================================================
@admin_bp.route("/users/<uuid:user_id>", methods=["GET"])
@jwt_required()
@protected("VIEW_USER")
@audit("USER_VIEW", "USER", "VIEW")
def get_user(user_id):
    user = Client.query.get_or_404(user_id)

    return success_response(data={
        "uuid": str(user.uuid),
        "name": user.client_name,
        "email": user.client_email,
        "status": user.client_status
    })


# =========================================================
# UPDATE USER DATA
# =========================================================
'''
UPDATE USER
PUT /admin/users/<id>
'''
@admin_bp.route("/users/<uuid:user_id>", methods=["PUT"])
@jwt_required()
@protected("UPDATE_USER")
@audit("USER_UPDATED", "USER", "UPDATE")
def update_user(user_id):
    user = Client.query.get_or_404(user_id)
    data = request.json

    user.client_name = data.get("name", user.client_name)
    user.client_email = data.get("status", user.client_email)
    user.updated_on = datetime.utcnow()

    db.session.commit()

    return success_response(message="User updated")


# =========================================================
# DEACTIVATE USER
# =========================================================
'''
DELETE /admin/users/<id>
Body:
None
'''
@admin_bp.route("/users/<uuid:user_id>", methods=["DELETE"])
@jwt_required()
@protected("DEACTIVATE_USER")
@audit("USER_DEACTIVATED", "USER", "DEACTIVATE")
def deactivate_user(user_id):
    user = Client.query.get_or_404(user_id)
    user.client_status = "inactive"
    user.updated_on = datetime.utcnow()
    db.session.commit()

    return success_response(message="User deactivated")


# =========================================================
# ACTIVATE USER
# =========================================================
'''
PUT /admin/users/<id>/activate
Body:
None
'''
@admin_bp.route("/admin/users/<uuid:user_id>/activate", methods=["PUT"])
@audit("USER_ACTIVATED", "USER", "ACTIVATED")
@protected("ACTIVATE_USER")
@jwt_required()
def activate_user(user_id):
    try:
        user = Client.query.get_or_404(user_id)

        if user.is_active:
            return jsonify({
                "success": True,
                "message": "User already active"
            }), 200

        user.client_status = "active"
        db.session.commit()

        return jsonify({
            "success": True,
            "message": "User activated"
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "error": "Internal server error"
        }), 500


# =========================================================
# ADMIN: Logout user from ALL devices
# =========================================================
'''
POST /admin/users/<uuid>/logout-all
'''
@admin_bp.route("/admin/users/<uuid:user_id>/logout-all", methods=["POST"])
@audit("ADMIN_LOGOUT_ALL_SESSIONS", "USER", "SUCCESS")
@protected("LOGOUT_ALL_USERS")
@jwt_required()
def admin_logout_all_sessions(user_id):

    revoke_all_sessions(user_id)

    return success_response(message="All user sessions revoked")


# =========================================================
# ADMIN: Logout SINGLE session of user
# =========================================================
'''
POST /admin/users/<uuid>/sessions/<session_uuid>/revoke
'''
@admin_bp.route(
    "/admin/users/<uuid:user_id>/sessions/<uuid:session_id>/revoke",
    methods=["POST"]
)
@audit("ADMIN_LOGOUT_SINGLE_SESSION", "USER", "SUCCESS")
@protected("LOGOUT_SINGLE_USER")
@jwt_required()
def admin_logout_single_session(user_id, session_id):

    result, error = revoke_session_by_uuid(user_id, session_id)

    if error:
        return error_response(error, 404, "SESSION_NOT_FOUND")

    return success_response(
        data=result,
        message="User session revoked successfully"
    )


# =========================================================
# LIST ALL USER ↔ ROLE MAPPINGS
# =========================================================
'''
GET /admin/user-roles
'''
@admin_bp.route("/user-roles", methods=["GET"])
@protected("LIST_CLIENT_ROLE_MAPPING")
@audit("USER_ROLE_LISTED", "USER-ROLE", "LIST")
def list_user_roles():
    mappings = ClientRoleMapping.query.all()

    result = []
    for m in mappings:
        role = ClientRole.query.get(m.role_uuid)
        user = Client.query.get(m.client_uuid)

        result.append({
            "mapping_uuid": str(m.uuid),
            "user_uuid": str(m.client_uuid),
            "user_email": user.client_email if user else None,
            "role_uuid": str(m.role_uuid),
            "role_name": role.role_name if role else None,
            "status": m.status,
            "valid_from": m.access_valid_from,
            "valid_to": m.access_valid_to
        })

    return success_response(data=result)


# =========================================================
# VIEW USER ↔ ROLES
# =========================================================
'''
GET /admin/users/<id>/roles
'''
@admin_bp.route("/users/<uuid:user_id>/roles", methods=["GET"])
@protected("VIEW_CLIENT_ROLE_MAPPING")
@audit("USER_ROLE_VIEWED", "USER-ROLE", "VIEW")
def get_user_roles(user_id):

    mappings = ClientRoleMapping.query.filter_by(
        client_uuid=user_id,
        status="active"
    ).all()

    roles = []
    for m in mappings:
        role = ClientRole.query.get(m.role_uuid)
        if role:
            roles.append({
                "role_uuid": str(role.uuid),
                "role_name": role.role_name,
                "valid_from": m.access_valid_from,
                "valid_to": m.access_valid_to
            })

    return success_response(data=roles)


# =========================================================
# ASSIGN USER ↔ ROLES
# =========================================================
'''
POST /admin/users/<id>/roles
'''
@admin_bp.route("/users/<uuid:user_id>/roles", methods=["POST"])
@protected("CREATE_CLIENT_ROLE_MAPPING")
@audit("USER_ROLE_ASSIGNED", "USER-ROLE", "ASSIGN")
def assign_role_to_user(user_id):

    data = request.get_json()
    role_uuid = data.get("role_uuid")

    if not role_uuid:
        return error_response("role_uuid required", 400, "VALIDATION_ERROR")

    # Check user + role exist
    user = Client.query.get(user_id)
    role = ClientRole.query.get(role_uuid)

    if not user or not role:
        return error_response("User or Role not found", 404, "NOT_FOUND")

    # Prevent duplicate mapping
    existing = ClientRoleMapping.query.filter_by(
        client_uuid=user_id,
        role_uuid=role_uuid
    ).first()

    if existing:
        existing.status = "active"
        existing.access_valid_from = datetime.utcnow()
        existing.access_valid_to = data.get("valid_to")
    else:
        mapping = ClientRoleMapping(
            uuid=uuid.uuid4(),
            client_uuid=user_id,
            role_uuid=role_uuid,
            status="active",
            access_valid_from=datetime.utcnow(),
            access_valid_to=data.get("valid_to"),
            created_on=datetime.utcnow()
        )
        db.session.add(mapping)

    db.session.commit()

    return success_response(message="Role assigned")


# =========================================================
# UPDATE  USER ↔ ROLES VALIDITY
# =========================================================
'''
PUT /admin/users/<id>/roles/<role_id>
'''
@admin_bp.route("/users/<uuid:user_id>/roles/<uuid:role_id>", methods=["PUT"])
@protected("UPDATE_CLIENT_ROLE_MAPPING")
@audit("USER_ROLE_UPDATED", "USER-ROLE", "UPDATE")
def update_user_role(user_id, role_id):

    data = request.get_json()

    mapping = ClientRoleMapping.query.filter_by(
        client_uuid=user_id,
        role_uuid=role_id
    ).first_or_404()

    if not mapping:
        return error_response("Mapping not found", 404, "MAPPING_NOT_FOUND")
    
    data = request.json    
    mapping.access_valid_from = data.get("valid_from")
    mapping.access_valid_to = data.get("valid_to")
    mapping.updated_on = datetime.utcnow()

    db.session.commit()
    return success_response(message="Role validity updated")


# =========================================================
# REMOVE USER ↔ ROLES FROM USER (SOFT DELETE)
# =========================================================
'''
DELETE /admin/users/<id>/roles/<role_id>
'''
@admin_bp.route("/users/<uuid:user_id>/roles/<uuid:role_id>", methods=["DELETE"])
@protected("DELETE_CLIENT_ROLE_MAPPING")
@audit("USER_ROLE_DELETE", "USER-ROLE", "REMOVE")
def remove_role_from_user(user_id, role_id):

    mapping = ClientRoleMapping.query.filter_by(
        client_uuid=user_id,
        role_uuid=role_id,
        status="active"
    ).first_or_404()

    if not mapping:
        return error_response("Mapping not found", 404, "MAPPING_NOT_FOUND")

    mapping.status = "inactive"
    mapping.updated_on = datetime.utcnow()

    db.session.commit()

    return success_response(message="Role removed")
