# tests/test_tasks.py
from datetime import date
from app.extensions import db
from app.models import Task, User, Workspace, WorkspaceMember


def login_user(client, email="member1@example.com", password="Password123!"):
    return client.post(
        "/login",
        data={"email": email, "password": password},
        follow_redirects=True,
    )


def test_auth_register_and_workspace_creation(client, app):
    """First user registers and automatically initializes the shared team workspace."""
    response = client.post(
        "/register",
        data={
            "full_name": "Sinh Viên 1",
            "email": "sv1@example.com",
            "password": "Password123!",
            "confirm_password": "Password123!",
            "invite_code": "CLOUDTASK-GROUP-8",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert "Đăng ký thành công" in response.get_data(as_text=True)

    with app.app_context():
        user = db.session.query(User).filter_by(email="sv1@example.com").first()
        assert user is not None
        assert user.check_password("Password123!") is True

        ws = db.session.query(Workspace).first()
        assert ws is not None
        membership = db.session.query(WorkspaceMember).filter_by(user_id=user.id).first()
        assert membership is not None
        assert membership.role == "admin"


def test_auth_duplicate_email_rejected(client, init_sample_data):
    """Registration with existing email must be rejected."""
    response = client.post(
        "/register",
        data={
            "full_name": "Trùng Email",
            "email": "member1@example.com",
            "password": "Password123!",
            "confirm_password": "Password123!",
            "invite_code": "CLOUDTASK-GROUP-8",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert "Email này đã được sử dụng" in response.get_data(as_text=True)


def test_auth_login_invalid_credentials(client, init_sample_data):
    """Login with wrong password must fail."""
    response = client.post(
        "/login",
        data={"email": "member1@example.com", "password": "WrongPassword"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert "Email hoặc mật khẩu không chính xác" in response.get_data(as_text=True)


def test_auth_login_logout_flow(client, init_sample_data):
    """Test successful login and subsequent logout."""
    login_res = login_user(client, "member1@example.com", "Password123!")
    assert login_res.status_code == 200
    assert "Chào mừng trở lại, Nguyễn Văn A" in login_res.get_data(as_text=True)

    logout_res = client.get("/logout", follow_redirects=True)
    assert logout_res.status_code == 200
    assert "đăng xuất thành công" in logout_res.get_data(as_text=True)


def test_protected_routes_require_login(client):
    """Unauthenticated users should be redirected to login."""
    routes = ["/", "/tasks", "/tasks/new", "/workspace"]
    for route in routes:
        response = client.get(route)
        assert response.status_code == 302
        assert "/login" in response.headers["Location"]


def test_shared_workspace_visibility_for_three_members(client, app, init_sample_data):
    """Three team members in the same workspace can all view and interact with the same task."""
    with app.app_context():
        # Add third member to workspace
        user3 = User(full_name="Lê Văn C", email="member3@example.com")
        user3.set_password("Password123!")
        db.session.add(user3)
        db.session.flush()

        ws = db.session.query(Workspace).first()
        db.session.add(WorkspaceMember(workspace_id=ws.id, user_id=user3.id, role="member"))
        db.session.commit()

    # Member 1 logs in and views task
    login_user(client, "member1@example.com", "Password123!")
    res1 = client.get("/tasks")
    assert res1.status_code == 200
    assert "Thiết lập hạ tầng PaaS Render" in res1.get_data(as_text=True)
    client.get("/logout")

    # Member 2 logs in and views the exact same task
    login_user(client, "member2@example.com", "Password123!")
    res2 = client.get("/tasks")
    assert res2.status_code == 200
    assert "Thiết lập hạ tầng PaaS Render" in res2.get_data(as_text=True)
    client.get("/logout")

    # Member 3 logs in and views the exact same task
    login_user(client, "member3@example.com", "Password123!")
    res3 = client.get("/tasks")
    assert res3.status_code == 200
    assert "Thiết lập hạ tầng PaaS Render" in res3.get_data(as_text=True)
    client.get("/logout")


def test_task_crud_operations(client, app, init_sample_data):
    """Test full CRUD: Create, Read, Update, Delete within shared workspace."""
    login_user(client, "member2@example.com", "Password123!")

    # 1. Create task
    create_res = client.post(
        "/tasks/new",
        data={
            "title": "Viết tài liệu IaaS",
            "description": "So sánh triển khai trên VM với PaaS Render",
            "status": "pending",
            "priority": "medium",
            "due_date": "2026-11-01",
        },
        follow_redirects=True,
    )
    assert create_res.status_code == 200
    assert "Đã thêm công việc mới" in create_res.get_data(as_text=True)

    with app.app_context():
        task = db.session.query(Task).filter_by(title="Viết tài liệu IaaS").first()
        assert task is not None
        task_id = task.id

    # 2. Read detail
    detail_res = client.get(f"/tasks/{task_id}")
    assert detail_res.status_code == 200
    assert "So sánh triển khai trên VM" in detail_res.get_data(as_text=True)

    # 3. Update task
    edit_res = client.post(
        f"/tasks/{task_id}/edit",
        data={
            "title": "Viết tài liệu IaaS và k6 script",
            "description": "Bổ sung kiểm thử tải bằng k6",
            "status": "completed",
            "priority": "high",
            "due_date": "2026-11-05",
        },
        follow_redirects=True,
    )
    assert edit_res.status_code == 200
    assert "Đã cập nhật công việc thành công" in edit_res.get_data(as_text=True)

    with app.app_context():
        updated_task = db.session.get(Task, task_id)
        assert updated_task.title == "Viết tài liệu IaaS và k6 script"
        assert updated_task.status == "completed"

    # 4. Delete task
    delete_res = client.post(f"/tasks/{task_id}/delete", follow_redirects=True)
    assert delete_res.status_code == 200
    assert "Đã xóa công việc" in delete_res.get_data(as_text=True)

    with app.app_context():
        assert db.session.get(Task, task_id) is None


def test_external_user_isolated_from_workspace(client, app, init_sample_data):
    """Users outside the workspace cannot view or delete tasks (403 Forbidden)."""
    with app.app_context():
        outsider = User(full_name="Người Ngoài Nhóm", email="outsider@example.com")
        outsider.set_password("Password123!")
        db.session.add(outsider)
        db.session.commit()
        outsider_id = outsider.id

    login_user(client, "outsider@example.com", "Password123!")
    task_id = init_sample_data["task_id"]

    # Access task detail of another workspace
    detail_res = client.get(f"/tasks/{task_id}")
    assert detail_res.status_code == 403

    # Attempt to delete task of another workspace
    delete_res = client.post(f"/tasks/{task_id}/delete")
    assert delete_res.status_code == 403
