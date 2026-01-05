from app.extensions import db
from app.models.role import ClientRole
from app.models.client_role_mapping import ClientRoleMapping
from app.models.client_acl import ClientACL


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
            "acl_title": a.acl_title
        }
        for a in acls
    ]


# ---------------- ROLE → ACL MAPPING ----------------

def assign_acl_to_role(role_id, acl_ids):
    for acl_id in acl_ids:
        mapping = ClientRoleMapping(
            role_uuid=role_id,
            acl_uuid=acl_id,
            status="active"
        )
        db.session.add(mapping)

    db.session.commit()


def get_role_acls(role_id):
    mappings = ClientRoleMapping.query.filter_by(role_uuid=role_id).all()

    return [str(m.acl_uuid) for m in mappings]