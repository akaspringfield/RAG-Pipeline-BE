import uuid
from app.extensions import db

class ClientACL(db.Model):
    __table_args__ = {"extend_existing": True}
    __tablename__ = "client_acl"
    
    uuid = db.Column(db.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    acl_title = db.Column(db.String(100), nullable=False)
    acl_description = db.Column(db.Text)

    acl_doc = db.Column(db.Text)
    status = db.Column(db.String(20), default="active")

    created_on = db.Column(db.DateTime)
    created_by = db.Column(db.String(100))

    updated_on = db.Column(db.DateTime)
    updated_by = db.Column(db.String(100))