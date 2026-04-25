from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.middleware.protected import protected

from app.services.rbac_service import (
    create_role,
    list_roles,
    create_acl,
    list_acls,
    assign_acl_to_role,
    get_role_acls
)

from app.utils.response import success_response, error_response

admin_rbac_bp = Blueprint("admin_rbac", __name__)


# ---------------- ROLE APIs ----------------

@admin_rbac_bp.route("/roles", methods=["POST"])
@protected("USER_READ")
def add_role():
    data = request.get_json()

    role = create_role(data)

    return success_response(role, "Role created")


@admin_rbac_bp.route("/roles", methods=["GET"])
@protected("USER_READ")
def get_roles():
    roles = list_roles()
    return success_response(roles, "Roles fetched")


# ---------------- ACL APIs ----------------

@admin_rbac_bp.route("/acl", methods=["POST"])
@protected("USER_READ")
def add_acl():
    data = request.get_json()

    acl = create_acl(data)

    return success_response(acl, "ACL created")


@admin_rbac_bp.route("/acl", methods=["GET"])
@protected("USER_READ")
def get_acl():
    acls = list_acls()
    return success_response(acls, "ACLs fetched")


# ---------------- ROLE ↔ ACL MAPPING ----------------

@admin_rbac_bp.route("/role/<role_id>/acl", methods=["POST"])
@protected("USER_READ")
def map_acl(role_id):
    data = request.get_json()

    assign_acl_to_role(role_id, data["acl_ids"])

    return success_response(None, "ACLs assigned to role")


@admin_rbac_bp.route("/role/<role_id>/acl", methods=["GET"])
@protected("USER_READ")
def role_acl(role_id):
    data = get_role_acls(role_id)

    return success_response(data, "Role ACLs fetched")