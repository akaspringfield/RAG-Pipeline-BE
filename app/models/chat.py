'''
Author : Akash Mambally
GitHub: https://github.com/akaspringfield
'''

import uuid
from datetime import datetime
from app.extensions import db
from app.models.user import Client
from app.utils.permissions import has_access

class ChatHistory(db.Model):
    __tablename__ = "client_chat_history"

    uuid = db.Column(db.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    client_uuid = db.Column(db.UUID, nullable=False)

    chat_title = db.Column(db.String(255))
    chat_description = db.Column(db.Text)

    status = db.Column(db.String(20), default="active")

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ChatMessage(db.Model):
    __tablename__ = "client_chat_message"

    uuid = db.Column(db.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    chat_history_uuid = db.Column(db.UUID, nullable=False)

    chat_message = db.Column(db.Text, nullable=False)
    message_type = db.Column(db.String(10))  # user / ai

    created_at = db.Column(db.DateTime, default=datetime.utcnow)