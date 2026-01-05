from functools import wraps
from flask_jwt_extended import get_jwt_identity

from app.models.client_list import Client  # your user table
from app.utils.permission import has_access
from app.utils.response import error_response


def require_acl(acl_code):
    """
    RBAC decorator
    """

    def wrapper(fn):
        @wraps(fn)
        def decorated(*args, **kwargs):

            user_id = get_jwt_identity()

            user = Client.query.filter_by(uuid=user_id).first()

            if not user:
                return error_response(
                    message="User not found",
                    status=404,
                    error_code="USER_NOT_FOUND"
                )

            if not user.role_uuid:
                return error_response(
                    message="Role not assigned",
                    status=403,
                    error_code="NO_ROLE_ASSIGNED"
                )

            if not has_access(user.role_uuid, acl_code):
                return error_response(
                    message="Access denied",
                    status=403,
                    error_code="FORBIDDEN"
                )

            return fn(*args, **kwargs)

        return decorated

    return wrapper