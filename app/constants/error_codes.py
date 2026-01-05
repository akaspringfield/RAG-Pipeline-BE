ERROR_MAP = {

    # ---------------- AI LAYER ----------------
    "AI_FAILURE": {
        "status": 500,
        "message": "AI internal failure"
    },

    "AI_UNAVAILABLE": {
        "status": 503,
        "message": "AI service not reachable"
    },
    
    "AI_UNREACHABLE": {
        "status": 503,
        "message": "AI service not reachable"
    },

    "AI_TIMEOUT": {
        "status": 504,
        "message": "AI request timeout"
    },

    "AI_INVALID_RESPONSE": {
        "status": 502,
        "message": "AI returned invalid response"
    },


    # ---------------- AUTH LAYER ----------------
    "TOKEN_MISSING": {
        "status": 401,
        "message": "Authorization token is required"
    },

    "TOKEN_INVALID": {
        "status": 401,
        "message": "Invalid authentication token"
    },

    "TOKEN_EXPIRED": {
        "status": 401,
        "message": "Token has expired"
    },

    "TOKEN_REVOKED": {
        "status": 401,
        "message": "Token has been revoked"
    },

    "INVALID_REFRESH_TOKEN": {
        "status": 401,
        "message": "Invalid refresh token"
    },


    # ---------------- REQUEST VALIDATION ----------------
    "BAD_REQUEST": {
        "status": 400,
        "message": "Bad request"
    },

    "VALIDATION_ERROR": {
        "status": 400,
        "message": "Validation failed"
    },

    "MISSING_FIELDS": {
        "status": 400,
        "message": "Required fields are missing"
    },

    "USER_NOT_FOUND": {
        "status": 404,
        "message": "User not found"
    },

    "BAD_REQUEST": {
        "status": 400,
        "message": "Bad request"
    },

    # ---------------- RATE LIMIT ----------------
    "RATE_LIMIT_EXCEEDED": {
        "status": 429,
        "message": "Too many requests. Please try again later."
    },


    # ---------------- CHAT / BUSINESS LOGIC ----------------
    "CHAT_NOT_FOUND": {
        "status": 404,
        "message": "Chat not found"
    },

    "MESSAGE_FAILED": {
        "status": 500,
        "message": "Failed to process message"
    },


    # ---------------- GENERAL ----------------
    "INTERNAL_ERROR": {
        "status": 500,
        "message": "Internal server error"
    }
}