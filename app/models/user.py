import uuid
from app.extensions import db


class Client(db.Model):
    __tablename__ = "client_list"
    __table_args__ = {"extend_existing": True}

    uuid = db.Column(db.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    client_name = db.Column(db.String(100))
    client_email = db.Column(db.String(120), unique=True)

    role_uuid = db.Column(db.UUID(as_uuid=True), db.ForeignKey("client_roles.uuid"))

    client_status = db.Column(db.String(20), default="active")