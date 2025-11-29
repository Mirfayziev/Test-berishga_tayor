from datetime import datetime, timedelta, date
import os
import random

from flask import (
    Flask, render_template, redirect, url_for,
    request, flash, jsonify
)
from flask_sqlalchemy import SQLAlchemy
from flask_login import (
    LoginManager, login_user, login_required,
    logout_user, current_user, UserMixin
)
from werkzeug.security import generate_password_hash, check_password_hash

# =====================================
# Config
# =====================================

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-me')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///demo.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'pdf', 'doc', 'docx', 'xls', 'xlsx'}
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"

# =====================================
# Models
# =====================================

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="xodim")  # admin / rahbar / xodim
    is_active = db.Column(db.Boolean, default=True)

    tasks_created = db.relationship("Task", backref="creator", foreign_keys="Task.created_by_id")
    tasks_assigned = db.relationship("Task", backref="assignee", foreign_keys="Task.assigned_to_id")

    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), default="new")  # new / in_progress / review / done / overdue
    priority = db.Column(db.String(20), default="normal")  # low / normal / high / critical
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    due_date = db.Column(db.Date, nullable=True)

    created_by_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    assigned_to_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)


class SolarStat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    day = db.Column(db.Date, nullable=False, index=True)
    energy_kwh = db.Column(db.Float, nullable=False)


