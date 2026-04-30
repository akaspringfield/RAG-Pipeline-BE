import uuid
from datetime import datetime
from app.extensions import db

class AuditLog(db.Model):
    __tablename__ = "audit_logs"

    uuid = db.Column(db.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    user_uuid = db.Column(db.UUID(as_uuid=True))
    event_type = db.Column(db.String(100))
    entity_type = db.Column(db.String(100))   # USER / ROLE / AUTH / CHAT
    entity_uuid = db.Column(db.UUID(as_uuid=True))

    action = db.Column(db.String(50))         # CREATE / UPDATE / DELETE / LOGIN
    description = db.Column(db.Text)

    ip_address = db.Column(db.String(100))
    user_agent = db.Column(db.Text)

    created_on = db.Column(db.DateTime, default=datetime.utcnow)

