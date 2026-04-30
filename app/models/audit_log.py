'''
Author : Akash Mambally
GitHub: https://github.com/akaspringfield
'''

import uuid 
from datetime import datetime, timedelta
from app.extensions import db


# class AuditLog(db.Model):
#     __tablename__ = "audit_logs"

#     id = db.Column(db.Integer, primary_key=True)
#     uuid = db.Column(db.String(36), unique=True, default=lambda: str(uuid.uuid4()))

#     event = db.Column(db.String(100))
#     module = db.Column(db.String(50))
#     action = db.Column(db.String(50))

#     user_id = db.Column(db.String(36), nullable=True)
#     status = db.Column(db.String(20))

#     created_at = db.Column(db.DateTime, default=datetime.utcnow)