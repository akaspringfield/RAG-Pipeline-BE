'''
Author : Akash Mambally
GitHub: https://github.com/akaspringfield


Database Bootstrap / Initial Setup Script
Run:
    python -m app.scripts.setup_db
'''

import uuid
from app import create_app
from app.extensions import db

from app.models.user import Client
from app.models.role import ClientACL, ClientRole, ClientRoleMapping, RoleACLMapping

app = create_app()

SYSTEM_USER_UUID = uuid.uuid4()


# ---------------- ROLE ----------------
def get_or_create_role(name, desc):
    role = ClientRole.query.filter_by(role_name=name).first()
    if role:
        return role

    role = ClientRole(
        uuid=uuid.uuid4(),
        role_name=name,
        role_description=desc,
        status="active",
        created_by=SYSTEM_USER_UUID
    )
    db.session.add(role)
    return role


# ---------------- ACL ----------------
def get_or_create_acl(title, desc):
    acl = ClientACL.query.filter_by(acl_title=title).first()
    if acl:
        return acl

    acl = ClientACL(
        uuid=uuid.uuid4(),
        acl_key=title,   # ✅ FIX (important if column exists NOT NULL)
        acl_title=title,
        acl_description=desc,
        status="active",
        created_by=SYSTEM_USER_UUID
    )
    db.session.add(acl)
    return acl


# ---------------- ROLE-ACL MAP ----------------
def map_role_to_acl(role_uuid, acl_uuid):
    exists = RoleACLMapping.query.filter_by(
        role_uuid=role_uuid,
        acl_uuid=acl_uuid
    ).first()

    if exists:
        return

    db.session.add(RoleACLMapping(
        uuid=uuid.uuid4(),
        role_uuid=role_uuid,
        acl_uuid=acl_uuid,
        status="active",
        created_by=SYSTEM_USER_UUID
    ))


# ---------------- USER ----------------
def create_admin_user(role_uuid):
    user = Client.query.filter_by(client_email="admin@system.com").first()
    if user:
        return

    db.session.add(Client(
        uuid=uuid.uuid4(),
        client_name="Super Admin",
        client_email="admin@system.com",
        role_uuid=role_uuid,
        client_status="active"
    ))


# ---------------- MAIN SETUP ----------------
def run_setup():
    print("🚀 Starting DB setup...")

    # Roles
    super_admin = get_or_create_role(
        "SUPER_ADMIN",
        "System administrator with full access"
    )

    user_role = get_or_create_role(
        "USER",
        "Normal application user"
    )

    # ACLs
    chat_send = get_or_create_acl("CHAT_SEND", "Send chat messages")
    profile_update = get_or_create_acl("PROFILE_UPDATE", "Update profile")
    user_read = get_or_create_acl("USER_READ", "Read user data")

    # Role mappings
    for acl in [chat_send, profile_update, user_read]:
        map_role_to_acl(super_admin.uuid, acl.uuid)

    map_role_to_acl(user_role.uuid, chat_send.uuid)

    # Admin user
    create_admin_user(super_admin.uuid)

    # ✅ SINGLE COMMIT (IMPORTANT FIX)
    db.session.commit()

    print("✅ DB setup completed successfully!")


# ---------------- ENTRY POINT ----------------
if __name__ == "__main__":
    with app.app_context():
        run_setup()