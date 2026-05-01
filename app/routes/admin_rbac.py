'''
Author : Akash Mambally
GitHub: https://github.com/akaspringfield
'''
# =========================================================
# RABC MANAGEMENT
# admin_rbac.py
#  ├── ACL management
#  ├── Role management
#  └── Role ↔ ACL mapping
# =========================================================
from flask import Blueprint, request, jsonify
from datetime import datetime
import uuid

from flask_jwt_extended import jwt_required
from sqlalchemy import and_

from app.middleware.protected import protected
from app.extensions import db
from app.utils.response import success_response, error_response
from app.models.user import (Client)

from app.models.role import (
    ClientACL,
    ClientRole,
    RoleACLMapping,
    ClientRoleMapping
)

from app.audit_logs.decorator import audit
from app.audit_logs.constants import *


admin_rbac_bp = Blueprint("admin_rbac", __name__)


# =========================================================
# CREATE ACL
# =========================================================
@admin_rbac_bp.route("/admin/acls", methods=["POST"])
@protected("CREATE_ACL")
@audit("ACL_CREATED", "ACL", "CREATED")
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


# =========================================================
# LIST ALL ACL
# =========================================================
@admin_rbac_bp.route("/admin/acls", methods=["GET"])
@protected("LIST_ACL")
@audit("ACL_LISTED", "ACL", "LISTED")
def get_acls():
    acls = ClientACL.query.all()

    return success_response(
        data=[
        {
            "uuid": str(a.uuid),
            "acl_key": a.acl_key,
            "title": a.acl_title,
            "status": a.status
        }
        for a in acls
        ],
        message="ACLs fetched successfully"
    )


# =========================================================
# REMOVE ACL
# =========================================================
@admin_rbac_bp.route("/admin/acls/<uuid:acl_id>", methods=["DELETE"])
@protected("DELETE_ACL")
@audit("ACL_DELETED", "ACL", "REMOVE")
def delete_acl(acl_id):
    acl = ClientACL.query.filter_by(uuid=acl_id).first()
    if not acl:
        return error_response("ACL not found",404,"ACL_NOT_FOUND")

    # soft delete
    acl.status = "inactive"
    acl.updated_on = datetime.utcnow()

    db.session.commit()

    return success_response(message="ACL deactivated")


# =========================================================
# LIST SINGLE ACL
# =========================================================
@admin_rbac_bp.route("/admin/acls/<uuid:acl_id>", methods=["GET"])
@protected("ACL_VIEWED")
@audit("ROLE_REMOVED", "ROLE", "REMOVED")
def get_single_acl(acl_id):
    acl = ClientACL.query.filter_by(uuid=acl_id).first()
    if not acl:
        return error_response("ACL not found",404,"ACL_NOT_FOUND")

    return success_response(data={
        "uuid": str(acl.uuid),
        "acl_key": acl.acl_key,
        "acl_title": acl.acl_title,
        "acl_description": acl.acl_description,
        "status": acl.status
    })


# =========================================================
# UPDATE ACL
# =========================================================
@admin_rbac_bp.route("/admin/acls/<uuid:acl_id>", methods=["PUT"])
@protected("ACL_UPDATED")
@audit("UPDATE_ACL", "UPDATE", "UPDATE")
def update_acl(acl_id):
    acl = ClientACL.query.filter_by(uuid=acl_id).first()
    if not acl:
        return error_response("ACL not found",404,"ACL_NOT_FOUND")

    data = request.get_json()

    acl.acl_title = data.get("acl_title", acl.acl_title)
    acl.acl_description = data.get("acl_description", acl.acl_description)
    acl.status = data.get("status", acl.status)
    acl.updated_on = datetime.utcnow()

    db.session.commit()

    return success_response(message="ACL updated")


# =========================================================
# CREATE ROLE 
# =========================================================
@admin_rbac_bp.route("/admin/roles", methods=["POST"])
@protected("ACL_CREATED")
@audit("CREATE_ACL", "ACL", "CREATE")
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


