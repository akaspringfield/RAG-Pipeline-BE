from datetime import datetime

from app.extensions import db
from app.models.user import Client
from app.models.user import ClientPassword
from app.utils.security import hash_password, verify_password


# ---------------- GET PROFILE ----------------
def get_profile(user_uuid):

    user = Client.query.filter_by(uuid=user_uuid).first()

    if not user:
        return None, "USER_NOT_FOUND"

    return {
        "uuid": str(user.uuid),
        "name": user.client_name,
        "email": user.client_email,
        "status": user.client_status
    }, None


# ---------------- UPDATE PROFILE ----------------
def update_profile(user_uuid, data):

    if not data:
        return None, "BAD_REQUEST"

    user = Client.query.filter_by(uuid=user_uuid).first()

    if not user:
        return None, "USER_NOT_FOUND"

    # email uniqueness check
    if "email" in data:
        existing = Client.query.filter_by(client_email=data["email"]).first()
        if existing and existing.uuid != user.uuid:
            return None, "EMAIL_ALREADY_EXISTS"
        user.client_email = data["email"]

    if "name" in data:
        user.client_name = data["name"]

    user.updated_on = datetime.utcnow()

    db.session.commit()

    return {
        "uuid": str(user.uuid),
        "name": user.client_name,
        "email": user.client_email
    }, None


# ---------------- LIST USERS (ADMIN ONLY) ----------------
def list_users():

    users = Client.query.all()

    return [
        {
            "uuid": str(u.uuid),
            "name": u.client_name,
            "email": u.client_email,
            "status": u.client_status
        }
        for u in users
    ]


# ---------------- ACTIVATE / DEACTIVATE USER ----------------
def set_user_status(user_uuid, status):

    user = Client.query.filter_by(uuid=user_uuid).first()

    if not user:
        return None, "USER_NOT_FOUND"

    user.client_status = status
    user.updated_on = datetime.utcnow()

    db.session.commit()

    return {
        "uuid": str(user.uuid),
        "status": user.client_status
    }, None


# ---------------- CHANGE PASSWORD ----------------
def change_password(user_id, old_password, new_password):

    if not old_password or not new_password:
        return None, "VALIDATION_ERROR"

    user = Client.query.filter_by(uuid=user_id).first()
    if not user:
        return None, "USER_NOT_FOUND"

    pwd = ClientPassword.query.filter_by(client_uuid=user_id).first()
    if not pwd:
        return None, "PASSWORD_NOT_SET"

    if not verify_password(old_password, pwd.password):
        return None, "INVALID_OLD_PASSWORD"

    pwd.password = hash_password(new_password)
    pwd.updated_on = datetime.utcnow()

    db.session.commit()

    return {"message": "Password updated successfully"}, None

def list_users():

    users = Client.query.all()

    return [
        {
            "uuid": str(u.uuid),
            "name": u.client_name,
            "email": u.client_email,
            "status": u.client_status
        }
        for u in users
    ]


