'''
✅ Correct Order (VERY IMPORTANT)
Create app
Init extensions
Import models
(Run migrations externally)
THEN seed data

create_app()
   ↓
init db / jwt
   ↓
import models
   ↓
register routes
   ↓
✅ seed (only if env enabled)


✅ Python Auto-Seed (Superadmin)
This script creates a superadmin user with the email "
▶️ How to run
python app/scripts/seed_superadmin.py

OR

export SEED_DATA=true
python run.py
unset SEED_DATA

if it does not work hear is the SQL to insert the superadmin user directly into the database:

INSERT INTO client_roles (uuid, role_name, role_description, status)
VALUES (gen_random_uuid(), 'SUPER_ADMIN', 'System Super Admin', 'active');

-- insert  manually
INSERT INTO client_list (
    uuid,
    client_name,
    client_email,
    client_status,
)
VALUES (
    gen_random_uuid(),
    'Super User',
    'superadmin@hochrise.com',
    'active',
);

'''
import uuid
import os
from datetime import datetime
from werkzeug.security import generate_password_hash


def seed_superadmin():
    from app.extensions import db
    from app.models.user import Client, ClientPassword
    from app.models.role import ClientRole
    from app.models.acl import ClientACL
    from app.models.role_mapping import ClientRoleMapping

    # ---------------- CONFIG ----------------
    email = os.getenv("SUPERADMIN_EMAIL", "superadmin@hochrise.com")
    password = os.getenv("SUPERADMIN_PASSWORD", "admin123")

    # ---------------- CREATE ROLE ----------------
    role = ClientRole.query.filter_by(role_name="SUPER_ADMIN").first()

    if not role:
        role = ClientRole(
            uuid=uuid.uuid4(),
            role_name="SUPER_ADMIN",
            role_description="System Super Admin",
            status="active",
            created_on=datetime.utcnow()
        )
        db.session.add(role)
        db.session.commit()
        print("✅ SUPER_ADMIN role created")

    # ---------------- CREATE ACLS ----------------
    default_acls = [
        ("CHAT_SEND", "Send chat messages"),
        ("PROFILE_UPDATE", "Update profile"),
        ("USER_READ", "Read user data"),
        ("USER_UPDATE", "Update users"),
        ("ROLE_CREATE", "Create roles"),
        ("ROLE_ASSIGN", "Assign roles"),
        ("ACL_CREATE", "Create ACL"),
    ]

    acl_objects = []

    for title, desc in default_acls:
        acl = ClientACL.query.filter_by(acl_title=title).first()

        if not acl:
            acl = ClientACL(
                uuid=uuid.uuid4(),
                acl_title=title,
                acl_description=desc,
                status="active",
                created_on=datetime.utcnow()
            )
            db.session.add(acl)
            db.session.flush()
            print(f"✅ ACL created: {title}")

        acl_objects.append(acl)

    db.session.commit()

    # ---------------- MAP ALL ACLs TO ROLE ----------------
    for acl in acl_objects:
        mapping = ClientRoleMapping.query.filter_by(
            role_uuid=role.uuid,
            acl_uuid=acl.uuid
        ).first()

        if not mapping:
            mapping = ClientRoleMapping(
                uuid=uuid.uuid4(),
                role_uuid=role.uuid,
                acl_uuid=acl.uuid,
                status="active",
                created_on=datetime.utcnow()
            )
            db.session.add(mapping)

    db.session.commit()
    print("✅ All ACLs mapped to SUPER_ADMIN")

    # ---------------- CREATE USER ----------------
    user = Client.query.filter_by(client_email=email).first()

    if user:
        print("✅ Superadmin already exists")
        return

    user = Client(
        uuid=uuid.uuid4(),
        client_name="Super User",
        client_email=email,
        client_status="active",
    )

    db.session.add(user)
    db.session.flush()

    # Create password entry in ClientPassword table
    pwd = ClientPassword(
        uuid=uuid.uuid4(),
        client_uuid=user.uuid,
        password_hash=generate_password_hash(password)
    )
    
    db.session.add(pwd)
    db.session.commit()

    print("🚀 Superadmin user created successfully!")


if __name__ == "__main__":
    from app import create_app
    app = create_app()
    with app.app_context():
        seed_superadmin()