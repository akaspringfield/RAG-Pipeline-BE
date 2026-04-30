
from flask import request
from app.extensions import db
from app.audit_logs.model import AuditLog

def log_event(
    user_uuid=None,
    event_type=None,
    entity_type=None,
    entity_uuid=None,
    action=None,
    description=None
):
    """
    Central audit logger — call from anywhere.
    Never crashes your API if logging fails.
    """

    try:
        log = AuditLog(
            user_uuid=user_uuid,
            event_type=event_type,
            entity_type=entity_type,
            entity_uuid=entity_uuid,
            action=action,
            description=description,
            ip_address=request.remote_addr,
            user_agent=request.headers.get("User-Agent")
        )

        db.session.add(log)
        db.session.commit()

    except Exception as e:
        # 🚨 Never break main app if audit fails
        print("Audit log failed:", e)

