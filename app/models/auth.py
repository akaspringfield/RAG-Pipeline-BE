import uuid
from app.extensions import db

class ClientPassword(db.Model):
    __tablename__ = "biscuits"

    uuid = db.Column(db.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    client_uuid = db.Column(db.UUID)
    password = db.Column(db.Text)