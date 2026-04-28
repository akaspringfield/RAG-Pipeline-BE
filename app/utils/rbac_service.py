'''
Author : Akash Mambally
GitHub: https://github.com/akaspringfield
'''
from datetime import datetime
from flask import g, has_request_context
from app.models.role import ClientACL, ClientRoleMapping, RoleACLMapping
from app.utils.response import error_response
import os
import redis
import json

# ---------------- REDIS SETUP ----------------
redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    db=0,
    decode_responses=True
)

# ---------------- TTL ----------------
PERMISSION_CACHE_TTL = int(os.getenv("PERMISSION_CACHE_TTL", 60))


# -------------------------------------------------------
# CLEAR CACHE (Redis only)
# -------------------------------------------------------
def clear_permission_cache(user_uuid):
    user_uuid = str(user_uuid)
    cache_key = f"user_permissions:{user_uuid}"
    redis_client.delete(cache_key)


# -------------------------------------------------------
# DB FETCH (source of truth)
# -------------------------------------------------------
def _fetch_permissions_from_db(user_uuid):
    now = datetime.utcnow()

    role_mappings = ClientRoleMapping.query.filter(
        ClientRoleMapping.client_uuid == user_uuid,
        ClientRoleMapping.status == "active"
    ).all()

    valid_role_ids = []
    for mapping in role_mappings:
        if mapping.access_valid_from and mapping.access_valid_from > now:
            continue
        if mapping.access_valid_to and mapping.access_valid_to < now:
            continue
        valid_role_ids.append(mapping.role_uuid)

    if not valid_role_ids:
        return []

    role_acl_mappings = RoleACLMapping.query.filter(
        RoleACLMapping.role_uuid.in_(valid_role_ids),
        RoleACLMapping.status == "active"
    ).all()

    acl_ids = [m.acl_uuid for m in role_acl_mappings]

    if not acl_ids:
        return []

    acls = ClientACL.query.filter(
        ClientACL.uuid.in_(acl_ids),
        ClientACL.status == "active"
    ).all()

    return [acl.acl_key for acl in acls]


# -------------------------------------------------------
# GET PERMISSIONS (g + Redis + DB fallback)
# -------------------------------------------------------
def get_user_permissions(user_uuid):
    user_uuid = str(user_uuid)
    cache_key = f"user_permissions:{user_uuid}"

    # ---------------- 1️⃣ REQUEST CACHE (fastest) ----------------
    if has_request_context():
        if hasattr(g, "permission_cache"):
            if user_uuid in g.permission_cache:
                print("⚡ FROM REQUEST CACHE")
                return g.permission_cache[user_uuid]
        else:
            g.permission_cache = {}

    # ---------------- 2️⃣ REDIS CACHE ----------------
    cached = redis_client.get(cache_key)
    if cached:
        print("⚡ FROM REDIS CACHE")
        permissions = json.loads(cached)

        if has_request_context():
            g.permission_cache[user_uuid] = permissions

        return permissions

    # ---------------- 3️⃣ DATABASE ----------------
    print("🐢 FROM DATABASE")
    permissions = _fetch_permissions_from_db(user_uuid)

    # ---------------- STORE IN REDIS ----------------
    redis_client.setex(
        cache_key,
        PERMISSION_CACHE_TTL,
        json.dumps(permissions)
    )

    # ---------------- STORE IN REQUEST CACHE ----------------
    if has_request_context():
        g.permission_cache[user_uuid] = permissions

    return permissions


# -------------------------------------------------------
# PERMISSION CHECK HELPER
# -------------------------------------------------------
def user_has_permission(user_uuid, required_permission):
    permissions = get_user_permissions(user_uuid)

    if not permissions:
        return False

    return required_permission in permissions