import uuid
from datetime import datetime
from app.models.role import ClientRole, ClientACL, RoleACLMapping
from app.extensions import db


def seed_role_acl():
    print("🔗 Seeding role ACL mappings...")

    now = datetime.utcnow()

    super_admin = ClientRole.query.filter_by(role_name="SUPER_ADMIN").first()
    acls = ClientACL.query.all()

    for acl in acls:
        exists = RoleACLMapping.query.filter_by(
            role_uuid=super_admin.uuid,
            acl_uuid=acl.uuid
        ).first()

        if exists:
            continue

        db.session.add(RoleACLMapping(
            uuid=uuid.uuid4(),
            role_uuid=super_admin.uuid,
            acl_uuid=acl.uuid,
            status="active",
            created_on=now
        ))

    db.session.flush()
    print("✅ Role-ACL mappings seeded")