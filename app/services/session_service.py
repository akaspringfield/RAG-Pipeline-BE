'''
Author : Akash Mambally
GitHub: https://github.com/akaspringfield
'''

from flask_jwt_extended import get_jwt_identity
from app.models.session import ClientSession
from app.extensions import db
from datetime import datetime

def get_active_sessions(user_uuid, current_refresh_hash=None):

    sessions = ClientSession.query.filter_by(
        client_uuid=user_uuid,
        is_revoked=False
    ).all()

    result = []

    for s in sessions:
        result.append({
            "uuid": str(s.uuid),
            "device_info": s.device_info,
            "ip_address": s.ip_address,
            "created_at": s.created_at,
            "expires_at": s.expires_at
        })

    return result


def revoke_session_by_uuid(user_uuid, session_uuid):

    session = ClientSession.query.filter_by(
        uuid=session_uuid,
        client_uuid=user_uuid
    ).first()

    if not session:
        return None, "SESSION_NOT_FOUND"

    session.is_revoked = True
    session.updated_at = datetime.utcnow()

    db.session.commit()

    return {
        "session_id": str(session.uuid),
        "status": "revoked"
    }, None