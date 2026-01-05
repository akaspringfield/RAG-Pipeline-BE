import uuid
from app.extensions import db

class ClientRoleMapping(db.Model):
    __tablename__ = "client_role_mapping"
    __table_args__ = {"extend_existing": True}

    uuid = db.Column(db.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    role_uuid = db.Column(db.UUID(as_uuid=True), db.ForeignKey("client_roles.uuid"))
    acl_uuid = db.Column(db.UUID(as_uuid=True), db.ForeignKey("client_acl.uuid"))

    client_auth_code = db.Column(db.String(100))

    access_valid_from = db.Column(db.DateTime)
    access_valid_to = db.Column(db.DateTime)

    status = db.Column(db.String(20), default="active")

    created_on = db.Column(db.DateTime, server_default=db.func.now())
    created_by = db.Column(db.UUID(as_uuid=True))
    updated_on = db.Column(db.DateTime)
    updated_by = db.Column(db.UUID(as_uuid=True))