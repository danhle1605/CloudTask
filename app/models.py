# app/models.py
from datetime import date, datetime, timezone

from sqlalchemy import CheckConstraint, Date, DateTime, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from werkzeug.security import check_password_hash, generate_password_hash

from app.extensions import db

STATUS_LABELS = {
    "pending": "Chờ xử lý",
    "in_progress": "Đang thực hiện",
    "completed": "Đã hoàn thành",
}

PRIORITY_LABELS = {
    "low": "Thấp",
    "medium": "Trung bình",
    "high": "Cao",
}


class User(db.Model):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    full_name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    workspace_memberships = relationship(
        "WorkspaceMember", back_populates="user", cascade="all, delete-orphan"
    )
    tasks = relationship("Task", back_populates="creator")

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    def __repr__(self) -> str:
        return f"<User {self.id}: {self.email}>"


class Workspace(db.Model):
    __tablename__ = "workspaces"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    members = relationship(
        "WorkspaceMember", back_populates="workspace", cascade="all, delete-orphan"
    )
    tasks = relationship("Task", back_populates="workspace", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Workspace {self.id}: {self.name}>"


class WorkspaceMember(db.Model):
    __tablename__ = "workspace_members"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    workspace_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    role: Mapped[str] = mapped_column(String(20), nullable=False, default="member")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    workspace = relationship("Workspace", back_populates="members")
    user = relationship("User", back_populates="workspace_memberships")

    __table_args__ = (
        Index("ix_workspace_member_unique", "workspace_id", "user_id", unique=True),
    )

    def __repr__(self) -> str:
        return f"<WorkspaceMember ws={self.workspace_id} user={self.user_id} role={self.role}>"


class Task(db.Model):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    workspace_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False
    )
    created_by: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    title: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="pending",
    )
    priority: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="medium",
    )
    due_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    workspace = relationship("Workspace", back_populates="tasks")
    creator = relationship("User", back_populates="tasks")

    __table_args__ = (
        CheckConstraint(
            "status IN ('pending', 'in_progress', 'completed')",
            name="ck_tasks_status",
        ),
        CheckConstraint(
            "priority IN ('low', 'medium', 'high')",
            name="ck_tasks_priority",
        ),
        Index("ix_tasks_workspace_id", "workspace_id"),
        Index("ix_tasks_status", "status"),
        Index("ix_tasks_priority", "priority"),
        Index("ix_tasks_due_date", "due_date"),
    )

    @property
    def status_label(self) -> str:
        return STATUS_LABELS.get(self.status, self.status)

    @property
    def priority_label(self) -> str:
        return PRIORITY_LABELS.get(self.priority, self.priority)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "workspace_id": self.workspace_id,
            "created_by": self.created_by,
            "creator_name": self.creator.full_name if self.creator else "Không xác định",
            "title": self.title,
            "description": self.description,
            "status": self.status,
            "status_label": self.status_label,
            "priority": self.priority,
            "priority_label": self.priority_label,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self) -> str:
        return f"<Task {self.id}: {self.title}>"
