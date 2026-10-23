# app/forms.py
from flask_wtf import FlaskForm
from wtforms import DateField, PasswordField, SelectField, StringField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional
from app.models import PRIORITY_LABELS, STATUS_LABELS


class RegisterForm(FlaskForm):
    full_name = StringField(
        "Họ và tên",
        validators=[
            DataRequired(message="Vui lòng nhập họ và tên."),
            Length(min=2, max=100, message="Họ và tên từ 2 đến 100 ký tự."),
        ],
    )
    email = StringField(
        "Email",
        validators=[
            DataRequired(message="Vui lòng nhập email."),
            Email(message="Địa chỉ email không hợp lệ."),
            Length(max=120, message="Email tối đa 120 ký tự."),
        ],
    )
    password = PasswordField(
        "Mật khẩu",
        validators=[
            DataRequired(message="Vui lòng nhập mật khẩu."),
            Length(min=6, message="Mật khẩu tối thiểu 6 ký tự."),
        ],
    )
    confirm_password = PasswordField(
        "Xác nhận mật khẩu",
        validators=[
            DataRequired(message="Vui lòng xác nhận mật khẩu."),
            EqualTo("password", message="Mật khẩu xác nhận không khớp."),
        ],
    )
    invite_code = StringField(
        "Mã mời Workspace (nếu có)",
        validators=[Optional(), Length(max=50)],
    )


class LoginForm(FlaskForm):
    email = StringField(
        "Email",
        validators=[
            DataRequired(message="Vui lòng nhập email."),
            Email(message="Địa chỉ email không hợp lệ."),
        ],
    )
    password = PasswordField(
        "Mật khẩu",
        validators=[DataRequired(message="Vui lòng nhập mật khẩu.")],
    )


class JoinWorkspaceForm(FlaskForm):
    invite_code = StringField(
        "Mã mời Workspace",
        validators=[
            DataRequired(message="Vui lòng nhập mã mời."),
            Length(max=50),
        ],
    )


class TaskForm(FlaskForm):
    title = StringField(
        "Tiêu đề",
        validators=[
            DataRequired(message="Tiêu đề không được để trống."),
            Length(max=150, message="Tiêu đề không được vượt quá 150 ký tự."),
        ],
    )
    description = TextAreaField(
        "Mô tả",
        validators=[Optional()],
    )
    status = SelectField(
        "Trạng thái",
        choices=[(key, val) for key, val in STATUS_LABELS.items()],
        default="pending",
        validators=[DataRequired(message="Vui lòng chọn trạng thái.")],
    )
    priority = SelectField(
        "Mức độ ưu tiên",
        choices=[(key, val) for key, val in PRIORITY_LABELS.items()],
        default="medium",
        validators=[DataRequired(message="Vui lòng chọn mức ưu tiên.")],
    )
    due_date = DateField(
        "Hạn hoàn thành",
        format="%Y-%m-%d",
        validators=[Optional()],
    )


class DeleteTaskForm(FlaskForm):
    """Empty form used exclusively for CSRF protection on POST deletes."""
    pass
