'''
Author : Akash Mambally
GitHub: https://github.com/akaspringfield
'''

import uuid
from datetime import datetime, timedelta
from app.extensions import db

from app.models.user import Client
from app.models.password_reset_token import PasswordResetToken
from app.utils.security import hash_token
from app.utils.security import hash_password, verify_token_hash
from app.models.user import ClientPassword
from sqlalchemy.sql import func

class PasswordReset(db.Model):
    __tablename__ = "password_resets"

    uuid = db.Column(db.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    client_uuid = db.Column(db.UUID, nullable=False)

    token_hash = db.Column(db.Text, nullable=False)

    expires_at = db.Column(db.DateTime, nullable=False)

    used = db.Column(db.Boolean, default=False)

    created_at = db.Column(db.DateTime, server_default=func.now())


def create_reset_token(email):
    user = Client.query.filter_by(client_email=email).first()

    if not user:
        return None, "USER_NOT_FOUND"

    raw_token = str(uuid.uuid4())

    token_entry = PasswordResetToken(
        client_uuid=user.uuid,
        token_hash=hash_token(raw_token),
        expires_at=datetime.utcnow() + timedelta(minutes=30),
        used=False
    )

    db.session.add(token_entry)
    db.session.commit()

    return raw_token, None


def reset_password(email, token, new_password):
    user = Client.query.filter_by(client_email=email).first()

    if not user:
        return None, "USER_NOT_FOUND"

    token_row = PasswordResetToken.query.filter_by(
        client_uuid=user.uuid,
        used=False
    ).first()

    if not token_row:
        return None, "INVALID_TOKEN"

    # validate token
    if not verify_token_hash(token, token_row.token_hash):
        return None, "INVALID_TOKEN"

    if token_row.expires_at < datetime.utcnow():
        return None, "TOKEN_EXPIRED"

    # mark token used
    token_row.used = True

    # update password
    pwd = ClientPassword.query.filter_by(client_uuid=user.uuid).first()

    pwd.password = hash_password(new_password)

    db.session.commit()

    return True, None
