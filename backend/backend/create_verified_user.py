import app.db.base
import uuid
from app.db.session import SessionLocal
from app.models.user import User
from app.models.organization import Organization
from app.models.role import Role
from app.models.user_role import UserRole
from app.models.workspace import Workspace
from app.models.workspace_member import WorkspaceMember
from app.core.security import hash_password
from app.models.enums import Sector, UserStatus

def create_verified_user():
    db = SessionLocal()
    try:
        # Check if user already exists
        email = "test@example.com"
        password = "password123"
        
        user = db.query(User).filter(User.email == email).first()
        if user:
            user.is_verified = True
            user.status = UserStatus.ACTIVE
            db.commit()
            print(f"User {email} already exists. Marked as verified.")
            return

        print(f"Creating new verified user: {email}")
        org = Organization(
            name="TestOrg",
            slug="testorg-slug",
            industry="retail"
        )
        db.add(org)
        db.flush()

        roles = {name: Role(organization_id=org.id, name=name) for name in ["admin", "manager", "user"]}
        db.add_all(roles.values())
        db.flush()

        user = User(
            organization_id=org.id,
            first_name="Admin",
            last_name="TestOrg",
            email=email,
            password_hash=hash_password(password),
            is_verified=True,
            status=UserStatus.ACTIVE
        )
        db.add(user)
        db.flush()

        db.add(UserRole(user_id=user.id, role_id=roles["admin"].id))

        workspace = Workspace(
            organization_id=org.id,
            name="TestOrg Workspace",
            industry_type="retail",
            sector=Sector.RETAIL,
            created_by=user.id
        )
        db.add(workspace)
        db.flush()

        db.add(WorkspaceMember(workspace_id=workspace.id, user_id=user.id, member_role="admin"))
        db.commit()
        print("Verified user created successfully.")
    except Exception as e:
        db.rollback()
        print(f"Error creating user: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    create_verified_user()
