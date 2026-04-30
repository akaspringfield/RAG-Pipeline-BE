from flask import Blueprint
from datetime import datetime, timedelta
from app.extensions import db
from sqlalchemy import func
from sqlalchemy.orm import joinedload

from flask_jwt_extended import jwt_required
from app.middleware.protected import protected
from app.utils.response import success_response

from app.models.user import Client
from app.models.role import ClientRole, ClientACL, ClientRoleMapping, RoleACLMapping
from app.models.session import ClientSession as UserSession
from app.audit_logs.model import AuditLog

from app.audit_logs.decorator import audit
from app.audit_logs.constants import *
from app.audit_logs.service import log_event
from flask import Flask, app
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
limiter = Limiter(key_func=get_remote_address)

admin_dashboard_bp = Blueprint(
    "admin_dashboard",
    __name__,
    url_prefix="/admin/dashboard"
)

# =========================================================
# USER GROWTH (Last 12 months)
# =========================================================
@admin_dashboard_bp.route("/user-growth", methods=["GET"])
@limiter.limit("30/minute")
@jwt_required()
@protected("ADMIN_DASHBOARD")
@audit(DASHBOARD_VIEW, "DASHBOARD", "USER_GROWTH")
def user_growth():
    today = datetime.utcnow()
    one_year_ago = today - timedelta(days=365)

    results = (
        db.session.query(
            func.date_trunc('month', Client.created_on).label("month"),
            func.count(Client.uuid)
        )
        .filter(Client.created_on >= one_year_ago)
        .group_by("month")
        .order_by("month")
        .all()
    )

    data = [{"month": r[0].strftime("%Y-%m"), "users": r[1]} for r in results]

    log_event(
        event=DASHBOARD_VIEW,
        description="Admin viewed dashboard summary"
    )

    return success_response(data=data)


@limiter.limit("30/minute")
def get_dashboard_summary():
    result = db.session.query(
        func.count(UserSession.id).label("total_users"),
        func.count(UserSession.id).filter(UserSession.status=="active").label("active_users"),
    ).one()

    active_sessions = db.session.query(func.count(UserSession.id))\
        .filter(UserSession.is_revoked==True).scalar()

    return {
        "total_users": result.total_users,
        "active_users": result.active_users,
        "active_sessions": active_sessions
    }

# =========================================================
# ROLE DISTRIBUTION
# =========================================================
@admin_dashboard_bp.route("/role-distribution", methods=["GET"])
@limiter.limit("30/minute")
@jwt_required()
@protected("ADMIN_DASHBOARD")
@audit(DASHBOARD_VIEW, "DASHBOARD", "ROLE_DISTRIBUTION")
def role_distribution():
    results = (
        db.session.query(
            ClientRole.role_name,
            func.count(ClientRoleMapping.client_uuid)
        )
        .join(ClientRoleMapping, ClientRole.uuid == ClientRoleMapping.role_uuid)
        .filter(ClientRoleMapping.status == "active")
        .group_by(ClientRole.role_name)
        .all()
    )

    data = [{"role": r[0], "users": r[1]} for r in results]

    log_event(
        event=DASHBOARD_VIEW,
        description="Admin viewed dashboard summary"
    )

    return success_response(data=data)


# =========================================================
# ACL USAGE
# =========================================================
@admin_dashboard_bp.route("/acl-usage", methods=["GET"])
@limiter.limit("30/minute")
@jwt_required()
@protected("ADMIN_DASHBOARD")
@audit(DASHBOARD_VIEW, "DASHBOARD", "ACL_USAGE")
def acl_usage():
    results = (
        db.session.query(
            ClientACL.acl_key,
            func.count(RoleACLMapping.role_uuid)
        )
        .join(RoleACLMapping, ClientACL.uuid == RoleACLMapping.acl_uuid)
        .filter(RoleACLMapping.status == "active")
        .group_by(ClientACL.acl_key)
        .all()
    )

    data = [{"acl": r[0], "roles_using": r[1]} for r in results]

    log_event(
        event=DASHBOARD_VIEW,
        description="Admin viewed dashboard summary"
    )

    return success_response(data=data)


