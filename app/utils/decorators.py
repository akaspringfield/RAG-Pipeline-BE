from functools import wraps
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.utils.response import error_response
from app.utils.rbac_service import user_has_permission


def protected(acl_key):
    def wrapper(fn):
        @wraps(fn)
        @jwt_required()
        def decorator(*args, **kwargs):

            client_uuid = get_jwt_identity()

            if not user_has_permission(client_uuid, acl_key):
                return error_response(
                    message="You don't have permission to access this resource",
                    status=403,
                    error_code="ACCESS_DENIED"
                )

            return fn(*args, **kwargs)

        return decorator
    return wrapper