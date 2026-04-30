'''
Author : Akash Mambally
GitHub: https://github.com/akaspringfield
'''
# app/routes/admin_dashboard.py

from flask import Blueprint
from flask_jwt_extended import jwt_required

from app.utils.response import success_response
from app.utils.decorators import protected
from app.audit_logs.decorator import audit
from app.audit_logs.constants import *

from app.services.dashboard_service import get_dashboard_data


admin_dashboard_bp = Blueprint(
    "admin_dashboard",
    __name__,
    url_prefix="/admin"
)


'''
ADMIN DASHBOARD DATA
GET /admin/dashboard
Returns:

Summary cards
Users per role chart
User growth chart
'''
@admin_dashboard_bp.route("/dashboard", methods=["GET"])
@jwt_required()
@protected("ADMIN_DASHBOARD")
@audit(DASHBOARD_VIEW, "DASHBOARD", "VIEW")
def get_dashboard():
    data = get_dashboard_data()

    return success_response(
        data=data,
        message="Dashboard data fetched successfully"
    )