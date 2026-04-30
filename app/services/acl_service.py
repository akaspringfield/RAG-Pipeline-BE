'''
Author : Akash Mambally
GitHub: https://github.com/akaspringfield
'''

from app.models.role import ClientACL


def list_all_acls():
    """
    Fetch all ACLs in system
    """

    acls = ClientACL.query.all()

    return [
        {
            "uuid": str(a.uuid),
            "acl_title": a.acl_title,
            "acl_description": a.acl_description,
            "status": a.status
        }
        for a in acls
    ], None