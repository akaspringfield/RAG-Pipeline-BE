import uuid
import os
from datetime import datetime
from werkzeug.security import generate_password_hash

from app import create_app
from app.extensions import db

from app.models.user import Client, ClientPassword
from app.models.role import (
    ClientACL,
    ClientRole,
    RoleACLMapping,
    ClientRoleMapping
)


# ---------------- CONFIG ----------------
EMAIL = os.getenv("SUPERADMIN_EMAIL", "superadmin@hochrise.com")
PASSWORD = os.getenv("SUPERADMIN_PASSWORD", "admin123")


ACL_LIST = [
    ("logout_all_user", "Logout all sessions"),
    ("logout_single_user", "Logout single user session"),

    ("list_users", "List users"),
    ("update_user", "Update users"),
    ("delete_user", "Delete users"),
    ("manage_user", "Full user management"),

    ("list_acl", "List acl permissions"),
    ("view_acl", "View acl permissions"),
    ("create_acl", "Create acl permissions"),
    ("update_acl", "Update acl permissions"),
    ("delete_acl", "Delete acl permissions"),
    ("manage_acl", "Full acl management"),

    ("list_role", "List roles"),
    ("view_role", "View role"),
    ("create_role", "Create role"),
    ("update_role", "Update role"),
    ("delete_role", "Delete role"),
    ("manage_role", "Full role management"),

    ("list_acl_role", "List all role acl mapping"),
    ("view_acl_role", "View role acl mapping"),
    ("assign_acl_role", "Assign acl to role"),
    ("update_acl_role", "Update acl to role"),
    ("remove_acl_role", "Remove acl to role"),
    ("manage_acl_role", "Full acl to role management"),

    ("list_client_role_mapping", "List all client role mapping"),
    ("view_client_role_mapping", "View client role mapping"),
    ("create_client_role_mapping", "Create client role mapping"),
    ("update_client_role_mapping", "Update client role mapping"),
    ("delete_client_role_mapping", "Delete client role mapping"),

    ("list_chat_history", "List chat history"),
    ("create_new_chat", "Create chat"),
    ("view_chat", "View chat"),
    ("delete_chat", "Delete chat"),

    ("view_profile", "View profile"),
    ("update_profile", "Update profile"),
    ("deactivate_user", "Deactivate user"),
    ("activate_user", "Activate user"),
    ("update_subscription", "Update the subscription"),
]


def seed_data():
    try:
        now = datetime.utcnow()

        # -------------------------------------------------------
        # 1️⃣ CLIENT (SUPER USER)
        # -------------------------------------------------------
        user = Client.query.filter_by(client_email=EMAIL).first()

        if not user:
            user = Client(
                uuid=uuid.uuid4(),
                client_name="Super User",
                client_email=EMAIL,
                client_status="active",
                created_on=now
            )
            db.session.add(user)
            db.session.flush()
            print("✅ client_list created")
        else:
            print("ℹ️ client_list exists")

        # -------------------------------------------------------
        # 2️⃣ BISCUITS (PASSWORD)
        # -------------------------------------------------------
        from app.models.user import ClientPassword

        pwd = ClientPassword.query.filter_by(client_uuid=user.uuid).first()

        if not pwd:
            pwd = ClientPassword(
                uuid=uuid.uuid4(),
                client_uuid=user.uuid,
                password_hash=generate_password_hash(PASSWORD),
                created_on=now
            )
            db.session.add(pwd)
            print("✅ password created")
        else:
            print("ℹ️ password exists")

        # -------------------------------------------------------
        # 3️⃣ ACLs
        # -------------------------------------------------------
        acl_map = {}

        for key, desc in ACL_LIST:
            acl = ClientACL.query.filter_by(acl_key=key).first()

            if not acl:
                acl = ClientACL(
                    uuid=uuid.uuid4(),
                    acl_key=key,
                    acl_title=key,
                    acl_description=desc,
                    status="active",
                    created_on=now
                )
                db.session.add(acl)
                db.session.flush()
                print(f"✅ [SEED][ACL] created: {key}")
            else:
                print(f"ℹ️ [SEED][ACL] exists: {key}")

            acl_map[key] = acl

        db.session.commit()

        # -------------------------------------------------------
        # 4️⃣ ROLE (SUPER_ADMIN)
        # -------------------------------------------------------
        role = ClientRole.query.filter_by(role_name="SUPER_ADMIN").first()

        if not role:
            role = ClientRole(
                uuid=uuid.uuid4(),
                role_name="SUPER_ADMIN",
                role_description="System Super Admin",
                status="active",
                created_on=now
            )
            db.session.add(role)
            db.session.flush()
            print("✅ role created")
        else:
            print("ℹ️ role exists")

        # -------------------------------------------------------
        # 5️⃣ ROLE ↔ ACL MAPPING (FULL ACCESS)
        # -------------------------------------------------------
        
        for acl in acl_map.values():
            mapping = RoleACLMapping.query.filter_by(
                role_uuid=role.uuid,
                acl_uuid=acl.uuid
            ).first()

            if not mapping:
                mapping = RoleACLMapping(
                    uuid=uuid.uuid4(),
                    role_uuid=role.uuid,
                    acl_uuid=acl.uuid,
                    status="active",
                    created_on=now,
                    created_by=user.uuid
                )
                db.session.add(mapping)

        db.session.commit()
        print("✅ role_acl_mapping completed")

        # -------------------------------------------------------
        # 6️⃣ CLIENT ROLE ASSIGNMENT
        # -------------------------------------------------------
        crm = ClientRoleMapping.query.filter_by(
            client_uuid=user.uuid,
            role_uuid=role.uuid
        ).first()

        if not crm:
            crm = ClientRoleMapping(
                uuid=uuid.uuid4(),
                client_uuid=user.uuid,
                role_uuid=role.uuid,
                status="active",
                access_valid_from=now,
                access_valid_to=None,
                created_on=now
            )
            db.session.add(crm)

        db.session.commit()
        print("🚀 SUPER ADMIN FULL SEED COMPLETED")

    except Exception as e:
        import traceback
        print("🔥 SEED ERROR:", repr(e))
        traceback.print_exc()
        raise

# -------------------------------------------------------
# RUN SCRIPT
# -------------------------------------------------------
if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        seed_data()