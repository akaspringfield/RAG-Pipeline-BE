'''
Author : Akash Mambally
GitHub: https://github.com/akaspringfield
'''

import uuid
from datetime import datetime
from app.extensions import db


class Client(db.Model):
    __tablename__ = "client_list"

    uuid = db.Column(db.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    client_name = db.Column(db.String(100))
    client_email = db.Column(db.String(120), unique=True)
    client_status = db.Column(db.String(20), default="active")

    created_on = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.UUID(as_uuid=True))
    updated_on = db.Column(db.DateTime)
    updated_by = db.Column(db.UUID(as_uuid=True))

    # 🔗 relation to password table
    password = db.relationship(
        "ClientPassword",
        backref="client",
        uselist=False,
        cascade="all, delete-orphan"
    )


# ---------------- PASSWORD TABLE (BISCUITS) ----------------

class ClientPassword(db.Model):
    __tablename__ = "biscuits"

    uuid = db.Column(db.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    client_uuid = db.Column(
        db.UUID(as_uuid=True),
        db.ForeignKey("client_list.uuid"),
        nullable=False,
        unique=True
    )

    password_hash = db.Column(db.String(255), nullable=False)

    created_on = db.Column(db.DateTime, default=datetime.utcnow)
    updated_on = db.Column(db.DateTime)
    updated_by = db.Column(db.UUID(as_uuid=True))



