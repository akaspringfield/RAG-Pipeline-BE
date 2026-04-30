'''
Author : Akash Mambally
GitHub: https://github.com/akaspringfield
'''

import uuid 
from datetime import datetime, timedelta
from app.extensions import db


# ===============================
# ACL (Permissions)
# ===============================
class ClientACL(db.Model):
    __tablename__ = "client_acl"

    uuid = db.Column(db.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    acl_key = db.Column(db.String(100), unique=True, nullable=False)
    
    acl_title = db.Column(db.String(100), nullable=False)
    acl_description = db.Column(db.Text)

    status = db.Column(db.String(20), default="active")
    created_on = db.Column(db.DateTime, server_default=db.func.now())
    created_by = db.Column(db.UUID(as_uuid=True))
    updated_on = db.Column(db.DateTime)
    updated_by = db.Column(db.UUID(as_uuid=True))


# ===============================
# Roles
# ===============================
class ClientRole(db.Model):
    __tablename__ = "client_roles"

    uuid = db.Column(db.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    role_name = db.Column(db.String(100), unique=True, nullable=False)
    role_description = db.Column(db.Text)

    status = db.Column(db.String(20), default="active")
    created_on = db.Column(db.DateTime, server_default=db.func.now())
    created_by = db.Column(db.UUID(as_uuid=True))
    updated_on = db.Column(db.DateTime)
    updated_by = db.Column(db.UUID(as_uuid=True))


# ===============================
# Role → ACL Mapping
# ===============================
class RoleACLMapping(db.Model):
    __tablename__ = "role_acl_mapping"

    uuid = db.Column(db.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    role_uuid = db.Column(
        db.UUID(as_uuid=True),
        db.ForeignKey("client_roles.uuid"),
        nullable=False
    )

    acl_uuid = db.Column(
        db.UUID(as_uuid=True),
        db.ForeignKey("client_acl.uuid"),
        nullable=False
    )
    status = db.Column(db.String(20), default="active")  # ⭐ ADD THIS

    created_on = db.Column(db.DateTime, server_default=db.func.now())
    created_by = db.Column(db.UUID(as_uuid=True))
    updated_on = db.Column(db.DateTime)
    updated_by = db.Column(db.UUID(as_uuid=True))

    __table_args__ = (
        db.UniqueConstraint('role_uuid', 'acl_uuid', name='unique_role_acl'),
    )


# ===============================
# Client → Role Mapping
# ===============================
class ClientRoleMapping(db.Model):
    __tablename__ = "client_role_mapping"

    uuid = db.Column(db.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    client_uuid = db.Column(db.UUID(as_uuid=True), nullable=False)

    role_uuid = db.Column(
        db.UUID(as_uuid=True),
        db.ForeignKey("client_roles.uuid"),
        nullable=False
    )

    client_auth_code = db.Column(db.String(100), nullable=True)

    status = db.Column(db.String(20), default="active")

    access_valid_from = db.Column(db.DateTime)
    access_valid_to = db.Column(db.DateTime)

    created_on = db.Column(db.DateTime, server_default=db.func.now())
    created_by = db.Column(db.UUID(as_uuid=True))
    updated_on = db.Column(db.DateTime)
    updated_by = db.Column(db.UUID(as_uuid=True))

    __table_args__ = (
        db.UniqueConstraint('client_uuid', 'role_uuid', name='unique_client_role'),
    )