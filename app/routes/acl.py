from flask import Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.models.user import Client
from app.services.acl_service import list_all_acls
from app.utils.response import success_response, error_response

acl_bp = Blueprint("acl", __name__)


# ---------------- LIST ALL ACLS (SUPERADMIN ONLY) ----------------
@acl_bp.route("/", methods=["GET"])
@jwt_required()
def get_acls():

    user_id = get_jwt_identity()

    user = Client.query.filter_by(uuid=user_id).first()

    if not user:
        return error_response("User not found", 404, "USER_NOT_FOUND")

    # 🔐 SUPER ADMIN CHECK
    if user.client_status != "SUPER_ADMIN":
        return error_response("Access denied", 403, "FORBIDDEN")

    data, _ = list_all_acls()

    return success_response(
        data=data,
        message="ACL list fetched successfully"
    )