# =========================================================
# LIST ALL ROLES
# =========================================================
@admin_rbac_bp.route("/admin/roles", methods=["GET"])
@protected("LIST_ROLE")
@audit("ROLE_LIST", "ROLE", "LIST")
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


# =========================================================
# VIEW ROLE
# =========================================================
@admin_rbac_bp.route("/admin/roles/<uuid:role_id>", methods=["GET"])
@protected("VIEW_ROLE")
@audit("ROLE_VIEW", "ROLE", "VIEW")
def get_single_role(role_id):
    role = ClientRole.query.filter_by(uuid=role_id).first()
    if not role:
        return error_response("Role not found",404,"ROLE_NOT_FOUND")

    return success_response(data={
        "uuid": str(role.uuid),
        "role_name": role.role_name,
        "role_description": role.role_description,
        "status": role.status
    })


# =========================================================
# UPDATE ROLE
# =========================================================
@admin_rbac_bp.route("/admin/roles/<uuid:role_id>", methods=["PUT"])
@protected("UPDATE_ROLE")
@audit("ROLE_UPDATED", "ROLE", "UPDATED")
def update_role(role_id):
    role = ClientRole.query.filter_by(uuid=role_id).first()
    if not role:
        return error_response("Role not found",404,"ROLE_NOT_FOUND")

    data = request.get_json()

    role.role_name = data.get("role_name", role.role_name)
    role.role_description = data.get("role_description", role.role_description)
    role.status = data.get("status", role.status)
    role.updated_on = datetime.utcnow()

    db.session.commit()

    return success_response(message="Role updated")


# =========================================================
# REMOVE ROLE
# =========================================================
@admin_rbac_bp.route("/admin/roles/<uuid:role_id>", methods=["DELETE"])
@protected("DELETE_ROLE")
@audit("ROLE_REMOVED", "ROLE", "REMOVED")
def delete_role(role_id):
    role = ClientRole.query.filter_by(uuid=role_id).first()
    if not role:
        return error_response("Role not found",404,"ROLE_NOT_FOUND")

    role.status = "inactive"
    role.updated_on = datetime.utcnow()

    db.session.commit()

    return success_response(message="Role deactivated")


# =========================================================
# DASHBOARD SUMMARY
# =========================================================
@admin_rbac_bp.route("/summary", methods=["GET"])
@protected("ADMIN_DASHBOARD1")
@audit("DASHBOARD_SUMMARY_VIEWED", "SUMMARY", "VIEW")
def rbac_summary():
    return success_response(data={
        "users": Client.query.count(),
        "roles": ClientRole.query.count(),
        "acls": ClientACL.query.count(),
        "role_assignments": ClientRoleMapping.query.count()
    })


# =========================================================
# LIST ALL ROLE → ACL MAPPING
# =========================================================
'''
GET /api/admin/rbac/role-acl
'''
@admin_rbac_bp.route("/role-acl", methods=["GET"])
@jwt_required()
@protected("LIST_ACL_ROLE")
@audit("ROLE_ACL_LISTED", "ACL-ROLE", "LIST")
def list_role_acl():

    roles = ClientRole.query.filter_by(status="active").all()
    response = []

    for role in roles:
        mappings = (
            db.session.query(RoleACLMapping, ClientACL)
            .join(ClientACL, ClientACL.uuid == RoleACLMapping.acl_uuid)
            .filter(
                RoleACLMapping.role_uuid == role.uuid,
                RoleACLMapping.status == "active"
            ).all()
        )

        acl_list = [
            {
                "acl_uuid": str(acl.uuid),
                "acl_key": acl.acl_key,
                "acl_title": acl.acl_title
            }
            for mapping, acl in mappings
        ]

        response.append({
            "role_uuid": str(role.uuid),
            "role_name": role.role_name,
            "acls": acl_list
        })

    return jsonify({"success": True, "data": response}), 200


