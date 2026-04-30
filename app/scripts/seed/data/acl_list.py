
ACL_LIST = [

    # ===============================
    # SESSION MANAGEMENT
    # ===============================
    ("LOGOUT_ALL_USERS", "Logout all user sessions"),
    ("LOGOUT_SINGLE_USER", "Logout single user session"),

    # ===============================
    # USER MANAGEMENT
    # ===============================
    ("LIST_USERS", "List users"),
    ("VIEW_USER", "View user details"),
    ("CREATE_USER", "Create users"),
    ("UPDATE_USER", "Update users"),
    ("DELETE_USER", "Delete users"),
    ("ACTIVATE_USER", "Activate user"),
    ("DEACTIVATE_USER", "Deactivate user"),
    ("MANAGE_USER", "Full user management"),

    # ===============================
    # PROFILE
    # ===============================
    ("VIEW_PROFILE", "View profile"),
    ("UPDATE_PROFILE", "Update profile"),
    ("UPDATE_SUBSCRIPTION", "Update user subscription"),

    # ===============================
    # ACL MANAGEMENT
    # ===============================
    ("LIST_ACL", "List ACL permissions"),
    ("VIEW_ACL", "View ACL permission"),
    ("CREATE_ACL", "Create ACL permission"),
    ("UPDATE_ACL", "Update ACL permission"),
    ("DELETE_ACL", "Delete ACL permission"),
    ("MANAGE_ACL", "Full ACL management"),

    # ===============================
    # ROLE MANAGEMENT
    # ===============================
    ("LIST_ROLE", "List roles"),
    ("VIEW_ROLE", "View role"),
    ("CREATE_ROLE", "Create role"),
    ("UPDATE_ROLE", "Update role"),
    ("DELETE_ROLE", "Delete role"),
    ("MANAGE_ROLE", "Full role management"),

    # ===============================
    # ROLE ↔ ACL MAPPING
    # ===============================
    ("LIST_ACL_ROLE", "List role ACL mappings"),
    ("VIEW_ACL_ROLE", "View role ACL mapping"),
    ("ASSIGN_ACL_ROLE", "Assign ACL to role"),
    ("UPDATE_ACL_ROLE", "Update role ACL mapping"),
    ("REMOVE_ACL_ROLE", "Remove ACL from role"),
    ("MANAGE_ACL_ROLE", "Full ACL-to-role management"),

    # ===============================
    # USER ↔ ROLE MAPPING
    # ===============================
    ("LIST_CLIENT_ROLE_MAPPING", "List user role mappings"),
    ("VIEW_CLIENT_ROLE_MAPPING", "View user role mapping"),
    ("CREATE_CLIENT_ROLE_MAPPING", "Assign role to user"),
    ("UPDATE_CLIENT_ROLE_MAPPING", "Update user role mapping"),
    ("DELETE_CLIENT_ROLE_MAPPING", "Remove role from user"),
    ("MANAGE_CLIENT_ROLE_MAPPING", "Full user-role management"),

    # ===============================
    # CHAT MANAGEMENT
    # ===============================
    ("LIST_CHAT_HISTORY", "List chat history"),
    ("VIEW_CHAT", "View chat"),
    ("CREATE_CHAT", "Create chat"),
    ("DELETE_CHAT", "Delete chat"),
    ("MANAGE_CHAT", "Full chat management"),

    # ===============================
    # AUDIT LOGS
    # ===============================
    ("VIEW_AUDIT_LOGS", "View audit logs"),
    ("DELETE_AUDIT_LOGS", "Delete audit logs"),

    # ===============================
    # ADMIN DASHBOARD (NEW)
    # ===============================
    ("VIEW_ADMIN_DASHBOARD", "Access admin dashboard"),
    ("VIEW_DASHBOARD_SUMMARY", "View dashboard summary cards"),
    ("VIEW_USER_GROWTH_ANALYTICS", "View user growth analytics"),
    ("VIEW_ROLE_DISTRIBUTION", "View role distribution analytics"),
    ("VIEW_ACL_USAGE", "View ACL usage analytics"),
    ("VIEW_AUDIT_ACTIVITY", "View audit activity analytics"),
]
