from app.constants.error_codes import ERROR_MAP
from flask import jsonify


def error_response(message, status=500, error_code="ERROR", error=None):
    """
    Standardized error response for entire app
    """
    error_info = ERROR_MAP.get(error_code, ERROR_MAP["INTERNAL_ERROR"])

    return {
        "error_code": error_code,
        "message": error_info["message"],
        "error": str(error) if error else error_info["message"],
        "success": False
    }, error_info["status"]
 

def success_response(data=None, message="Success", status=200):
    return jsonify({
        "success": True,
        "message": message,
        "data": data
    }), status

