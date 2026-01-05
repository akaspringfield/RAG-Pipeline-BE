from flask import Blueprint, request, jsonify
from app.services.auth_service import register_user, login_user, refresh_session
from flask import Blueprint

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/health")
def test():
    return {"message": "application is healthy and working"}


# ---------------- REGISTER ----------------
@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.json

    user, error = register_user(
        data["name"],
        data["email"],
        data["password"]
    )

    if error:
        return jsonify({"error": error}), 400

    return jsonify({
        "message": "User created",
        "user_id": str(user.uuid)
    })


# ---------------- LOGIN ----------------
@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.json

    access, refresh, error = login_user(
        data["email"],
        data["password"]
    )

    if error:
        return jsonify({"error": error}), 401

    return jsonify({
        "access_token": access,
        "refresh_token": refresh
    })


# ---------------- REFRESH ----------------
# @auth_bp.route("/refresh", methods=["POST"])
# def refresh():
#     data = request.json

#     access, refresh = refresh_session(data["refresh_token"])

#     if not access:
#         return jsonify({"error": "Invalid refresh token"}), 401

#     return jsonify({
#         "access_token": access,
#         "refresh_token": refresh
#     })

@auth_bp.route("/refresh", methods=["POST"])
def refresh():

    data = request.get_json(silent=True)

    if not data:
        return {"error": True, "message": "Request body required"}, 400

    refresh_token = data.get("refresh_token")

    if not refresh_token:
        return {"error": True, "message": "refresh_token is mandatory"}, 400

    try:
        access, _ = refresh_session(refresh_token)

        if not access:
            return {"error": True, "message": "Invalid refresh token"}, 401

        return {
            "access_token": access
        }, 200

    except Exception:
        return {
            "error": True,
            "message": "Invalid or expired refresh token"
        }, 401
    

# @auth_bp.route("/refresh", methods=["POST"])
# def refresh():

#     data = request.get_json(silent=True)

#     if not data:
#         return {"error": True, "message": "Request body required"}, 400

#     refresh_token = data.get("refresh_token")

#     if not refresh_token:
#         return {"error": True, "message": "refresh_token is mandatory"}, 400

#     try:
#         access, new_refresh = refresh_session(refresh_token)

#         if not access:
#             return {"error": True, "message": "Invalid refresh token"}, 401

#         return {
#             "access_token": access,
#             "refresh_token": new_refresh
#         }, 200

#     except Exception:
#         return {
#             "error": True,
#             "message": "Invalid or expired refresh token"
#         }, 401