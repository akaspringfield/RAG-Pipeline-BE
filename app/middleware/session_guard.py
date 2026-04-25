from functools import wraps
from flask_jwt_extended import get_jwt_identity

from app.models.session import ClientSession
from app.utils.response import error_response


def require_active_session(fn):

    @wraps(fn)
    def wrapper(*args, **kwargs):

        user_id = get_jwt_identity()

        if not user_id:
            return error_response(
                "Missing token identity",
                401,
                "TOKEN_INVALID"
            )

        # check active session exists
        session = ClientSession.query.filter_by(
            client_uuid=user_id,
            is_revoked=False
        ).first()

        if not session:
            return error_response(
                "Session expired or logged out",
                401,
                "SESSION_INVALID"
            )

        return fn(*args, **kwargs)

    return wrapper