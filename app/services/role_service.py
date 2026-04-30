'''
Author : Akash Mambally
GitHub: https://github.com/akaspringfield
'''

from datetime import datetime
import uuid
from app.extensions import db
from app.models.role import ClientRole,ClientRoleMapping


def get_role_by_name(role_name: str):
    role = ClientRole.query.filter_by(role_name=role_name).first()

    if not role:
        raise Exception(f"ROLE NOT FOUND: {role_name}. Did you run seed?")
    
    return role


def assign_role_to_client(client_uuid, role_uuid):
    print("assign role")

    mapping = ClientRoleMapping(
        uuid=uuid.uuid4(),
        client_uuid=client_uuid,
        role_uuid=role_uuid,
        status="active",
        access_valid_from=datetime.utcnow(),
        created_by=client_uuid
    )

    db.session.add(mapping)
    db.session.flush()
    db.session.commit()
    db.session.add(mapping)
    return mapping