# =========================================================
# VIEW ACLs OF SINGLE ROLE
# =========================================================
'''
GET /role-acl/<role_uuid>/details
'''
@admin_rbac_bp.route("/role-acl/<uuid:role_uuid>/details", methods=["GET"])
@jwt_required()
@protected("VIEW_ACL_ROLE")
@audit("ROLE_ACL_VIEWED", "ACL-ROLE", "VIEW")
def view_role_acls(role_uuid):

    role = ClientRole.query.get_or_404(role_uuid)

    mappings = (
        db.session.query(RoleACLMapping, ClientACL)
        .join(ClientACL, ClientACL.uuid == RoleACLMapping.acl_uuid)
        .filter(
            RoleACLMapping.role_uuid == role_uuid,
            RoleACLMapping.status == "active"
        ).all()
    )

    acl_list = [
        {
            "acl_uuid": str(acl.uuid),
            "acl_key": acl.acl_key,
            "acl_title": acl.acl_title
        }
        for mapping, acl in mappings
    ]

    return jsonify({
        "success": True,
        "role": role.role_name,
        "acls": acl_list
    }), 200


# =========================================================
# ASSIGN ACLs TO ROLE (ADD NEW)
# =========================================================
'''
POST /role-acl/<role_uuid>/acl
'''
@admin_rbac_bp.route("/role-acl/<uuid:role_uuid>/assign", methods=["POST"])
@jwt_required()
@protected("ASSIGN_ACL_ROLE")
@audit("ROLE_ACL_ASSIGNED", "ACL-ROLE", "ASSIGN")
def assign_acl_to_role(role_uuid):

    ClientRole.query.get_or_404(role_uuid)
    data = request.get_json()
    acl_uuids = data.get("acl_uuids", [])

    created_count = 0

    for acl_uuid in acl_uuids:
        existing = RoleACLMapping.query.filter_by(
            role_uuid=role_uuid,
            acl_uuid=acl_uuid
        ).first()

        if existing:
            # Reactivate if previously inactive
            existing.status = "active"
            existing.updated_by = None
        else:
            mapping = RoleACLMapping(
                role_uuid=role_uuid,
                acl_uuid=acl_uuid,
                created_by=None
            )
            db.session.add(mapping)

        created_count += 1

    db.session.commit()

    return jsonify({
        "success": True,
        "message": f"{created_count} ACL(s) assigned to role"
    }), 200


# =========================================================
# REPLACE ACLs OF ROLE (FULL UPDATE)
# =========================================================
'''
PUT /role-acl/<role_uuid>/update
''' 
@admin_rbac_bp.route("/role-acl/<uuid:role_uuid>/update", methods=["PUT"])
@jwt_required()
@protected("UPDATE_ACL_ROLE")
@audit("ROLE_ACL_UPDATED", "ACL-ROLE", "UPDATE")
def replace_role_acls(role_uuid):

    ClientRole.query.get_or_404(role_uuid)
    data = request.get_json()
    acl_uuids = data.get("acl_uuids", [])

    # Soft delete all existing mappings
    RoleACLMapping.query.filter_by(role_uuid=role_uuid).update(
        {"status": "inactive"}
    )

    # Insert new mappings
    for acl_uuid in acl_uuids:
        mapping = RoleACLMapping(
            role_uuid=role_uuid,
            acl_uuid=acl_uuid,
            created_by=None,
            status="active"
        )
        db.session.add(mapping)

    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Role ACLs replaced successfully"
    }), 200


# =========================================================
# REMOVE SINGLE ACL FROM ROLE
# =========================================================
'''
DELETE /role-acl/<role_uuid>/remove/<acl_uuid>
'''
@admin_rbac_bp.route(
    "/role-acl/<uuid:role_uuid>/remove/<uuid:acl_uuid>",
    methods=["DELETE"]
)
@jwt_required()
@protected("REMOVE_ACL_ROLE")
@audit("ROLE_ACL_REMOVED", "ACL-ROLE", "REMOVE")
def remove_acl_from_role(role_uuid, acl_uuid):

    mapping = RoleACLMapping.query.filter(
        and_(
            RoleACLMapping.role_uuid == role_uuid,
            RoleACLMapping.acl_uuid == acl_uuid,
            RoleACLMapping.status == "active"
        )
    ).first_or_404()

    mapping.status = "inactive"
    db.session.commit()

    return jsonify({
        "success": True,
        "message": "ACL removed from role"
    }), 200