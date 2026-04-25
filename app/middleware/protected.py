'''
include this
from app.middleware.protected import protected

insted of 
@jwt_required()
@require_active_session
@require_acl("USER_READ")
def get_users():

just add this 
@protected("USER_READ")
def get_users():
    ....

'''

from functools import wraps
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity

from app.models.user import Client
from app.models.session import ClientSession
from app.utils.permissions import has_access
from app.utils.response import error_response


def protected(acl_code=None):

    def wrapper(fn):

        @wraps(fn)
        def decorator(*args, **kwargs):

            # ---------------- JWT VALIDATION ----------------
            try:
                verify_jwt_in_request()
            except Exception:
                return error_response(
                    "Invalid or missing token",
                    401,
                    "TOKEN_INVALID"
                )

            user_id = get_jwt_identity()

            # ---------------- USER CHECK ----------------
            user = Client.query.filter_by(uuid=user_id).first()

            if not user:
                return error_response(
                    "User not found",
                    404,
                    "USER_NOT_FOUND"
                )

            # ---------------- SESSION VALIDATION ----------------
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

            # ---------------- SUPER ADMIN BYPASS ----------------
            if user.client_status == "SUPER_ADMIN":
                return fn(*args, **kwargs)

            # ---------------- ACL CHECK ----------------
            if acl_code:
                if not user.role_uuid:
                    return error_response(
                        "Role not assigned",
                        403,
                        "NO_ROLE_ASSIGNED"
                    )

                if not has_access(user.role_uuid, acl_code):
                    return error_response(
                        "Access denied",
                        403,
                        "FORBIDDEN"
                    )

            return fn(*args, **kwargs)

        return decorator

    return wrapper