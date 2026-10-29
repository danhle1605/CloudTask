# tests/conftest.py
import re

import pytest

from app import create_app
from app.extensions import db
from app.models import Task, User, Workspace, WorkspaceMember


@pytest.fixture(scope="session")
def app():
    """Create testing application context."""
    test_app = create_app("testing")
    return test_app


@pytest.fixture(autouse=True)
def setup_database(app):
    """Isolate each test with clean tables."""
    with app.app_context():
        db.create_all()
        yield
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Test client for HTTP requests."""
    return app.test_client()


@pytest.fixture
def init_sample_data(app):
    """Create a default workspace, admin, and second member."""
    with app.app_context():
        user1 = User(full_name="Nguyễn Văn A", email="member1@example.com")
        user1.set_password("Password123!")
        db.session.add(user1)
        db.session.flush()

        ws = Workspace(name="CloudTask Team 8")
        db.session.add(ws)
        db.session.flush()

        m1 = WorkspaceMember(workspace_id=ws.id, user_id=user1.id, role="admin")
        db.session.add(m1)

        user2 = User(full_name="Trần Thị B", email="member2@example.com")
        user2.set_password("Password123!")
        db.session.add(user2)
        db.session.flush()

        m2 = WorkspaceMember(workspace_id=ws.id, user_id=user2.id, role="member")
        db.session.add(m2)

        task1 = Task(
            workspace_id=ws.id,
            created_by=user1.id,
            title="Thiết lập hạ tầng PaaS Render",
            description="Cấu hình environment variables và kết nối Neon PostgreSQL",
            status="in_progress",
            priority="high",
        )
        db.session.add(task1)
        db.session.commit()

        return {
            "workspace_id": ws.id,
            "user1_id": user1.id,
            "user2_id": user2.id,
            "task_id": task1.id,
        }


def extract_csrf_token(response_text: str) -> str | None:
    """Extract CSRF token from HTML response."""
    match = re.search(r'name="csrf_token"\s+type="hidden"\s+value="([^"]+)"', response_text)
    if not match:
        match = re.search(r'value="([^"]+)"\s+id="csrf_token"', response_text)
    return match.group(1) if match else None
