'''
Author : Akash Mambally
GitHub: https://github.com/akaspringfield
'''

import uuid 
from datetime import datetime, timedelta
from app.extensions import db


class TokenBlacklist(db.Model):
    __tablename__ = "token_blacklist"

    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(255), unique=True, nullable=False)

    user_id = db.Column(db.UUID, nullable=False)
    revoked_at = db.Column(db.DateTime, default=datetime.utcnow)