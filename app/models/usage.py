import uuid
from datetime import datetime, timedelta
from app.extensions import db


class ClientUsage(db.Model):
    __tablename__ = "client_usage_limits"

    uuid = db.Column(db.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    client_uuid = db.Column(db.UUID, nullable=False)

    token_counter = db.Column(db.Integer, default=0)
    token_limit = db.Column(db.Integer, default=1000)

    token_reset_time = db.Column(db.DateTime, default=lambda: datetime.utcnow() + timedelta(days=1))
    last_reset_at = db.Column(db.DateTime, default=datetime.utcnow)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)