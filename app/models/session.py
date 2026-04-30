'''
Author : Akash Mambally
GitHub: https://github.com/akaspringfield
'''

import uuid 
from datetime import datetime, timedelta
from app.extensions import db


class ClientSession(db.Model):
    __tablename__ = "client_sessions"

    uuid = db.Column(db.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    client_uuid = db.Column(db.UUID(as_uuid=True), nullable=False, index=True)

    refresh_token_hash = db.Column(db.Text, nullable=False)

    device_info = db.Column(db.String(255))
    ip_address = db.Column(db.String(50))

    is_revoked = db.Column(db.Boolean, default=False, index=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)