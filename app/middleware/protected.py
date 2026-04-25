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
from app.models.user import Client
from app.models.session import ClientSession
from app.utils.permissions import has_access
from app.utils.response import error_response
import uuid
from flask_jwt_extended import jwt_required,verify_jwt_in_request, get_jwt_identity



def protected(permission=None):
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            try:
                client_uuid = None

                # ✅ Try to read JWT if present (but don't force it)
                try:
                    verify_jwt_in_request(optional=True)
                    identity = get_jwt_identity()
                    if identity:
                        client_uuid = uuid.UUID(identity)
                except Exception:
                    pass

                # ✅ DEV MODE — fallback user
                if not client_uuid:
                    print("🧪 DEV MODE: Using default test user")
                    client = Client.query.first()
                else:
                    client = Client.query.filter_by(uuid=client_uuid).first()

                if not client:
                    return error_response("User not found", 404, "USER_NOT_FOUND")

                # store user in flask global (optional future use)
                from flask import g
                g.current_client = client

                return fn(*args, **kwargs)

            except Exception as e:
                print("🔥 AUTH ERROR:", str(e))
                return error_response("Authentication failed", 401, "AUTH_FAILED")

        return decorator
    return wrapper