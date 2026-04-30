'''
Author : Akash Mambally
GitHub: https://github.com/akaspringfield
'''

# app/services/dashboard_service.py

from datetime import datetime, timedelta
from sqlalchemy import func

from app.extensions import db
from app.models.user import Client
from app.models.role import ClientACL, ClientRole, ClientRoleMapping


# ---------------------------------------------
# SUMMARY CARDS
# ---------------------------------------------
def get_dashboard_summary():
    total_users = Client.query.count()

    active_users = Client.query.filter_by(client_status="active").count()
    inactive_users = Client.query.filter_by(client_status="inactive").count()

    total_roles = ClientRole.query.count()
    total_acls = ClientACL.query.count()

    return {
        "total_users": total_users,
        "active_users": active_users,
        "inactive_users": inactive_users,
        "total_roles": total_roles,
        "total_acls": total_acls,
    }


# ---------------------------------------------
# USERS PER ROLE (Pie chart)
# ---------------------------------------------
def get_users_per_role():
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

    data = []
    for role_name, count in results:
        data.append({
            "role": role_name,
            "count": count
        })

    return data


# ---------------------------------------------
# USER GROWTH LAST 7 DAYS (Line chart)
# ---------------------------------------------
def get_user_growth_last_7_days():
    today = datetime.utcnow().date()
    seven_days_ago = today - timedelta(days=6)

    results = (
        db.session.query(
            func.date(Client.created_on),
            func.count(Client.uuid)
        )
        .filter(Client.created_on >= seven_days_ago)
        .group_by(func.date(Client.created_on))
        .order_by(func.date(Client.created_on))
        .all()
    )

    # Convert to dict for easy fill of missing dates
    growth_map = {str(date): count for date, count in results}

    data = []
    for i in range(7):
        day = seven_days_ago + timedelta(days=i)
        day_str = str(day)

        data.append({
            "date": day_str,
            "count": growth_map.get(day_str, 0)
        })

    return data


# ---------------------------------------------
# MASTER FUNCTION → COMBINES ALL
# ---------------------------------------------
def get_dashboard_data():
    return {
        "summary": get_dashboard_summary(),
        "users_per_role": get_users_per_role(),
        "user_growth_last_7_days": get_user_growth_last_7_days(),
    }