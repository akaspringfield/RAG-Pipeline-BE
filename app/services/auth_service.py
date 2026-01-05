from datetime import datetime, timedelta
from flask_jwt_extended import create_access_token, create_refresh_token

from app.extensions import db
from app.models.user import Client
from app.models.auth import ClientPassword
from app.models.session import ClientSession
from app.utils.security import hash_password, verify_password, hash_token
from app.models.usage import ClientUsage


# ---------------- REGISTER ----------------

def register_user(name, email, password):

    existing = Client.query.filter_by(client_email=email).first()
    if existing:
        return None, "User already exists"

    client = Client(
        client_name=name,
        client_email=email
    )

    db.session.add(client)
    db.session.flush()

    pwd = ClientPassword(
        client_uuid=client.uuid,
        password=hash_password(password)
    )

    # ✅ ADD THIS: create usage record
    usage = ClientUsage(
        client_uuid=client.uuid,
        token_counter=0,
        token_limit=1000,
        token_reset_time=datetime.utcnow() + timedelta(days=1)
    )

    db.session.add(pwd)
    db.session.add(usage)

    db.session.commit()

    return client, None

# def register_user(name, email, password):

#     existing = Client.query.filter_by(client_email=email).first()
#     if existing:
#         return None, "User already exists"

#     client = Client(
#         client_name=name,
#         client_email=email
#     )

#     db.session.add(client)
#     db.session.flush()  # get UUID before commit

#     pwd = ClientPassword(
#         client_uuid=client.uuid,
#         password=hash_password(password)
#     )

#     db.session.add(pwd)
#     db.session.commit()

#     return client, None


# ---------------- LOGIN ----------------
def login_user(email, password):

    client = Client.query.filter_by(client_email=email).first()
    if not client:
        return None, None, "Invalid credentials"

    pwd = ClientPassword.query.filter_by(client_uuid=client.uuid).first()

    if not verify_password(password, pwd.password):
        return None, None, "Invalid credentials"

    access_token = create_access_token(identity=str(client.uuid))
    refresh_token = create_refresh_token(identity=str(client.uuid))

    session = ClientSession(
        client_uuid=client.uuid,
        refresh_token_hash=hash_token(refresh_token),
        expires_at=datetime.utcnow() + timedelta(days=7)
    )

    db.session.add(session)
    db.session.commit()

    return access_token, refresh_token, None


# ---------------- REFRESH ----------------

from flask_jwt_extended import decode_token

def refresh_session(refresh_token):

    try:
        decoded = decode_token(refresh_token)

        if decoded.get("type") != "refresh":
            return None, "Invalid token type"

        user_id = decoded.get("sub")

        new_access = create_access_token(identity=user_id)

        return new_access, None

    except Exception:
        return None, "Invalid or expired refresh token"
    
