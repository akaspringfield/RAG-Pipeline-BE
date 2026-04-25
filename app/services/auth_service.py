from datetime import datetime, timedelta

from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    decode_token
)
from werkzeug.security import check_password_hash
from app.extensions import db
from app.models.user import Client, ClientPassword
from app.models.session import ClientSession
from app.models.usage import ClientUsage
from app.utils.security import hash_password, verify_password, hash_token
import secrets
from app.models.password_reset import PasswordReset
from app.models.token_blacklist import TokenBlacklist


# ---------------- REGISTER ----------------
def register_user(name, email, password):

    existing = Client.query.filter_by(client_email=email).first()
    if existing:
        return None, "User already exists"

    client = Client(
        client_name=name,
        client_email=email,
        client_status="active"
    )

    db.session.add(client)
    db.session.flush()

    pwd = ClientPassword(
        client_uuid=client.uuid,
        password=hash_password(password)
    )

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


# ---------------- LOGIN ----------------
def login_user(email, password):

    client = Client.query.filter_by(client_email=email).first()
    if not client:
        return None, None, "Invalid credentials"

    pwd = ClientPassword.query.filter_by(client_uuid=client.uuid).first()

    if not pwd:
        return None, None, "PASSWORD_NOT_SET"

    # FIXED: consistent hashing check
    if not check_password_hash(pwd.password, password):
        return None, None, "Invalid credentials"

    # JWT tokens
    access_token = create_access_token(identity=str(client.uuid))
    refresh_token = create_refresh_token(identity=str(client.uuid))

    # Store session (IMPORTANT FIX)
    session = ClientSession(
        client_uuid=client.uuid,
        refresh_token_hash=hash_token(refresh_token),
        expires_at=datetime.utcnow() + timedelta(days=7),
        is_revoked=False
    )

    db.session.add(session)
    db.session.commit()

    return access_token, refresh_token, None


# ---------------- AUTHENTICATE (USED BY LOGIN ROUTE) ----------------
def authenticate_user(email, password):

    user = Client.query.filter_by(client_email=email).first()

    if not user:
        return None, "USER_NOT_FOUND"

    if user.client_status != "active":
        return None, "USER_INACTIVE"

    creds = ClientPassword.query.filter_by(client_uuid=user.uuid).first()

    if not creds:
        return None, "PASSWORD_NOT_SET"

    # FIXED: consistent hashing
    if not check_password_hash(creds.password, password):
        return None, "INVALID_PASSWORD"

    return user, None


# ---------------- REFRESH SESSION ----------------
def refresh_session(refresh_token):

    try:
        decoded = decode_token(refresh_token)

        if decoded.get("type") != "refresh":
            return None, "INVALID_TOKEN_TYPE"

        user_id = decoded.get("sub")

        token_hash = hash_token(refresh_token)

        # ✅ SINGLE SOURCE OF TRUTH
        session = ClientSession.query.filter_by(
            client_uuid=user_id,
            refresh_token_hash=token_hash,
            is_revoked=False
        ).first()

        if not session:
            return None, "SESSION_REVOKED"

        if session.expires_at and session.expires_at < datetime.utcnow():
            return None, "SESSION_EXPIRED"

        # (optional) rotate refresh token here later

        new_access = create_access_token(identity=user_id)

        return new_access, None

    except Exception:
        return None, "INVALID_OR_EXPIRED_REFRESH"
    

# ---------------- LOGOUT SINGLE SESSION ----------------
def logout_session(refresh_token):

    session = ClientSession.query.filter_by(
        refresh_token_hash=hash_token(refresh_token)
    ).first()

    if session:
        session.is_revoked = True
        session.updated_at = datetime.utcnow()
        db.session.commit()

    return True


# ---------------- LOGOUT ALL SESSIONS ----------------
def logout_all_sessions(user_uuid):

    sessions = ClientSession.query.filter_by(
        client_uuid=user_uuid,
        is_revoked=False
    ).all()

    for s in sessions:
        s.is_revoked = True
        s.updated_at = datetime.utcnow()

    db.session.commit()

    return len(sessions)