# =========================================================
# AUDIT ACTIVITY (Last 7 days)
# =========================================================
@admin_dashboard_bp.route("/audit-activity", methods=["GET"])
@limiter.limit("30/minute")
@jwt_required()
@protected("ADMIN_DASHBOARD")
@audit(DASHBOARD_VIEW, "DASHBOARD", "AUDIT_ACTIVITY")
def audit_activity():
    last_week = datetime.utcnow() - timedelta(days=7)

    results = (
        db.session.query(
            func.date(AuditLog.created_on),
            func.count(AuditLog.uuid)
        )
        .filter(AuditLog.created_on >= last_week)
        .group_by(func.date(AuditLog.created_on))
        .order_by(func.date(AuditLog.created_on))
        .all()
    )

    data = [{"date": str(r[0]), "events": r[1]} for r in results]
    log_event(
        event=DASHBOARD_VIEW,
        description="Admin viewed dashboard summary"
    )
    return success_response(data=data)


# =========================================================
# DASHBOARD SUMMARY CARDS
# =========================================================
@admin_dashboard_bp.route("/summary", methods=["GET"])
@limiter.limit("30/minute")
@jwt_required()
@protected("ADMIN_DASHBOARD")
@audit(DASHBOARD_VIEW, "DASHBOARD", "SUMMARY")
def dashboard_summary():
    today = datetime.utcnow().date()

    total_users = db.session.query(func.count(Client.uuid)).scalar()
    active_users = db.session.query(func.count(Client.uuid)).filter(Client.status=="active").scalar()

    total_roles = db.session.query(func.count(ClientRole.uuid)).scalar()
    active_roles = db.session.query(func.count(ClientRole.uuid)).filter(ClientRole.status=="active").scalar()

    total_acls = db.session.query(func.count(ClientACL.uuid)).scalar()
    active_acls = db.session.query(func.count(ClientACL.uuid)).filter(ClientACL.status=="active").scalar()

    active_sessions = db.session.query(func.count(UserSession.uuid)).filter(UserSession.is_revoked==False).scalar()

    audit_today = db.session.query(func.count(AuditLog.uuid)).filter(
        func.date(AuditLog.created_on) == today
    ).scalar()

    data = {
        "users": {"total": total_users, "active": active_users},
        "roles": {"total": total_roles, "active": active_roles},
        "acls": {"total": total_acls, "active": active_acls},
        "sessions": {"active": active_sessions},
        "audit": {"today_events": audit_today}
    }

    log_event(
        event=DASHBOARD_VIEW,
        description="Admin viewed dashboard summary"
    )
    return success_response(data=data)


# =========================================================
# RECENT ACTIVITY (Latest 20 audit logs)
# =========================================================
@admin_dashboard_bp.route("/recent-activity", methods=["GET"])
@limiter.limit("30/minute")
@jwt_required()
@protected("ADMIN_DASHBOARD")
@audit(DASHBOARD_VIEW, "DASHBOARD", "RECENT_ACTIVITY")
def recent_activity():
    logs = (
        AuditLog.query
        .options(joinedload(AuditLog.user))
        .order_by(AuditLog.created_on.desc())
        .limit(20)
        .all()
    )

    data = []
    for log in logs:
        data.append({
            "event": log.event_type,
            "module": log.module,
            "action": log.action,
            "ip_address": log.ip_address,
            "timestamp": log.created_on.strftime("%Y-%m-%d %H:%M:%S"),
            "user": {
                "uuid": str(log.user_uuid) if log.user_uuid else None,
                "name": log.user.full_name if log.user else "System",
                "email": log.user.email if log.user else None
            }
        })

    log_event(
        event=DASHBOARD_VIEW,
        description="Admin viewed dashboard summary"
    )
    return success_response(data=data)