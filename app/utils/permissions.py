'''
permissions.py
│
├── get_role_acls()   → fetch data
├── require_acl()     → enforce access (YOU JUST ADDED THIS)
'''


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
        ROLE_CACHE[role_uuid] = set()
        return set()   # ✅ explicit empty set

    acls = ClientACL.query.filter(
        ClientACL.uuid.in_(acl_ids),
        ClientACL.status == "active"
    ).all()

    acl_titles = {a.acl_title for a in acls}

    ROLE_CACHE[role_uuid] = acl_titles
    return acl_titles
 

from flask import jsonify
from flask_jwt_extended import get_jwt_identity


def require_acl(acl_key):
    """
    Central permission gate
    Blocks user if:
    - no role
    - no ACLs
    - ACL not present
    """

    def wrapper(fn):
        from functools import wraps

        @wraps(fn)
        def decorated(*args, **kwargs):

            user_id = get_jwt_identity()

            user = Client.query.filter_by(uuid=user_id).first()

            if not user:
                return jsonify({"error": "User not found"}), 404

            if not user.role_uuid:
                return jsonify({"error": "No role assigned"}), 403

            # 🔥 fetch ACLs using your function
            acl_set = get_role_acls(user.role_uuid)

            # 🚨 BLOCK IF EMPTY (your requirement)
            if not acl_set:
                return jsonify({
                    "error": "No permissions assigned. Access denied."
                }), 403

            # 🚨 CHECK SPECIFIC ACL
            if acl_key not in acl_set:
                return jsonify({
                    "error": f"Permission denied: {acl_key}"
                }), 403

            return fn(*args, **kwargs)

        return decorated

    return wrapper