# ---------------- LIST ACTIVE SESSIONS ----------------
def list_sessions(user_uuid):

    sessions = ClientSession.query.filter_by(
        client_uuid=user_uuid,
        is_revoked=False
    ).all()

    return [
        {
            "session_id": str(s.uuid),
            "device_info": s.device_info,
            "ip_address": s.ip_address,
            "expires_at": s.expires_at
        }
        for s in sessions
    ]


# ---------------- FORGOT PASSWORD ----------------
def forgot_password(email):

    user = Client.query.filter_by(client_email=email).first()
    if not user:
        return None, "USER_NOT_FOUND"

    # generate raw token
    raw_token = secrets.token_urlsafe(32)

    reset = PasswordReset(
        client_uuid=user.uuid,
        token_hash=hash_token(raw_token),
        expires_at=datetime.utcnow() + timedelta(minutes=30)
    )

    db.session.add(reset)
    db.session.commit()

    # In real system → send email
    reset_link = f"http://localhost:3000/reset-password?token={raw_token}"

    return {
        "reset_link": reset_link
    }, None


def reset_password(token, new_password):

    token_hash = hash_token(token)

    record = PasswordReset.query.filter_by(token_hash=token_hash, used=False).first()

    if not record:
        return None, "INVALID_TOKEN"

    if record.expires_at < datetime.utcnow():
        return None, "TOKEN_EXPIRED"

    # update password
    pwd = ClientPassword.query.filter_by(client_uuid=record.client_uuid).first()

    if not pwd:
        return None, "PASSWORD_NOT_FOUND"

    pwd.password = hash_password(new_password)

    # mark token used
    record.used = True

    db.session.commit()

    return {"message": "Password reset successful"}, None


def store_session(user_uuid, refresh_token, device_info=None, ip_address=None):

    session = ClientSession(
        client_uuid=user_uuid,
        refresh_token_hash=hash_token(refresh_token),
        device_info=device_info,
        ip_address=ip_address,
        is_revoked=False
    )

    db.session.add(session)
    db.session.commit()

    return session


def revoke_all_sessions(user_uuid):

    sessions = ClientSession.query.filter_by(
        client_uuid=user_uuid,
        is_revoked=False
    ).all()

    for s in sessions:
        s.is_revoked = True

    db.session.commit()

    return True

def list_sessions(user_uuid):

    sessions = ClientSession.query.filter_by(
        client_uuid=user_uuid,
        is_revoked=False
    ).all()

    return [
        {
            "session_id": str(s.uuid),
            "device": s.device_info,
            "ip": s.ip_address,
            "created_at": s.created_at
        }
        for s in sessions
    ]


def change_password(user_id, old_password, new_password):

    user = Client.query.filter_by(uuid=user_id).first()
    if not user:
        return None, "USER_NOT_FOUND"

    pwd = ClientPassword.query.filter_by(client_uuid=user_id).first()
    if not pwd:
        return None, "PASSWORD_NOT_SET"

    # verify old password
    if not verify_password(old_password, pwd.password):
        return None, "INVALID_OLD_PASSWORD"

    # update password
    pwd.password = hash_password(new_password)

    # 🔥 CRITICAL FIX: revoke ALL sessions
    ClientSession.query.filter_by(client_uuid=user_id).update(
        {"is_revoked": True}
    )

    db.session.commit()

    return True, None


def revoke_session(refresh_token, access_jti=None, user_id=None):

    # ---------------- Revoke DB session ----------------
    hashed = hash_token(refresh_token)

    session = ClientSession.query.filter_by(
        refresh_token_hash=hashed
    ).first()

    if session:
        session.is_revoked = True

    # ---------------- Blacklist access token ----------------
    if access_jti and user_id:
        db.session.add(TokenBlacklist(
            jti=access_jti,
            user_id=user_id
        ))

    db.session.commit()


def logout_all_sessions(user_uuid):
    """
    Revoke all active sessions for a user
    """

    sessions = ClientSession.query.filter_by(
        client_uuid=user_uuid,
        is_revoked=False
    ).all()

    if not sessions:
        return True, None

    for s in sessions:
        s.is_revoked = True
        s.updated_at = datetime.utcnow()

    db.session.commit()

    return True, None