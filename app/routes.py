# app/routes.py
import functools
import logging

from flask import (
    Blueprint,
    abort,
    current_app,
    flash,
    g,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from sqlalchemy import func, or_, select, text

from app.extensions import db
from app.forms import DeleteTaskForm, JoinWorkspaceForm, LoginForm, RegisterForm, TaskForm
from app.models import Task, User, Workspace, WorkspaceMember

logger = logging.getLogger(__name__)

bp = Blueprint("main", __name__)


def login_required(view):
    """Decorator to protect routes requiring authentication."""
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.current_user is None:
            flash("Vui lòng đăng nhập để tiếp tục.", "warning")
            return redirect(url_for("main.login", next=request.path))
        return view(**kwargs)

    return wrapped_view


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get("user_id")
    if user_id is None:
        g.current_user = None
        g.current_workspace = None
    else:
        g.current_user = db.session.get(User, user_id)
        if g.current_user:
            membership = (
                db.session.query(WorkspaceMember)
                .filter_by(user_id=g.current_user.id)
                .order_by(WorkspaceMember.created_at.asc())
                .first()
            )
            g.current_workspace = membership.workspace if membership else None
        else:
            session.clear()
            g.current_workspace = None


@bp.context_processor
def inject_globals():
    return {
        "current_user": g.get("current_user"),
        "current_workspace": g.get("current_workspace"),
        "app_version": current_app.config.get("APP_VERSION", "v1.0.0"),
    }


# -------------------------------------------------------------
# Health Checks & Liveness
# -------------------------------------------------------------
@bp.route("/health/live")
def health_live():
    """Liveness probe: returns 200 if the web process is running."""
    return jsonify({
        "status": "healthy",
        "app_version": current_app.config.get("APP_VERSION", "v1.0.0"),
    }), 200


@bp.route("/health/ready")
def health_ready():
    """Readiness probe: checks database connectivity, returns 503 if unavailable."""
    try:
        db.session.execute(text("SELECT 1"))
        return jsonify({
            "status": "ready",
            "database": "connected",
            "app_version": current_app.config.get("APP_VERSION", "v1.0.0"),
        }), 200
    except Exception as exc:
        logger.error(f"Readiness check failed - Database error: {exc}")
        return jsonify({
            "status": "not_ready",
            "database": "disconnected",
            "error": "Database unreachable",
        }), 503


@bp.route("/health")
def health_legacy():
    """Backward compatibility health check endpoint."""
    return health_ready()


# -------------------------------------------------------------
# Authentication Routes
# -------------------------------------------------------------
@bp.route("/register", methods=["GET", "POST"])
def register():
    if g.current_user:
        return redirect(url_for("main.dashboard"))

    form = RegisterForm()
    if form.validate_on_submit():
        clean_email = form.email.data.strip().lower()
        existing_user = db.session.query(User).filter_by(email=clean_email).first()
        if existing_user:
            flash("Email này đã được sử dụng. Vui lòng đăng nhập hoặc dùng email khác.", "error")
            return render_template("auth/register.html", form=form)

        # Create new user
        new_user = User(
            full_name=form.full_name.data.strip(),
            email=clean_email,
        )
        new_user.set_password(form.password.data)
        db.session.add(new_user)
        db.session.flush()

        expected_invite = current_app.config.get("GROUP_INVITE_CODE", "CLOUDTASK-GROUP-8")
        input_invite = (form.invite_code.data or "").strip()

        # Check existing primary workspace
        primary_workspace = db.session.query(Workspace).order_by(Workspace.id.asc()).first()

        session.clear()
        session["user_id"] = new_user.id

        if not primary_workspace:
            # First user becomes admin of newly created team workspace
            primary_workspace = Workspace(name="CloudTask Team 8")
            db.session.add(primary_workspace)
            db.session.flush()
            membership = WorkspaceMember(
                workspace_id=primary_workspace.id, user_id=new_user.id, role="admin"
            )
            db.session.add(membership)
            db.session.commit()
            flash("Đăng ký thành công! Bạn là quản trị viên của workspace chung.", "success")
        else:
            # Workspace exists: require valid GROUP_INVITE_CODE to join shared workspace
            if input_invite and input_invite == expected_invite:
                membership = WorkspaceMember(
                    workspace_id=primary_workspace.id, user_id=new_user.id, role="member"
                )
                db.session.add(membership)
                db.session.commit()
                flash("Đăng ký thành công và đã tham gia workspace chung!", "success")
            else:
                db.session.commit()
                flash(
                    "Đăng ký tài khoản thành công nhưng mã mời chưa đúng để vào nhóm chung.",
                    "warning",
                )

        return redirect(url_for("main.dashboard"))

    return render_template("auth/register.html", form=form)


@bp.route("/login", methods=["GET", "POST"])
def login():
    if g.current_user:
        return redirect(url_for("main.dashboard"))

    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data.strip().lower()
        user = db.session.query(User).filter_by(email=email).first()

        if user and user.check_password(form.password.data):
            session.clear()
            session["user_id"] = user.id
            flash(f"Chào mừng trở lại, {user.full_name}!", "success")
            next_page = request.args.get("next")
            if next_page and next_page.startswith("/"):
                return redirect(next_page)
            return redirect(url_for("main.dashboard"))

        flash("Email hoặc mật khẩu không chính xác.", "error")

    return render_template("auth/login.html", form=form)


@bp.route("/logout")
def logout():
    session.clear()
    flash("Bạn đã đăng xuất thành công.", "info")
    return redirect(url_for("main.login"))


# -------------------------------------------------------------
# Workspace & Profile Routes
# -------------------------------------------------------------
@bp.route("/workspace")
@login_required
def workspace_info():
    if not g.current_workspace:
        form = JoinWorkspaceForm()
        return render_template("workspace.html", form=form, members=[])

    members = (
        db.session.query(WorkspaceMember)
        .filter_by(workspace_id=g.current_workspace.id)
        .all()
    )
    form = JoinWorkspaceForm()
    return render_template(
        "workspace.html",
        workspace=g.current_workspace,
        members=members,
        form=form,
    )


@bp.route("/workspace/join", methods=["POST"])
@login_required
def join_workspace():
    form = JoinWorkspaceForm()
    if form.validate_on_submit():
        expected_invite = current_app.config.get("GROUP_INVITE_CODE", "CLOUDTASK-GROUP-8")
        if form.invite_code.data.strip() == expected_invite:
            primary_ws = db.session.query(Workspace).order_by(Workspace.id.asc()).first()
            if not primary_ws:
                primary_ws = Workspace(name="CloudTask Team 8")
                db.session.add(primary_ws)
                db.session.flush()

            existing_member = (
                db.session.query(WorkspaceMember)
                .filter_by(workspace_id=primary_ws.id, user_id=g.current_user.id)
                .first()
            )
            if not existing_member:
                db.session.add(
                    WorkspaceMember(
                        workspace_id=primary_ws.id, user_id=g.current_user.id, role="member"
                    )
                )
                db.session.commit()
                flash("Tham gia workspace thành công!", "success")
            else:
                flash("Bạn đã là thành viên của workspace này.", "info")
        else:
            flash("Mã mời không chính xác.", "error")

    return redirect(url_for("main.workspace_info"))


# -------------------------------------------------------------
# Dashboard & Task CRUD
# -------------------------------------------------------------
@bp.route("/")
@login_required
def dashboard():
    if not g.current_workspace:
        return redirect(url_for("main.workspace_info"))

    ws_id = g.current_workspace.id
    total_count = (
        db.session.scalar(select(func.count(Task.id)).where(Task.workspace_id == ws_id)) or 0
    )
    pending_count = (
        db.session.scalar(
            select(func.count(Task.id)).where(Task.workspace_id == ws_id, Task.status == "pending")
        )
        or 0
    )
    in_progress_count = (
        db.session.scalar(
            select(func.count(Task.id)).where(
                Task.workspace_id == ws_id, Task.status == "in_progress"
            )
        )
        or 0
    )
    completed_count = (
        db.session.scalar(
            select(func.count(Task.id)).where(
                Task.workspace_id == ws_id, Task.status == "completed"
            )
        )
        or 0
    )

    recent_tasks_query = (
        select(Task)
        .where(Task.workspace_id == ws_id)
        .order_by(Task.created_at.desc())
        .limit(5)
    )
    recent_tasks = db.session.scalars(recent_tasks_query).all()

    return render_template(
        "dashboard.html",
        total_count=total_count,
        pending_count=pending_count,
        in_progress_count=in_progress_count,
        completed_count=completed_count,
        recent_tasks=recent_tasks,
    )


@bp.route("/tasks")
@login_required
def task_list():
    if not g.current_workspace:
        return redirect(url_for("main.workspace_info"))

    ws_id = g.current_workspace.id
    page = request.args.get("page", 1, type=int)
    status_filter = request.args.get("status", "", type=str).strip()
    priority_filter = request.args.get("priority", "", type=str).strip()
    search_query = request.args.get("q", "", type=str).strip()

    stmt = select(Task).where(Task.workspace_id == ws_id)

    if status_filter in ["pending", "in_progress", "completed"]:
        stmt = stmt.where(Task.status == status_filter)

    if priority_filter in ["low", "medium", "high"]:
        stmt = stmt.where(Task.priority == priority_filter)

    if search_query:
        stmt = stmt.where(
            or_(
                Task.title.ilike(f"%{search_query}%"),
                Task.description.ilike(f"%{search_query}%"),
            )
        )

    stmt = stmt.order_by(Task.created_at.desc())
    pagination = db.paginate(stmt, page=page, per_page=10, error_out=False)
    delete_form = DeleteTaskForm()

    return render_template(
        "tasks/list.html",
        pagination=pagination,
        tasks=pagination.items,
        status_filter=status_filter,
        priority_filter=priority_filter,
        search_query=search_query,
        delete_form=delete_form,
    )


@bp.route("/tasks/new", methods=["GET", "POST"])
@login_required
def task_create():
    if not g.current_workspace:
        flash("Bạn cần tham gia workspace trước khi tạo công việc.", "warning")
        return redirect(url_for("main.workspace_info"))

    form = TaskForm()
    if form.validate_on_submit():
        task = Task(
            workspace_id=g.current_workspace.id,
            created_by=g.current_user.id,
            title=form.title.data.strip(),
            description=form.description.data.strip() if form.description.data else None,
            status=form.status.data,
            priority=form.priority.data,
            due_date=form.due_date.data,
        )
        db.session.add(task)
        db.session.commit()
        flash("Đã thêm công việc mới vào workspace chung.", "success")
        return redirect(url_for("main.task_list"))

    return render_template("tasks/form.html", form=form, is_edit=False)


@bp.route("/tasks/<int:id>")
@login_required
def task_detail(id: int):
    task = db.session.get(Task, id)
    if not task:
        abort(404)

    # Server-side workspace isolation
    if not g.current_workspace or task.workspace_id != g.current_workspace.id:
        abort(403)

    delete_form = DeleteTaskForm()
    return render_template("tasks/detail.html", task=task, delete_form=delete_form)


@bp.route("/tasks/<int:id>/edit", methods=["GET", "POST"])
@login_required
def task_edit(id: int):
    task = db.session.get(Task, id)
    if not task:
        abort(404)

    if not g.current_workspace or task.workspace_id != g.current_workspace.id:
        abort(403)

    form = TaskForm(obj=task)
    if form.validate_on_submit():
        task.title = form.title.data.strip()
        task.description = form.description.data.strip() if form.description.data else None
        task.status = form.status.data
        task.priority = form.priority.data
        task.due_date = form.due_date.data

        db.session.commit()
        flash("Đã cập nhật công việc thành công.", "success")
        return redirect(url_for("main.task_detail", id=task.id))

    return render_template("tasks/form.html", form=form, is_edit=True, task=task)


@bp.route("/tasks/<int:id>/delete", methods=["POST"])
@login_required
def task_delete(id: int):
    task = db.session.get(Task, id)
    if not task:
        abort(404)

    if not g.current_workspace or task.workspace_id != g.current_workspace.id:
        abort(403)

    form = DeleteTaskForm()
    if not form.validate_on_submit():
        flash("Yêu cầu không hợp lệ (lỗi bảo vệ CSRF).", "error")
        return redirect(url_for("main.task_list"))

    db.session.delete(task)
    db.session.commit()
    flash("Đã xóa công việc khỏi workspace.", "success")
    return redirect(url_for("main.task_list"))
