'''
Author : Akash Mambally
GitHub: https://github.com/akaspringfield
'''

import uuid
from datetime import datetime
from app.extensions import db


class PasswordResetToken(db.Model):
    __tablename__ = "client_password_reset_tokens"

    uuid = db.Column(db.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    client_uuid = db.Column(db.UUID(as_uuid=True), nullable=False)

    token_hash = db.Column(db.Text, nullable=False)

    expires_at = db.Column(db.DateTime, nullable=False)

    used = db.Column(db.Boolean, default=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)