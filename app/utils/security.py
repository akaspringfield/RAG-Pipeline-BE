import bcrypt
import hashlib


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def verify_token_hash(raw_token, hashed_token):
    return hash_token(raw_token) == hashed_token


def is_super_admin(user):
    """
    Centralized super admin check
    """

    if not user:
        return False

    # Option 1: role-based (BEST - future ready)
    if hasattr(user, "role") and user.role:
        return user.role.role_name == "SUPER_ADMIN"

    # Option 2: fallback (temporary, your current setup)
    return getattr(user, "client_status", None) == "SUPER_ADMIN"