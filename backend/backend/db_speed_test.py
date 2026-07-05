import time
import uuid
import app.db.base
from app.db.session import SessionLocal
from app.models.user import User
from app.models.workspace import Workspace
from app.models.workspace_member import WorkspaceMember
from app.models.role import Role
from app.models.user_role import UserRole
from app.models.user_session import UserSession
from sqlalchemy import select
from sqlalchemy.orm import noload

def test_speed():
    db = SessionLocal()
    print("Testing DB execution speeds...")
    
    # 1. Connect / ping
    t0 = time.time()
    db.execute(select(1)).scalar()
    print(f"Ping took: {time.time() - t0:.3f}s")
    
    # 2. Select user with noload
    t0 = time.time()
    user = db.execute(
        select(User)
        .where(User.email == "test@example.com")
        .options(
            noload(User.organization),
            noload(User.user_roles),
            noload(User.sessions),
            noload(User.workspace_members),
            noload(User.datasets),
            noload(User.dataset_uploads),
            noload(User.analysis_jobs),
            noload(User.created_analysis_jobs),
            noload(User.updated_analysis_jobs),
            noload(User.ai_conversations),
            noload(User.report_exports),
            noload(User.notifications),
            noload(User.audit_logs),
            noload(User.system_settings)
        )
    ).scalar_one_or_none()
    print(f"Select User (with noload) took: {time.time() - t0:.3f}s")
    
    if not user:
        print("User test@example.com not found!")
        return

    # 3. Resolve workspace (columns only)
    t0 = time.time()
    ws_row = db.execute(
        select(Workspace.id, Workspace.sector)
        .join(WorkspaceMember, WorkspaceMember.workspace_id == Workspace.id)
        .where(WorkspaceMember.user_id == user.id)
    ).first()
    print(f"Resolve workspace (columns only) took: {time.time() - t0:.3f}s")

    # 4. Resolve role
    t0 = time.time()
    role = db.execute(
        select(Role.name)
        .join(UserRole, UserRole.role_id == Role.id)
        .where(UserRole.user_id == user.id)
    ).scalars().first()
    print(f"Resolve role took: {time.time() - t0:.3f}s")

    # 5. Insert session
    t0 = time.time()
    from datetime import datetime, timezone, timedelta
    session = UserSession(user_id=user.id, refresh_token=str(uuid.uuid4()), expires_at=datetime.now(timezone.utc) + timedelta(days=7))
    db.add(session)
    db.flush()
    print(f"Insert session + flush took: {time.time() - t0:.3f}s")

    # 6. Delete session
    t0 = time.time()
    db.delete(session)
    db.flush()
    print(f"Delete session + flush took: {time.time() - t0:.3f}s")

    # 7. Commit
    t0 = time.time()
    db.commit()
    print(f"Commit took: {time.time() - t0:.3f}s")

    db.close()

if __name__ == "__main__":
    test_speed()