class EmployeeActivity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    day = db.Column(db.Date, nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    completed_tasks = db.Column(db.Integer, default=0)

# =====================================
# Login manager
# =====================================

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# =====================================
# Helpers / Demo data
# =====================================

def allowed_file(filename: str) -> bool:
    return '.' in filename and         filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


def init_demo_data():
    """Create demo admin, rahbar, xodim users and some stats if DB empty."""
    if User.query.count() > 0:
        return

    admin = User(full_name="Super Admin", email="admin@example.com", role="admin")
    admin.set_password("admin123")

    rahbar = User(full_name="Rahbar Bek", email="rahbar@example.com", role="rahbar")
    rahbar.set_password("rahbar123")

    xodim = User(full_name="Xodim Ali", email="xodim@example.com", role="xodim")
    xodim.set_password("xodim123")

    db.session.add_all([admin, rahbar, xodim])
    db.session.commit()

    # Tasks
    titles = [
        "Ombor inventarizatsiyasi",
        "Qurilish maydonini tekshirish",
        "Quyosh panellarini ko'rikdan o'tkazish",
        "Hisobotlarni tayyorlash",
        "Mehmonlarni kutib olish",
    ]
    statuses = ["new", "in_progress", "review", "done"]
    priorities = ["low", "normal", "high", "critical"]

    for i in range(25):
        t = Task(
            title=random.choice(titles),
            description="Demo topshiriq #" + str(i + 1),
            status=random.choice(statuses),
            priority=random.choice(priorities),
            created_by_id=rahbar.id,
            assigned_to_id=xodim.id,
            created_at=datetime.utcnow() - timedelta(days=random.randint(0, 20)),
            due_date=date.today() + timedelta(days=random.randint(-3, 10)),
        )
        db.session.add(t)

    # Solar stats - last 30 days
    today = date.today()
    for i in range(30):
        d = today - timedelta(days=29 - i)
        s = SolarStat(day=d, energy_kwh=round(random.uniform(50, 150), 2))
        db.session.add(s)

    # Employee activity
    for i in range(30):
        d = today - timedelta(days=29 - i)
        ea = EmployeeActivity(day=d, user_id=xodim.id, completed_tasks=random.randint(0, 7))
        db.session.add(ea)

    db.session.commit()
    print("Demo data initialized.")


def ai_suggest_assignee(task_title: str, task_description: str) -> str:
    """Very simple rule-based 'AI' suggestion – demo only."""
    text = f"{task_title} {task_description}".lower()
    if "quyosh" in text or "panel" in text or "solar" in text:
        return "Energetika bo'yicha mutaxassisga berish tavsiya etiladi."
    if "hisobot" in text or "report" in text:
        return "Analitik yoki buxgalter xodimga topshirish maqsadga muvofiq."
    if "mehmon" in text or "guest" in text:
        return "Reception / mehmonlarni kutib olish bo'limiga biriktirish mumkin."
    if "qurilish" in text:
        return "Qurilish bo'yicha injener yoki nazoratchiga topshirish kerak."
    return "Topshiriq mazmuniga qarab mos xodimni rahbar tanlashi tavsiya etiladi."


def ai_solar_forecast():
    """Make a tiny naive forecast for the next 7 days based on last 7-day average."""
    last_7 = SolarStat.query.order_by(SolarStat.day.desc()).limit(7).all()
    if not last_7:
        return []
    avg = sum(s.energy_kwh for s in last_7) / len(last_7)
    today = date.today()
    forecast = []
    for i in range(1, 8):
        d = today + timedelta(days=i)
        # +/- 10% noise
        val = round(avg * random.uniform(0.9, 1.1), 2)
        forecast.append({"day": d.isoformat(), "energy_kwh": val})
    return forecast

# =====================================
# Routes
# =====================================

@app.route("/")
@login_required
def index():
    # Dashboard stats
    total_tasks = Task.query.count()
    completed = Task.query.filter(Task.status == "done").count()
    in_progress = Task.query.filter(Task.status == "in_progress").count()
    overdue = Task.query.filter(Task.due_date < date.today(), Task.status != "done").count()

    # For cards
    recent_tasks = Task.query.order_by(Task.created_at.desc()).limit(5).all()

    return render_template(
        "dashboard.html",
        total_tasks=total_tasks,
        completed=completed,
        in_progress=in_progress,
        overdue=overdue,
        recent_tasks=recent_tasks,
    )


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("index"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user)
            flash("Muvaffaqiyatli tizimga kirdingiz.", "success")
            return redirect(url_for("index"))
        flash("Login yoki parol noto'g'ri.", "danger")
    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Tizimdan chiqdingiz.", "info")
    return redirect(url_for("login"))


@app.route("/tasks")
@login_required
def tasks_list():
    status = request.args.get("status")
    query = Task.query
    if status:
        query = query.filter_by(status=status)
    tasks = query.order_by(Task.created_at.desc()).all()
    users = User.query.all()
    return render_template("tasks.html", tasks=tasks, users=users, status=status)


@app.route("/tasks/create", methods=["POST"])
@login_required
def tasks_create():
    title = request.form.get("title")
    description = request.form.get("description")
    priority = request.form.get("priority", "normal")
    due_date_raw = request.form.get("due_date")
    assigned_to_id = request.form.get("assigned_to_id") or None

    due = None
    try:
        if due_date_raw:
            due = datetime.strptime(due_date_raw, "%Y-%m-%d").date()
    except ValueError:
        pass

    task = Task(
        title=title,
        description=description,
        priority=priority,
        created_by_id=current_user.id,
        assigned_to_id=int(assigned_to_id) if assigned_to_id else None,
        due_date=due,
        status="new",
    )
    db.session.add(task)
    db.session.commit()
    flash("Topshiriq yaratildi.", "success")
    return redirect(url_for("tasks_list"))


@app.route("/tasks/<int:task_id>/status", methods=["POST"])
@login_required
def tasks_update_status(task_id):
    task = Task.query.get_or_404(task_id)
    new_status = request.form.get("status")
    if new_status in {"new", "in_progress", "review", "done"}:
        task.status = new_status
        db.session.commit()
        flash("Holat yangilandi.", "success")
    else:
        flash("Noto'g'ri status.", "danger")
    return redirect(url_for("tasks_list"))


@app.route("/ijro")
@login_required
def ijro_board():
    # For demo: all tasks with due_date + indicator
    tasks = Task.query.order_by(Task.due_date.asc()).all()
    today = date.today()
    return render_template("ijro.html", tasks=tasks, today=today)


@app.route("/solar")
@login_required
def solar_page():
    stats = SolarStat.query.order_by(SolarStat.day.asc()).all()
    return render_template("solar.html", stats=stats)


@app.route("/activity")
@login_required
def activity_page():
    # We will build heatmap on client side
    return render_template("activity.html")


@app.route("/ai/task-suggest", methods=["POST"])
@login_required
def ai_task_suggest():
    data = request.get_json(force=True)
    title = data.get("title", "")
    description = data.get("description", "")
    suggestion = ai_suggest_assignee(title, description)
    return jsonify({"suggestion": suggestion})


@app.route("/api/dashboard-data")
@login_required
def api_dashboard_data():
    # For charts.js
    task_counts = {
        "new": Task.query.filter_by(status="new").count(),
        "in_progress": Task.query.filter_by(status="in_progress").count(),
        "review": Task.query.filter_by(status="review").count(),
        "done": Task.query.filter_by(status="done").count(),
    }

    solar_stats = SolarStat.query.order_by(SolarStat.day.asc()).all()
    solar = [{"day": s.day.isoformat(), "energy_kwh": s.energy_kwh} for s in solar_stats]
    forecast = ai_solar_forecast()

    # Employee activity
    activities = EmployeeActivity.query.order_by(EmployeeActivity.day.asc()).all()
    activity_data = [
        {"day": a.day.isoformat(), "user_id": a.user_id, "completed_tasks": a.completed_tasks}
        for a in activities
    ]

    return jsonify(
        {
            "task_counts": task_counts,
            "solar": solar,
            "solar_forecast": forecast,
            "activity": activity_data,
        }
    )


# Simple fake telegram webhook to avoid errors (demo)
@app.route("/telegram-webhook", methods=["POST"])
def telegram_webhook():
    # Demo: just return ok to avoid crashes if webhook called
    return "ok", 200


# =====================================
# CLI / init
# =====================================

@app.cli.command("init-demo")
def init_demo_command():
    """Initialize database and demo data."""
    db.create_all()
    init_demo_data()
    print("DB & demo data ready.")


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        init_demo_data()
    app.run(debug=True)
