'''
Author : Akash Mambally
GitHub: https://github.com/akaspringfield
'''

import uuid
from app.extensions import db

class ClientRole(db.Model):
    __tablename__ = "client_roles"
    __table_args__ = {"extend_existing": True}

    uuid = db.Column(db.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    role_name = db.Column(db.String(100), nullable=False)
    role_description = db.Column(db.Text)
    allowed_acl = db.Column(db.JSON)

    status = db.Column(db.String(20), default="active")

    created_on = db.Column(db.DateTime, server_default=db.func.now())
    created_by = db.Column(db.UUID(as_uuid=True))
    updated_on = db.Column(db.DateTime)
    updated_by = db.Column(db.UUID(as_uuid=True))