'''
Author : Akash Mambally
GitHub: https://github.com/akaspringfield
'''

from flask import Blueprint, request
from datetime import datetime
import uuid

from app.middleware.protected import protected
from app.utils.response import success_response, error_response
from app.extensions import db

from app.models.role import (
    ClientACL,
    ClientRole,
    RoleACLMapping,
    ClientRoleMapping
)
from app.models.user import Client

admin_rbac_bp = Blueprint("admin_rbac", __name__)

# =========================================================
# ACL MANAGEMENT
# =========================================================

@admin_rbac_bp.route("/acl", methods=["POST"])
@protected("RBAC_MANAGE")
def create_acl():
    data = request.get_json()

    if not data.get("acl_key"):
        return error_response("acl_key required", 400, "VALIDATION_ERROR")

    existing = ClientACL.query.filter_by(acl_key=data["acl_key"]).first()
    if existing:
        return error_response("ACL already exists", 400, "ACL_EXISTS")

    acl = ClientACL(
        uuid=uuid.uuid4(),
        acl_key=data.get("acl_key"),
        acl_title=data.get("acl_title"),
        acl_description=data.get("acl_description"),
        status="active",
        created_on=datetime.utcnow()
    )

    db.session.add(acl)
    db.session.commit()

    return success_response({"acl_uuid": str(acl.uuid)}, "ACL created")


@admin_rbac_bp.route("/acls", methods=["GET"])
@protected("RBAC_MANAGE")
def get_acls():
    acls = ClientACL.query.all()

    data = [
        {
            "uuid": str(a.uuid),
            "acl_key": a.acl_key,
            "title": a.acl_title
        } for a in acls
    ]

    return success_response(data=data)


@admin_rbac_bp.route("/acl/<acl_uuid>", methods=["DELETE"])
@protected("RBAC_MANAGE")
def delete_acl(acl_uuid):
    acl = ClientACL.query.filter_by(uuid=acl_uuid).first()
    if not acl:
        return error_response("ACL not found",404,"ACL_NOT_FOUND")

    RoleACLMapping.query.filter_by(acl_uuid=acl_uuid).delete()
    db.session.delete(acl)
    db.session.commit()

    return success_response(message="ACL deleted")


# =========================================================
# ROLE MANAGEMENT
# =========================================================

@admin_rbac_bp.route("/role", methods=["POST"])
@protected("RBAC_MANAGE")
def create_role():
    data = request.get_json()

    if not data.get("role_name"):
        return error_response("role_name required", 400, "VALIDATION_ERROR")

    role = ClientRole(
        uuid=uuid.uuid4(),
        role_name=data.get("role_name"),
        role_description=data.get("role_description"),
        status="active",
        created_on=datetime.utcnow()
    )

    db.session.add(role)
    db.session.commit()

    return success_response({"role_uuid": str(role.uuid)}, "Role created")


@admin_rbac_bp.route("/roles", methods=["GET"])
@protected("RBAC_MANAGE")
def get_roles():
    roles = ClientRole.query.all()

    data = [
        {
            "uuid": str(r.uuid),
            "role_name": r.role_name,
            "status": r.status
        } for r in roles
    ]

    return success_response(data=data)


@admin_rbac_bp.route("/role/<role_uuid>", methods=["DELETE"])
@protected("RBAC_MANAGE")
def delete_role(role_uuid):
    role = ClientRole.query.filter_by(uuid=role_uuid).first()
    if not role:
        return error_response("Role not found",404,"ROLE_NOT_FOUND")

    RoleACLMapping.query.filter_by(role_uuid=role_uuid).delete()
    ClientRoleMapping.query.filter_by(role_uuid=role_uuid).delete()

    db.session.delete(role)
    db.session.commit()

    return success_response(message="Role deleted")


# =========================================================
# ROLE ↔ ACL MAPPING
# =========================================================

@admin_rbac_bp.route("/role/assign-acl", methods=["POST"])
@protected("RBAC_MANAGE")
def assign_acl_to_role():
    data = request.get_json()

    mapping = RoleACLMapping(
        uuid=uuid.uuid4(),
        role_uuid=data.get("role_uuid"),
        acl_uuid=data.get("acl_uuid"),
        created_on=datetime.utcnow()
    )

    db.session.add(mapping)
    db.session.commit()

    return success_response(message="ACL assigned to role")


@admin_rbac_bp.route("/role/remove-acl", methods=["POST"])
@protected("RBAC_MANAGE")
def remove_acl_from_role():
    data = request.get_json()

    mapping = RoleACLMapping.query.filter_by(
        role_uuid=data.get("role_uuid"),
        acl_uuid=data.get("acl_uuid")
    ).first()

    if not mapping:
        return error_response("Mapping not found",404,"MAPPING_NOT_FOUND")

    db.session.delete(mapping)
    db.session.commit()

    return success_response(message="ACL removed from role")


# =========================================================
# USER ↔ ROLE MAPPING
# =========================================================

@admin_rbac_bp.route("/user/assign-role", methods=["POST"])
@protected("RBAC_MANAGE")
def assign_role_to_user():
    data = request.get_json()

    user = Client.query.filter_by(uuid=data.get("client_uuid")).first()
    if not user:
        return error_response("User not found",404,"USER_NOT_FOUND")

    mapping = ClientRoleMapping(
        uuid=uuid.uuid4(),
        client_uuid=data.get("client_uuid"),
        role_uuid=data.get("role_uuid"),
        status="active",
        created_on=datetime.utcnow()
    )

    db.session.add(mapping)
    db.session.commit()

    return success_response(message="Role assigned to user")


@admin_rbac_bp.route("/user/remove-role", methods=["POST"])
@protected("RBAC_MANAGE")
def remove_role_from_user():
    data = request.get_json()

    mapping = ClientRoleMapping.query.filter_by(
        client_uuid=data.get("client_uuid"),
        role_uuid=data.get("role_uuid")
    ).first()

    if not mapping:
        return error_response("Mapping not found",404,"MAPPING_NOT_FOUND")

    db.session.delete(mapping)
    db.session.commit()

    return success_response(message="Role removed from user")


@admin_rbac_bp.route("/user/<client_uuid>/roles", methods=["GET"])
@protected("RBAC_MANAGE")
def get_user_roles(client_uuid):
    mappings = ClientRoleMapping.query.filter_by(client_uuid=client_uuid).all()
    role_ids = [m.role_uuid for m in mappings]

    roles = ClientRole.query.filter(ClientRole.uuid.in_(role_ids)).all()

    return success_response(data=[
        {"role_uuid": str(r.uuid), "role_name": r.role_name}
        for r in roles
    ])


# =========================================================
# DASHBOARD SUMMARY
# =========================================================

@admin_rbac_bp.route("/summary", methods=["GET"])
@protected("RBAC_MANAGE")
def rbac_summary():
    return success_response(data={
        "users": Client.query.count(),
        "roles": ClientRole.query.count(),
        "acls": ClientACL.query.count(),
        "role_assignments": ClientRoleMapping.query.count()
    })