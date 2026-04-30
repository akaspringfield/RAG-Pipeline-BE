
from functools import wraps
from flask_jwt_extended import get_jwt_identity
from app.audit_logs.service import log_event


def audit(event_type, entity_type, action):
    """
    Auto audit decorator for successful actions.
    """
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            response = fn(*args, **kwargs)

            try:
                user_uuid = get_jwt_identity()
            except:
                user_uuid = None

            log_event(
                user_uuid=user_uuid,
                event_type=event_type,
                entity_type=entity_type,
                action=action,
                description=f"{action} performed on {entity_type}"
            )

            return response

        return decorator
    return wrapper






