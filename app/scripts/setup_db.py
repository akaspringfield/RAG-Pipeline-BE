'''
Author : Akash Mambally
GitHub: https://github.com/akaspringfield
'''

from app import create_app
from app.extensions import db

from app.models.user import Client
from app.models.role import ClientRole
from app.models.acl import ClientACL

import uuid

app = create_app()


def get_or_create_role(name, desc):
    role = ClientRole.query.filter_by(role_name=name).first()
    if role:
        return role

    role = ClientRole(
        uuid=uuid.uuid4(),
        role_name=name,
        role_description=desc,
        status="active"
    )
    db.session.add(role)
    db.session.commit()
    return role


def get_or_create_acl(title, desc):
    acl = ClientACL.query.filter_by(acl_title=title).first()
    if acl:
        return acl

    acl = ClientACL(
        uuid=uuid.uuid4(),
        acl_title=title,
        acl_description=desc,
        status="active"
    )
    db.session.add(acl)
    db.session.commit()
    return acl


def map_role_to_acl(role_uuid, acl_uuid):
    exists = ClientRoleMapping.query.filter_by(
        role_uuid=role_uuid,
        acl_uuid=acl_uuid
    ).first()

    if exists:
        return

    mapping = ClientRoleMapping(
        uuid=uuid.uuid4(),
        role_uuid=role_uuid,
        acl_uuid=acl_uuid,
        status="active"
    )
    db.session.add(mapping)
    db.session.commit()


def create_admin_user(role_uuid):
    user = Client.query.filter_by(client_email="admin@system.com").first()
    if user:
        return

    user = Client(
        uuid=uuid.uuid4(),
        client_name="Super Admin",
        client_email="admin@system.com",
        role_uuid=role_uuid,
        client_status="active"
    )

    db.session.add(user)
    db.session.commit()


def run_setup():
    print("🚀 Starting DB setup...")

    # ---------------- ROLES ----------------
    super_admin = get_or_create_role(
        "SUPER_ADMIN",
        "System administrator with full access"
    )

    user_role = get_or_create_role(
        "USER",
        "Normal application user"
    )

    # ---------------- ACLS ----------------
    chat_send = get_or_create_acl("CHAT_SEND", "Send chat messages")
    profile_update = get_or_create_acl("PROFILE_UPDATE", "Update profile")
    user_read = get_or_create_acl("USER_READ", "Read user data")

    # ---------------- ROLE MAPPINGS ----------------

    # SUPER ADMIN gets all access
    for acl in [chat_send, profile_update, user_read]:
        map_role_to_acl(super_admin.uuid, acl.uuid)

    # USER gets limited access
    map_role_to_acl(user_role.uuid, chat_send.uuid)

    # ---------------- DEFAULT ADMIN USER ----------------
    create_admin_user(super_admin.uuid)

    db.session.commit()

    print("✅ DB setup completed successfully!")


if __name__ == "__main__":
    with app.app_context():
        run_setup()