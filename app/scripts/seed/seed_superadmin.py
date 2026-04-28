import uuid
import os
from datetime import datetime
from werkzeug.security import generate_password_hash

from app.models.user import Client, ClientPassword
from app.models.role import ClientRole
from app.extensions import db


def seed_superadmin():
    print("👤 Seeding superadmin...")

    now = datetime.utcnow()

    email = os.getenv("SUPERADMIN_EMAIL", "superadmin@hochrise.com")
    password = os.getenv("SUPERADMIN_PASSWORD", "admin123")

    role = ClientRole.query.filter_by(role_name="SUPER_ADMIN").first()

    user = Client.query.filter_by(client_email=email).first()

    if not user:
        user = Client(
            uuid=uuid.uuid4(),
            client_name="Super Admin",
            client_email=email,
            client_status="active",
            created_on=now
        )
        db.session.add(user)
        db.session.flush()

        db.session.add(ClientPassword(
            uuid=uuid.uuid4(),
            client_uuid=user.uuid,
            password_hash=generate_password_hash(password),
            created_on=now
        ))

    # ensure role mapping exists
    from app.models.role import ClientRoleMapping

    mapping = ClientRoleMapping.query.filter_by(
        client_uuid=user.uuid,
        role_uuid=role.uuid
    ).first()

    if not mapping:
        db.session.add(ClientRoleMapping(
            uuid=uuid.uuid4(),
            client_uuid=user.uuid,
            role_uuid=role.uuid,
            status="active",
            access_valid_from=now,
            created_on=now
        ))

    db.session.flush()
    print("✅ Superadmin seeded")