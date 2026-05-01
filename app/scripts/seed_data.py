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

    # ===============================
    # SESSION MANAGEMENT
    # ===============================
    ("LOGOUT_ALL_USERS", "Logout all user sessions"),
    ("LOGOUT_SINGLE_USER", "Logout single user session"),

    # ===============================
    # USER MANAGEMENT
    # ===============================
    ("LIST_USERS", "List users"),
    ("VIEW_USER", "View user details"),
    ("CREATE_USER", "Create users"),
    ("UPDATE_USER", "Update users"),
    ("DELETE_USER", "Delete users"),
    ("ACTIVATE_USER", "Activate user"),
    ("DEACTIVATE_USER", "Deactivate user"),
    ("MANAGE_USER", "Full user management"),

    # ===============================
    # PROFILE
    # ===============================
    ("VIEW_PROFILE", "View profile"),
    ("UPDATE_PROFILE", "Update profile"),
    ("UPDATE_SUBSCRIPTION", "Update user subscription"),

    # ===============================
    # ACL MANAGEMENT
    # ===============================
    ("LIST_ACL", "List ACL permissions"),
    ("VIEW_ACL", "View ACL permission"),
    ("CREATE_ACL", "Create ACL permission"),
    ("UPDATE_ACL", "Update ACL permission"),
    ("DELETE_ACL", "Delete ACL permission"),
    ("MANAGE_ACL", "Full ACL management"),

    # ===============================
    # ROLE MANAGEMENT
    # ===============================
    ("LIST_ROLE", "List roles"),
    ("VIEW_ROLE", "View role"),
    ("CREATE_ROLE", "Create role"),
    ("UPDATE_ROLE", "Update role"),
    ("DELETE_ROLE", "Delete role"),
    ("MANAGE_ROLE", "Full role management"),

    # ===============================
    # ROLE ↔ ACL MAPPING
    # ===============================
    ("LIST_ACL_ROLE", "List role ACL mappings"),
    ("VIEW_ACL_ROLE", "View role ACL mapping"),
    ("ASSIGN_ACL_ROLE", "Assign ACL to role"),
    ("UPDATE_ACL_ROLE", "Update role ACL mapping"),
    ("REMOVE_ACL_ROLE", "Remove ACL from role"),
    ("MANAGE_ACL_ROLE", "Full ACL-to-role management"),

    # ===============================
    # USER ↔ ROLE MAPPING
    # ===============================
    ("LIST_CLIENT_ROLE_MAPPING", "List user role mappings"),
    ("VIEW_CLIENT_ROLE_MAPPING", "View user role mapping"),
    ("CREATE_CLIENT_ROLE_MAPPING", "Assign role to user"),
    ("UPDATE_CLIENT_ROLE_MAPPING", "Update user role mapping"),
    ("DELETE_CLIENT_ROLE_MAPPING", "Remove role from user"),
    ("MANAGE_CLIENT_ROLE_MAPPING", "Full user-role management"),

    # ===============================
    # CHAT MANAGEMENT
    # ===============================
    ("LIST_CHAT_HISTORY", "List chat history"),
    ("VIEW_CHAT", "View chat"),
    ("CREATE_CHAT", "Create chat"),
    ("DELETE_CHAT", "Delete chat"),
    ("MANAGE_CHAT", "Full chat management"),

    # ===============================
    # AUDIT LOGS
    # ===============================
    ("VIEW_AUDIT_LOGS", "View audit logs"),
    ("DELETE_AUDIT_LOGS", "Delete audit logs"),

    # ===============================
    # ADMIN DASHBOARD (NEW)
    # ===============================
    ("VIEW_ADMIN_DASHBOARD", "Access admin dashboard"),
    ("VIEW_DASHBOARD_SUMMARY", "View dashboard summary cards"),
    ("VIEW_USER_GROWTH_ANALYTICS", "View user growth analytics"),
    ("VIEW_ROLE_DISTRIBUTION", "View role distribution analytics"),
    ("VIEW_ACL_USAGE", "View ACL usage analytics"),
    ("VIEW_AUDIT_ACTIVITY", "View audit activity analytics"),
    ("VIEW_DASHBOARD", "View admin dashboard"),
    ("VIEW_AUDIT_LOGS", "View audit logs"),
    ("ADMIN_DASHBOARD1", "View dashboard summary"),
    ("ADMIN_DASHBOARD_AUDIT", "View dashboard audit"),
    ("CLIENT_DASHBOARD1", "View dashboard summary"),
    ("CLIENT_DASHBOARD_AUDIT", "View dashboard audit"),
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
        print(f"USER {user.uuid}")
        return user

    except Exception as e:
        import traceback
        print("🔥 SEED ERROR:", repr(e))
        traceback.print_exc()
        raise


def seed_base_role(admin_user):
    try:
        now = datetime.utcnow()

        print("Seeding base_role and minimal permissions...")

        # 1️⃣ Create permissions
        BASE_LINE_ACL = [
            ("VIEW_PROFILE", "View profile"),
            ("UPDATE_PROFILE", "Update profile"),
            ("LIST_CHAT_HISTORY", "List chat history"),
            ("VIEW_CHAT", "View chat"),
            ("CREATE_CHAT", "Create chat"),
            ("DELETE_CHAT", "Delete chat"),
            ("MANAGE_CHAT", "Full chat management"),
            ("CLIENT_DASHBOARD1", "View dashboard summary"),
            ("CLIENT_DASHBOARD_AUDIT", "View dashboard audit"),
        ]

        # -------------------------------------------------------
        # 2️⃣ ROLE (BASE_LINE_USER)
        # -------------------------------------------------------
        role = ClientRole.query.filter_by(role_name="BASE_LINE_USER").first()

        if not role:
            role = ClientRole(
                uuid=uuid.uuid4(),
                role_name="BASE_LINE_USER",
                role_description="Default role for new users",
                status="active",
                created_on=now
            )
            db.session.add(role)
            db.session.flush()
            db.session.commit()
            print("✅ role created")
        else:
            print("ℹ️ role exists")

        # -------------------------------------------------------
        # 3️⃣ ROLE ↔ ACL MAPPING (FULL ACCESS)
        # -------------------------------------------------------
        
        # superadmin = Client.query.filter_by(client_email="superadmin@hochrise.com").first()

        for key, desc in BASE_LINE_ACL:
            #  Fetch ACL from DB
            acl = ClientACL.query.filter_by(acl_key=key).first()

            if not acl:
                print(f"⚠️ ACL not found in DB: {key}")
                continue

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
                    created_by=admin_user.uuid
                )
                db.session.add(mapping)

        db.session.commit()
        print("✅ role_acl_mapping completed")

        print("🚀 BASELINE ROLE SEED COMPLETED")
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
        admin_user = seed_data()
        print(f"Seeding base_role begins...{admin_user.uuid}")

        seed_base_role(admin_user)
