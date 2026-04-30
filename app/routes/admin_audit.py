from flask import Blueprint, request
from datetime import datetime, timedelta
import uuid

from app.extensions import db
from app.audit_logs.model import AuditLog
from app.utils.response import success_response, error_response
from app.middleware.protected import protected
from app.audit_logs.constants import *

admin_audit_bp = Blueprint("admin_audit", __name__, url_prefix="/api/admin/audit-logs")


''' 
Get logs
GET /admin/audit-logs?page=1&limit=20
'''
@admin_audit_bp.route("", methods=["GET"])
@protected("USER_READ")   # or ADMIN_READ later
def list_audit_logs():
    try:
        query = AuditLog.query

        # ---------- FILTERS ----------
        user_uuid = request.args.get("user_uuid")
        event_type = request.args.get("event_type")
        entity_type = request.args.get("entity_type")
        from_date = request.args.get("from_date")
        to_date = request.args.get("to_date")

        if user_uuid:
            query = query.filter(AuditLog.user_uuid == uuid.UUID(user_uuid))

        if event_type:
            query = query.filter(AuditLog.event_type == event_type)

        if entity_type:
            query = query.filter(AuditLog.entity_type == entity_type)

        if from_date:
            query = query.filter(AuditLog.created_on >= datetime.fromisoformat(from_date))

        if to_date:
            query = query.filter(AuditLog.created_on <= datetime.fromisoformat(to_date))

        # ---------- PAGINATION ----------
        page = int(request.args.get("page", 1))
        limit = int(request.args.get("limit", 20))

        logs = query.order_by(AuditLog.created_on.desc()).paginate(page=page, per_page=limit)

        result = []
        for log in logs.items:
            result.append({
                "id": str(log.uuid),
                "user_uuid": str(log.user_uuid) if log.user_uuid else None,
                "event_type": log.event_type,
                "entity_type": log.entity_type,
                "entity_id": str(log.entity_uuid) if log.entity_uuid else None,
                "action": log.action,
                "description": log.description,
                "ip_address": log.ip_address,
                "created_on": log.created_on.isoformat()
            })

        return success_response(
            data={
                "logs": result,
                "total": logs.total,
                "page": page
            },
            message="Audit logs fetched"
        )

    except Exception as e:
        return error_response(str(e), 500, "AUDIT_FETCH_FAILED")
    

'''
Filter by user
GET /admin/audit-logs?user_uuid=<uuid>
Filter by event
GET /admin/audit-logs?event_type=ACCESS_DENIED
'''
@admin_audit_bp.route("/<log_id>", methods=["GET"])
@protected("USER_READ")
def get_audit_log(log_id):
    try:
        log = AuditLog.query.get(uuid.UUID(log_id))
        if not log:
            return error_response("Log not found", 404, "NOT_FOUND")

        return success_response(
            data={
                "id": str(log.uuid),
                "user_uuid": str(log.user_uuid) if log.user_uuid else None,
                "event_type": log.event_type,
                "entity_type": log.entity_type,
                "entity_id": str(log.entity_uuid) if log.entity_uuid else None,
                "action": log.action,
                "description": log.description,
                "ip_address": log.ip_address,
                "created_on": log.created_on.isoformat()
            },
            message="Audit log fetched"
        )

    except Exception as e:
        return error_response(str(e), 500, "AUDIT_FETCH_FAILED")
    

'''
Delete logs older than 90 days
DELETE /admin/audit-logs?days=90
'''
@admin_audit_bp.route("", methods=["DELETE"])
@protected("SUPER_ADMIN")
def purge_old_logs():
    try:
        days = int(request.args.get("days", 30))
        cutoff = datetime.utcnow() - timedelta(days=days)

        deleted = AuditLog.query.filter(AuditLog.created_on < cutoff).delete()
        db.session.commit()

        return success_response(
            data={"deleted_rows": deleted},
            message=f"Logs older than {days} days deleted"
        )

    except Exception as e:
        return error_response(str(e), 500, "AUDIT_PURGE_FAILED")