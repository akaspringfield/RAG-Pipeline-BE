# 🚀 Flask AI Backend (RAG System)

This project is a Flask-based backend for AI chat (RAG system) with:

- JWT Authentication
- Role-Based Access Control (RBAC)
- ACL-based permissions
- Chat system
- AI service integration
- Redis caching & rate limiting (optional)

---

# 📦 Tech Stack

- Flask
- PostgreSQL
- SQLAlchemy
- Flask-Migrate (Alembic)
- Flask-JWT-Extended
- Redis (optional)
- External AI API

---

# ⚙️ 1. Initial Setup

## 🔹 Create virtual environment
```bash
python -m venv venv
🔹 Activate environment
Windows (Git Bash)
source venv/Scripts/activate
🔹 Install dependencies
pip install -r requirements.txt
🗄️ 2. Database Setup
🔹 Configure DB in .env
DATABASE_URL=postgresql://postgres:password@localhost:5432/your_db
🔹 Initialize migrations (first time only)
flask db init
🔹 Create migration
flask db migrate -m "initial migration with RBAC"
🔹 Apply migration
flask db upgrade
🧠 3. Required Tables (Auto created via migration)
client_list
client_roles
client_acl
client_role_mapping
👤 4. Create Super Admin (Manual DB Seed)
🔹 Create Role
INSERT INTO client_roles (uuid, role_name, role_description, status)
VALUES (
    gen_random_uuid(),
    'SUPER_ADMIN',
    'System Administrator with full access',
    'active'
);
🔹 Create Super User
INSERT INTO client_list (uuid, client_name, client_email, role_uuid, client_status)
VALUES (
    gen_random_uuid(),
    'Super Admin',
    'admin@system.com',
    '<ROLE_UUID_FROM_ABOVE>',
    'active'
);
🔐 5. Create Default ACLs
INSERT INTO client_acl (uuid, acl_title, acl_description, status)
VALUES 
(gen_random_uuid(), 'CHAT_SEND', 'Send chat messages', 'active'),
(gen_random_uuid(), 'PROFILE_UPDATE', 'Update user profile', 'active'),
(gen_random_uuid(), 'USER_READ', 'Read user data', 'active');
🔗 6. Role → ACL Mapping
INSERT INTO client_role_mapping (
    uuid,
    role_uuid,
    acl_uuid,
    status
)
SELECT 
    gen_random_uuid(),
    '<ROLE_UUID>',
    uuid,
    'active'
FROM client_acl;
🚀 7. Run Application
python run.py

Server will start at:

http://127.0.0.1:5000
🔑 8. Authentication Flow
Login → Get JWT
POST /auth/login
Use Token
Authorization: Bearer <token>
💬 9. Chat APIs
Create Chat
POST /chat/create
Send Message
POST /chat/message
👤 10. User APIs
Get Profile
GET /user/profile
Update Profile
PUT /user/profile
⚡ 11. Redis (Optional)

Used for:

Rate limiting
Cache
Start Redis
redis-server

If Redis is OFF:

Rate limiting will be skipped safely (fallback enabled)
🔥 12. Common Issues
❌ Redis not connected

Ignore in dev OR start Redis server

❌ JWT secret warning

Use at least 32-char secret:

JWT_SECRET_KEY=your_super_secure_32_char_key_here
❌ 401 Unauthorized

Token missing or expired

❌ AI service down
{
  "error_code": "AI_UNAVAILABLE",
  "message": "AI service not reachable"
}
🧱 13. Architecture Overview
User → JWT → Flask API → ACL Check → Service Layer → AI / DB → Response
🧠 14. Key Design Rules
All errors follow unified format
RBAC via roles + ACL mapping
No hardcoded permission strings (use ACL table)
All APIs protected with JWT
AI failures handled gracefully (no crash)