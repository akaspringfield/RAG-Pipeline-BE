from functools import wraps
from flask_jwt_extended import get_jwt_identity

from app.models.user import Client
from app.models.session import ClientSession
from app.utils.permissions import has_access
from app.utils.response import error_response


def require_acl(acl_code):

    def wrapper(fn):

        @wraps(fn)
        def decorated(*args, **kwargs):

            # ---------------- GET USER ID FIRST ----------------
            user_id = get_jwt_identity()

            if not user_id:
                return error_response(
                    message="Missing token identity",
                    status=401,
                    error_code="TOKEN_INVALID"
                )

            # ---------------- GET USER ----------------
            user = Client.query.filter_by(uuid=user_id).first()

            if not user:
                return error_response(
                    message="User not found",
                    status=404,
                    error_code="USER_NOT_FOUND"
                )

            # ---------------- SESSION VALIDATION ----------------
            session = ClientSession.query.filter_by(
                client_uuid=user_id,
                is_revoked=False
            ).first()

            if not session:
                return error_response(
                    message="Session expired or revoked",
                    status=401,
                    error_code="SESSION_INVALID"
                )

            # ---------------- SUPER ADMIN BYPASS ----------------
            # (fix: check role, NOT status)
            if user.role and user.role.role_name == "SUPER_ADMIN":
                return fn(*args, **kwargs)

            # ---------------- ROLE CHECK ----------------
            if not user.role_uuid:
                return error_response(
                    message="Role not assigned",
                    status=403,
                    error_code="NO_ROLE_ASSIGNED"
                )

            # ---------------- ACL CHECK ----------------
            if not has_access(user.role_uuid, acl_code):
                return error_response(
                    message="Access denied",
                    status=403,
                    error_code="FORBIDDEN"
                )

            return fn(*args, **kwargs)

        return decorated

    return wrapper