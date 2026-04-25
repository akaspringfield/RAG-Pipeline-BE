'''
Author : Akash Mambally
GitHub: https://github.com/akaspringfield
'''

from datetime import datetime, timedelta
import uuid

from app.extensions import db
from app.models.user import Client
from app.models.auth import ClientPassword
from app.utils.security import hash_password, verify_password


def create_reset_token(email):
    user = Client.query.filter_by(client_email=email).first()

    if not user:
        return None, "USER_NOT_FOUND"

    token = str(uuid.uuid4())

    # store hashed token (you can create table later)
    # for now assume simple in-memory / DB table exists

    return token, None

def reset_password(email, token, new_password):
    user = Client.query.filter_by(client_email=email).first()

    if not user:
        return None, "USER_NOT_FOUND"

    # validate token (you will plug DB validation here)
    
    pwd = ClientPassword.query.filter_by(client_uuid=user.uuid).first()

    if not pwd:
        return None, "PASSWORD_NOT_SET"

    pwd.password = hash_password(new_password)
    pwd.updated_on = datetime.utcnow()

    db.session.commit()

    return True, None
