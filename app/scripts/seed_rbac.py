import uuid
from datetime import datetime
from app.extensions import db
from app.models.role import ClientACL, ClientRole, RoleACLMapping

SYSTEM_USER_UUID = uuid.uuid4()

def seed_rbac():
    print("🌱 Seeding RBAC data...")

    SYSTEM_ACLS = [
        ("ACL_CREATE", "Create ACL"),
        ("ROLE_CREATE", "Create Role"),
        ("ROLE_ASSIGN_ACL", "Assign ACL to Role"),
        ("ROLE_ASSIGN_TO_USER", "Assign Role to User"),
        ("PROFILE_UPDATE", "Update profile"),
        ("CHAT_SEND", "Send chat message"),
    ]

    created_acls = []

    for key, title in SYSTEM_ACLS:
        existing = ClientACL.query.filter_by(acl_key=key).first()

        if existing:
            created_acls.append(existing)
            continue

        acl = ClientACL(
            uuid=uuid.uuid4(),
            acl_key=key,
            acl_title=title,
            status="active",
            created_on=datetime.utcnow(),
            created_by=SYSTEM_USER_UUID
        )
        db.session.add(acl)
        created_acls.append(acl)

    db.session.commit()

    role = ClientRole.query.filter_by(role_name="SUPER_ADMIN").first()

    if not role:
        role = ClientRole(
            uuid=uuid.uuid4(),
            role_name="SUPER_ADMIN",
            role_description="System super administrator",
            status="active",
            created_on=datetime.utcnow(),
            created_by=SYSTEM_USER_UUID
        )
        db.session.add(role)
        db.session.commit()

    for acl in created_acls:
        exists = RoleACLMapping.query.filter_by(
            role_uuid=role.uuid,
            acl_uuid=acl.uuid
        ).first()

        if not exists:
            mapping = RoleACLMapping(
                uuid=uuid.uuid4(),
                role_uuid=role.uuid,
                acl_uuid=acl.uuid,
                created_on=datetime.utcnow(),
                created_by=SYSTEM_USER_UUID
            )
            db.session.add(mapping)

    db.session.commit()
    print("🎉 RBAC seeding completed successfully!")