'''
Author : Akash Mambally
GitHub: https://github.com/akaspringfield
'''

from app.models.user import Client
from app.models.client_acl import ClientACL 


def list_all_users():

    users = Client.query.all()

    return [
        {
            "uuid": str(u.uuid),
            "name": u.client_name,
            "email": u.client_email,
            "status": u.client_status,
            "role_uuid": str(u.role_uuid) if u.role_uuid else None
        }
        for u in users
    ]

def list_all_acls():

    acls = ClientACL.query.all()

    return [
        {
            "uuid": str(a.uuid),
            "title": a.acl_title,
            "description": a.acl_description,
            "status": a.status
        }
        for a in acls
    ]

def toggle_user_status(user_id, status):

    user = Client.query.filter_by(uuid=user_id).first()

    if not user:
        return None, "USER_NOT_FOUND"

    if status not in ["ACTIVE", "INACTIVE"]:
        return None, "INVALID_STATUS"

    user.client_status = status

    from app import db
    db.session.commit()

    return {
        "user_id": str(user.uuid),
        "status": user.client_status
    }, None