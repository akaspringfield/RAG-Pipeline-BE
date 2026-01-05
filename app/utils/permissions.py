from datetime import datetime

from app.extensions import db
from app.models.client_role_mapping import ClientRoleMapping
from app.models.client_acl import ClientACL
from app.models.user import Client   # ✅ your actual model file
from app.models.role import ClientRole

# ---------------- ROLE ACL CACHE (future Redis upgrade) ----------------
ROLE_CACHE = {}


# ---------------- FETCH ROLE ACLS ----------------
def get_role_acls(role_uuid, use_cache=True):
    """
    Get all active ACLs for a role with validity check
    """

    if use_cache and role_uuid in ROLE_CACHE:
        return ROLE_CACHE[role_uuid]

    mappings = ClientRoleMapping.query.filter_by(
        role_uuid=role_uuid,
        status="active"
    ).all()

    now = datetime.utcnow()
    acl_ids = []

    for m in mappings:
        # validity window check
        if m.access_valid_from and now < m.access_valid_from:
            continue
        if m.access_valid_to and now > m.access_valid_to:
            continue

        acl_ids.append(m.acl_uuid)

    if not acl_ids:
        return set()

    acls = ClientACL.query.filter(
        ClientACL.uuid.in_(acl_ids),
        ClientACL.status == "active"
    ).all()

    acl_titles = {a.acl_title for a in acls}

    ROLE_CACHE[role_uuid] = acl_titles
    return acl_titles


# ---------------- CORE PERMISSION CHECK ----------------
def has_access(role_uuid, acl_code):
    """
    Check if role has access to a specific ACL
    """

    # SUPER ADMIN bypass
    if role_uuid and str(role_uuid).upper() == "SUPER_ADMIN":
        return True

    allowed_acls = get_role_acls(role_uuid)

    return acl_code in allowed_acls