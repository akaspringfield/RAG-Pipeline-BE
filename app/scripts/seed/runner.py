from app import create_app
from app.extensions import db

from app.scripts.seed.seed_acls import seed_acls
from app.scripts.seed.seed_roles import seed_roles
from app.scripts.seed.seed_role_acl import seed_role_acl
from app.scripts.seed.seed_superadmin import seed_superadmin


def run_all():
    print("🚀 STARTING SEED PROCESS")

    seed_acls()
    seed_roles()
    seed_role_acl()
    seed_superadmin()

    db.session.commit()

    print("✅ SEED COMPLETED SUCCESSFULLY")


if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        run_all()