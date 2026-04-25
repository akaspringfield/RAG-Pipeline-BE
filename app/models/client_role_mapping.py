'''
Author : Akash Mambally
GitHub: https://github.com/akaspringfield
'''

import uuid
from app.extensions import db

class ClientRoleMapping(db.Model):
    __tablename__ = "client_role_mapping"

    uuid = db.Column(db.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    role_uuid = db.Column(db.UUID(as_uuid=True), nullable=False)
    acl_uuid = db.Column(db.UUID(as_uuid=True), nullable=False)

    status = db.Column(db.String(20), default="active")

    client_auth_code = db.Column(db.String(100))

    access_valid_from = db.Column(db.DateTime)
    access_valid_to = db.Column(db.DateTime)

    created_by = db.Column(db.String(100))
    created_on = db.Column(db.DateTime)

    updated_by = db.Column(db.String(100))
    updated_on = db.Column(db.DateTime)