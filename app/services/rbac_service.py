'''
Author : Akash Mambally
'''

from datetime import datetime
from app.extensions import db
from app.models.role import (
    ClientRole,
    ClientACL,
    RoleACLMapping,
    ClientRoleMapping
)

# =========================================================
# ROLES
# =========================================================

def create_role(data):
    role = ClientRole(
        role_name=data["role_name"],
        role_description=data.get("role_description"),
        status="active"
    )

    db.session.add(role)
    db.session.commit()

    return {
        "uuid": str(role.uuid),
        "role_name": role.role_name
    }


def list_roles():
    roles = ClientRole.query.all()

    return [
        {
            "uuid": str(r.uuid),
            "role_name": r.role_name,
            "status": r.status
        }
        for r in roles
    ]


# =========================================================
# ACL
# =========================================================

def create_acl(data):
    acl = ClientACL(
        acl_key=data["acl_key"],  # ⭐ IMPORTANT
        acl_title=data["acl_title"],
        acl_description=data.get("acl_description"),
        status="active"
    )

    db.session.add(acl)
    db.session.commit()

    return {
        "uuid": str(acl.uuid),
        "acl_key": acl.acl_key
    }


def list_acls():
    acls = ClientACL.query.all()

    return [
        {
            "uuid": str(a.uuid),
            "acl_key": a.acl_key,
            "status": a.status
        }
        for a in acls
    ]


# =========================================================
# ROLE → ACL MAPPING  (Role Permissions)
# =========================================================

def assign_acl_to_role(role_uuid, acl_uuids):

    for acl_uuid in acl_uuids:

        # avoid duplicates
        exists = RoleACLMapping.query.filter_by(
            role_uuid=role_uuid,
            acl_uuid=acl_uuid
        ).first()

        if exists:
            continue

        mapping = RoleACLMapping(
            role_uuid=role_uuid,
            acl_uuid=acl_uuid
        )
        db.session.add(mapping)

    db.session.commit()


def get_role_acls(role_uuid):
    mappings = RoleACLMapping.query.filter_by(role_uuid=role_uuid).all()
    return [str(m.acl_uuid) for m in mappings]


# =========================================================
# CLIENT → ROLE ASSIGNMENT
# =========================================================

def assign_role_to_client(client_uuid, role_uuid):

    exists = ClientRoleMapping.query.filter_by(
        client_uuid=client_uuid,
        role_uuid=role_uuid
    ).first()

    if exists:
        return

    mapping = ClientRoleMapping(
        client_uuid=client_uuid,
        role_uuid=role_uuid,
        status="active",
        access_valid_from=datetime.utcnow()
    )

    db.session.add(mapping)
    db.session.commit()


# =========================================================
# 🔐 MAIN PERMISSION ENGINE
# =========================================================

def has_access(client_uuid: str, acl_key: str) -> bool:
    try:
        now = datetime.utcnow()

        # 1️⃣ Get client's role
        role_mapping = ClientRoleMapping.query.filter_by(
            client_uuid=client_uuid,
            status="active"
        ).first()

        if not role_mapping:
            return False

        # date validation
        if role_mapping.access_valid_from and now < role_mapping.access_valid_from:
            return False
        if role_mapping.access_valid_to and now > role_mapping.access_valid_to:
            return False

        # 2️⃣ Find ACL by key
        acl = ClientACL.query.filter_by(
            acl_key=acl_key,
            status="active"
        ).first()

        if not acl:
            return False

        # 3️⃣ Check role permission
        role_acl = RoleACLMapping.query.filter_by(
            role_uuid=role_mapping.role_uuid,
            acl_uuid=acl.uuid
        ).first()

        return role_acl is not None

    except Exception as e:
        print("RBAC ERROR:", str(e))
        return False