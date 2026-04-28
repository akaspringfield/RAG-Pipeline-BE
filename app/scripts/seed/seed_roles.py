import uuid
from datetime import datetime
from app.models.role import ClientRole
from app.extensions import db


def seed_roles():
    print("👑 Seeding roles...")

    now = datetime.utcnow()

    roles = [
        ("SUPER_ADMIN", "System Super Admin"),
        ("USER", "Normal user"),
    ]

    for name, desc in roles:
        role = ClientRole.query.filter_by(role_name=name).first()

        if role:
            continue

        db.session.add(ClientRole(
            uuid=uuid.uuid4(),
            role_name=name,
            role_description=desc,
            status="active",
            created_on=now
        ))

    db.session.flush()
    print("✅ Roles seeded")