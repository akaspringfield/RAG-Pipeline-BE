import uuid
from datetime import datetime

from app.models.role import ClientRoleMapping, RoleACLMapping, ClientACL
from app.utils.response import error_response


def check_permission(client_uuid, required_acl_key):
    """
    Returns True if user has permission else (False, error_response)
    """

    # 1️⃣ Get role mapping
    mapping = ClientRoleMapping.query.filter_by(
        client_uuid=client_uuid,
        status="active"
    ).first()

    if not mapping:
        return False, error_response(
            "No role assigned to user",
            403,
            "ROLE_NOT_ASSIGNED"
        )

    # 2️⃣ Check role validity window
    now = datetime.utcnow()
    if mapping.access_valid_from and mapping.access_valid_from > now:
        return False, error_response("Role not active yet", 403, "ROLE_NOT_ACTIVE")

    if mapping.access_valid_to and mapping.access_valid_to < now:
        return False, error_response("Role expired", 403, "ROLE_EXPIRED")

    role_uuid = mapping.role_uuid

    # 3️⃣ Get ACL UUID by key
    acl = ClientACL.query.filter_by(acl_key=required_acl_key).first()

    if not acl:
        return False, error_response("ACL not found", 500, "ACL_NOT_FOUND")

    # 4️⃣ Check role → ACL mapping
    allowed = RoleACLMapping.query.filter_by(
        role_uuid=role_uuid,
        acl_uuid=acl.uuid
    ).first()

    if not allowed:
        return False, error_response(
            "Permission denied",
            403,
            "PERMISSION_DENIED"
        )

    return True, None