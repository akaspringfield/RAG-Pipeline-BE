from app import db
from app.models.user import Client

def get_current_client():
    """
    TEMPORARY DEV AUTH
    Always returns first client in DB.
    Replace later with JWT auth.
    """
    client = Client.query.first()

    if not client:
        raise Exception("No client found in DB")

    return client