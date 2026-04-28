import uuid
from datetime import datetime
from app.models.role import ClientACL
from app.extensions import db

from app.scripts.seed.data.acl_list import ACL_LIST


def seed_acls():
    print("🔐 Seeding ACLs...")

    now = datetime.utcnow()

    for key, desc in ACL_LIST:
        acl = ClientACL.query.filter_by(acl_key=key).first()

        if acl:
            continue

        db.session.add(ClientACL(
            uuid=uuid.uuid4(),
            acl_key=key,
            acl_title=key,
            acl_description=desc,
            status="active",
            created_on=now
        ))

    db.session.flush()
    print("✅ ACLs seeded")