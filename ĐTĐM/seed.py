# seed.py
import logging
from datetime import date, timedelta
from app import create_app
from app.extensions import db
from app.models import Task, User, Workspace, WorkspaceMember

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("seed")

app = create_app("development")

with app.app_context():
    logger.info("Checking database data...")

    # Find or create shared workspace
    ws = db.session.query(Workspace).first()
    if not ws:
        ws = Workspace(name="CloudTask Team 8")
        db.session.add(ws)
        db.session.flush()
        logger.info("Created shared workspace: CloudTask Team 8")

    # Accounts definition (Admin + Members/Employees)
    accounts_data = [
        {"name": "Quản Trị Viên", "email": "admin@cloudtask.com", "role": "admin"},
        {"name": "Nguyễn Văn A (Nhân viên Dev)", "email": "nhanvien1@cloudtask.com", "role": "member"},
        {"name": "Trần Thị B (Nhân viên QA)", "email": "nhanvien2@cloudtask.com", "role": "member"},
    ]

    users = []
    for acc in accounts_data:
        user = db.session.query(User).filter_by(email=acc["email"]).first()
        if not user:
            user = User(full_name=acc["name"], email=acc["email"])
            user.set_password("123456")
            db.session.add(user)
            db.session.flush()

            membership = WorkspaceMember(workspace_id=ws.id, user_id=user.id, role=acc["role"])
            db.session.add(membership)
            logger.info(f"Created account & membership: {acc['email']} ({acc['role']})")
        else:
            # Check membership if user exists
            membership = db.session.query(WorkspaceMember).filter_by(workspace_id=ws.id, user_id=user.id).first()
            if not membership:
                membership = WorkspaceMember(workspace_id=ws.id, user_id=user.id, role=acc["role"])
                db.session.add(membership)
                logger.info(f"Added existing user {acc['email']} to workspace as {acc['role']}")
        users.append(user)

    db.session.commit()
    user = users[0]  # default user for task creation

    # Initial demo tasks
    if db.session.query(Task).count() == 0:
        tasks_data = [
            {
                "title": "Tạo database trên Neon PostgreSQL và bàn giao",
                "description": "Tạo project cloudtask-db trên Neon, region Singapore, trích xuất DATABASE_URL an toàn.",
                "status": "completed",
                "priority": "high",
                "due_date": date.today() + timedelta(days=2),
                "created_by": user.id,
            },
            {
                "title": "Thiết lập Pipeline CI/CD trên GitHub Actions",
                "description": "Tự động hóa pytest, linting và database migration khi có PR hoặc push vào main.",
                "status": "in_progress",
                "priority": "high",
                "due_date": date.today() + timedelta(days=4),
                "created_by": user.id,
            },
            {
                "title": "Triển khai ứng dụng PaaS trên Render",
                "description": "Kết nối Neon PostgreSQL, cấu hình /health/ready và kiểm tra độ ổn định.",
                "status": "in_progress",
                "priority": "high",
                "due_date": date.today() + timedelta(days=5),
                "created_by": user.id,
            },
            {
                "title": "Triển khai ứng dụng IaaS trên Linux VM",
                "description": "Chạy Docker Compose trên Linux VM và kiểm tra khả năng phục hồi khi container restart.",
                "status": "pending",
                "priority": "medium",
                "due_date": date.today() + timedelta(days=7),
                "created_by": user.id,
            },
            {
                "title": "Thực hiện kiểm thử tải bằng k6 và so sánh hiệu năng",
                "description": "Đo p95 latency, error rate và ghi nhận số liệu so sánh giữa PaaS và IaaS.",
                "status": "pending",
                "priority": "medium",
                "due_date": date.today() + timedelta(days=10),
                "created_by": user.id,
            },
        ]

        for t in tasks_data:
            task = Task(workspace_id=ws.id, **t)
            db.session.add(task)

        db.session.commit()
        logger.info("Successfully seeded demo tasks into the shared workspace.")
    else:
        logger.info("Database already contains tasks. Seed skipped to preserve data.")
