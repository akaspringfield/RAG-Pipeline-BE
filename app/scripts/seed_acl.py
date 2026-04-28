"""
Run from project root:
python app/scripts/seed_acl.py
"""

import uuid
from app.extensions import db
from app.models.role import ClientACL
from app import create_app

SYSTEM_USER_UUID = uuid.uuid4()

ACL_LIST = [
    ("auth.logout_all", "Logout all sessions"),
    ("user.read", "Read users"),
    ("user.update", "Update users"),
    ("user.delete", "Delete users"),
    ("user.manage", "Full user management"),
    ("role.create", "Create roles"),
    ("role.read", "Read roles"),
    ("role.update", "Update roles"),
    ("role.delete", "Delete roles"),
    ("role.manage", "Full role management"),
    ("permission.read", "Read permissions"),
    ("permission.assign", "Assign permissions to role"),
    ("chat.create", "Create chat"),
    ("chat.read", "Read chat"),
    ("chat.delete", "Delete chat")
]

def seed_acls():
    print("🌱 Seeding Client ACLs...")

    for key, title in ACL_LIST:
        exists = ClientACL.query.filter_by(acl_key=key).first()

        if not exists:
            acl = ClientACL(
                acl_key=key,
                acl_title=title,
                acl_description=title,
                created_by=SYSTEM_USER_UUID
            )
            db.session.add(acl)
            print(f"✔ Added ACL: {key}")

    db.session.commit()
    print("✅ ACL seeding completed!")

app = create_app()
with app.app_context():
    seed_acls()