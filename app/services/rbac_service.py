'''
Author : Akash Mambally
GitHub: https://github.com/akaspringfield
'''

from datetime import datetime
from app.extensions import db

from app.models.role import ClientRole
from app.models.role_mapping import ClientRoleMapping
from app.models.acl import ClientACL


# ---------------- ROLES ----------------

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


# ---------------- ACL ----------------

def create_acl(data):
    acl = ClientACL(
        acl_title=data["acl_title"],
        acl_description=data.get("acl_description"),
        status="active"
    )

    db.session.add(acl)
    db.session.commit()

    return {
        "uuid": str(acl.uuid),
        "acl_title": acl.acl_title
    }


def list_acls():
    acls = ClientACL.query.all()

    return [
        {
            "uuid": str(a.uuid),
            "acl_title": a.acl_title,
            "status": a.status
        }
        for a in acls
    ]


# ---------------- ROLE → ACL MAPPING ----------------

def assign_acl_to_role(role_id, acl_ids):
    for acl_id in acl_ids:

        # avoid duplicate mapping
        existing = ClientRoleMapping.query.filter_by(
            role_uuid=role_id,
            acl_uuid=acl_id
        ).first()

        if existing:
            continue

        mapping = ClientRoleMapping(
            role_uuid=role_id,
            acl_uuid=acl_id,
            status="active",
            created_on=datetime.utcnow()
        )

        db.session.add(mapping)

    db.session.commit()


def get_role_acls(role_id):
    mappings = ClientRoleMapping.query.filter_by(
        role_uuid=role_id,
        status="active"
    ).all()

    return [str(m.acl_uuid) for m in mappings]


# ---------------- ACCESS CHECK ----------------

def has_access(role_uuid, acl_code):
    """
    Core permission check with SUPER_ADMIN bypass
    """

    # 🔹 GET ROLE
    role = ClientRole.query.filter_by(uuid=role_uuid).first()

    if not role:
        return False

    # 🔹 SUPER ADMIN BYPASS
    if role.role_name == "SUPER_ADMIN":
        return True

    # 🔹 GET ACTIVE MAPPINGS
    mappings = ClientRoleMapping.query.filter_by(
        role_uuid=role_uuid,
        status="active"
    ).all()

    now = datetime.utcnow()
    valid_acl_ids = []

    for m in mappings:
        if m.access_valid_from and now < m.access_valid_from:
            continue

        if m.access_valid_to and now > m.access_valid_to:
            continue

        valid_acl_ids.append(m.acl_uuid)

    if not valid_acl_ids:
        return False

    # 🔹 FETCH ACL TITLES
    acls = ClientACL.query.filter(
        ClientACL.uuid.in_(valid_acl_ids)
    ).all()

    allowed_acls = {acl.acl_title for acl in acls}

    return acl_code in allowed_acls