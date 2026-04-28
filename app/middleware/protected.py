from functools import wraps
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
import uuid

from app.models.user import Client
from app.utils.response import error_response
from app.utils.rbac_service import user_has_permission, get_user_permissions
import traceback


def protected(required_permission=None):
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            try:
                # ---------------- VERIFY TOKEN ----------------

                identity = get_jwt_identity()
                if not identity:
                    return error_response("Missing token identity", 401, "INVALID_TOKEN")

                # ---------------- VALIDATE UUID ----------------
                try:
                    user_uuid = uuid.UUID(str(identity))
                except Exception:
                    return error_response("Invalid UUID in token", 401, "INVALID_UUID")

                print(f"🔐 USER UUID: {user_uuid}")

                # ---------------- FETCH USER ----------------
                user = Client.query.filter_by(uuid=user_uuid).first()
                if not user:
                    return error_response("User not found", 404, "USER_NOT_FOUND")

                # ---------------- LOGIN ONLY ROUTES ----------------
                if required_permission is None:
                    return fn(*args, **kwargs)

                # ---------------- FETCH PERMISSIONS ----------------
                permissions = get_user_permissions(user_uuid)
                print("🔐 PERMISSIONS:", permissions)

                # ---------------- NO ACL ----------------
                if not permissions:
                    return error_response(
                        "No permissions assigned to user",
                        403,
                        "NO_ACL_ASSIGNED"
                    )

                # ---------------- CHECK PERMISSION ----------------
                if required_permission not in permissions:
                    return error_response(
                        "You don't have permission to access this resource",
                        403,
                        "FORBIDDEN"
                    )

                return fn(*args, **kwargs)

            except Exception as e:
                print("🔥 AUTH ERROR:", repr(e))
                traceback.print_exc()
                return error_response("Internal server error", 500, "AUTH_FAILED")
        
        return decorator
    
    return wrapper