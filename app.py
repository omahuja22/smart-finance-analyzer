import os
import csv
import pickle
import statistics
from datetime import datetime
from flask import (
    Flask, render_template, redirect, url_for,
    request, flash, Response
)
from flask_login import (
    login_user, login_required, logout_user, current_user
)
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import func

from extensions import db, login_manager
from models import User, Expense, Budget
from ml.savings_predictor import predict_savings

# ---------------- PATH SETUP ----------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INSTANCE_DIR = os.path.join(BASE_DIR, "instance")
os.makedirs(INSTANCE_DIR, exist_ok=True)

DB_PATH = os.path.join(INSTANCE_DIR, "finance.db")
MODEL_PATH = os.path.join(BASE_DIR, "expense_model.pkl")

# ---------------- APP CONFIG ----------------
app = Flask(__name__)
app.config["SECRET_KEY"] = "super-secret-key"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + DB_PATH
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)
login_manager.init_app(app)
login_manager.login_view = "login"

# ---------------- LOAD ML MODEL ----------------
with open(MODEL_PATH, "rb") as f:
    model = pickle.load(f)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ---------------- CACHE FIX ----------------
@app.after_request
def no_cache(response):
    response.headers["Cache-Control"] = "no-store"
    return response

# ---------------- LANDING ----------------
@app.route("/")
def landing():
    return render_template("landing.html")

# ---------------- LOGIN ----------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        user = User.query.filter_by(email=request.form["email"]).first()
        if user and check_password_hash(user.password, request.form["password"]):
            login_user(user)
            return redirect(url_for("dashboard"))

    return render_template("login.html")

# ---------------- REGISTER ----------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        db.session.add(User(
            name=request.form["name"],
            email=request.form["email"],
            password=generate_password_hash(request.form["password"])
        ))
        db.session.commit()
        return redirect(url_for("login"))

    return render_template("register.html")

# ---------------- DASHBOARD ----------------
@app.route("/dashboard", methods=["GET", "POST"])
@login_required
def dashboard():
    alert_messages = []
    predicted_savings = None
    health_score = None

    # ---------- ADD EXPENSE ----------
    if request.method == "POST" and "description" in request.form:
        db.session.add(Expense(
            user_id=current_user.id,
            amount=float(request.form["amount"]),
            description=request.form["description"],
            category=model.predict([request.form["description"]])[0]
        ))
        db.session.commit()

    # ---------- SET BUDGET ----------
    if request.method == "POST" and "budget_category" in request.form:
        cat = request.form["budget_category"]
        limit = float(request.form["budget_limit"])

        b = Budget.query.filter_by(
            user_id=current_user.id,
            category=cat
        ).first()

        if b:
            b.limit = limit
        else:
            db.session.add(Budget(
                user_id=current_user.id,
                category=cat,
                limit=limit
            ))
        db.session.commit()

    # ---------- FETCH EXPENSES ----------
    expenses = Expense.query.filter_by(
        user_id=current_user.id
    ).order_by(Expense.date.desc()).all()

    amounts_only = [e.amount for e in expenses]
    total_spent = sum(amounts_only)

    # ---------- FINANCIAL SUMMARY ----------
    income_value = None
    savings_value = None
    savings_rate = None

    if request.method == "POST" and "income" in request.form:
        income_value = float(request.form["income"])
        savings_value = income_value - total_spent
        savings_rate = round(
            (savings_value / income_value) * 100, 2
        ) if income_value > 0 else 0

        predicted_savings, health_score = predict_savings(
            income_value, amounts_only
        )

    # ---------- ANOMALY DETECTION ----------
    IGNORE_ANOMALY_CATEGORIES = [
        "Savings", "Investments", "Insurance",
        "Rent", "EMI / Loans"
    ]

    if len(amounts_only) >= 3:
        mean = statistics.mean(amounts_only)
        std = statistics.stdev(amounts_only)

        for e in expenses:
            if e.category in IGNORE_ANOMALY_CATEGORIES:
                continue

            if e.amount > mean + 3 * std:
                alert_messages.append(
                    f"Spending spike detected: ₹{e.amount} in {e.category}. Please review."
                )

    # ---------- BUDGET USAGE (MONTHLY RESET) ----------
    current_month = datetime.now().strftime("%Y-%m")
    budget_usage = []

    budgets = Budget.query.filter_by(user_id=current_user.id).all()

    for b in budgets:
        spent = sum(
            e.amount for e in expenses
            if e.category == b.category and
            e.date.strftime("%Y-%m") == current_month
        )

        usage = round((spent / b.limit) * 100, 2) if b.limit > 0 else 0

        budget_usage.append({
            "id": b.id,
            "category": b.category,
            "spent": spent,
            "limit": b.limit,
            "usage": usage
        })

    # ---------- CHART DATA ----------
    category_data = db.session.query(
        Expense.category, func.sum(Expense.amount)
    ).filter_by(user_id=current_user.id).group_by(
        Expense.category
    ).all()

    daily_data = db.session.query(
        func.date(Expense.date), func.sum(Expense.amount)
    ).filter_by(user_id=current_user.id).group_by(
        func.date(Expense.date)
    ).all()

    monthly_data = db.session.query(
        func.strftime("%Y-%m", Expense.date),
        func.sum(Expense.amount)
    ).filter_by(user_id=current_user.id).group_by(
        func.strftime("%Y-%m", Expense.date)
    ).all()

    return render_template(
        "dashboard.html",
        expenses=expenses,
        categories=[c[0] for c in category_data],
        amounts=[float(c[1]) for c in category_data],
        daily_dates=[str(d[0]) for d in daily_data],
        daily_amounts=[float(d[1]) for d in daily_data],
        months=[m[0] for m in monthly_data],
        monthly_amounts=[float(m[1]) for m in monthly_data],
        total_spent=total_spent,
        income_value=income_value,
        savings_value=savings_value,
        savings_rate=savings_rate,
        predicted_savings=predicted_savings,
        health_score=health_score,
        budget_usage=budget_usage,
        alert_messages=alert_messages
    )

# ---------------- CLEAR ALL EXPENSES ----------------
@app.route("/clear-expenses", methods=["POST"])
@login_required
def clear_expenses():
    Expense.query.filter_by(user_id=current_user.id).delete()
    db.session.commit()
    flash("All expenses cleared successfully")
    return redirect(url_for("dashboard"))

# ---------------- CSV UPLOAD ----------------
@app.route("/upload-csv", methods=["POST"])
@login_required
def upload_csv():
    file = request.files.get("file")
    if not file:
        return redirect(url_for("dashboard"))

    rows = csv.DictReader(
        file.stream.read().decode("utf-8").splitlines()
    )
    count = 0

    for r in rows:
        try:
            db.session.add(Expense(
                user_id=current_user.id,
                amount=float(r["amount"]),
                description=r["description"],
                category=model.predict([r["description"]])[0]
            ))
            count += 1
        except:
            continue

    db.session.commit()
    flash(f"{count} expenses imported successfully")
    return redirect(url_for("dashboard"))

# ---------------- EXPORT CSV ----------------
@app.route("/export-expenses")
@login_required
def export_expenses():
    expenses = Expense.query.filter_by(
        user_id=current_user.id
    ).order_by(Expense.date.desc()).all()

    def generate():
        yield "date,description,category,amount\n"
        for e in expenses:
            yield f"{e.date},{e.description},{e.category},{e.amount}\n"

    return Response(
        generate(),
        mimetype="text/csv",
        headers={
            "Content-Disposition":
            "attachment;filename=expenses_report.csv"
        }
    )

# ---------------- DELETE BUDGET ----------------
@app.route("/delete-budget/<int:id>")
@login_required
def delete_budget(id):
    b = Budget.query.get_or_404(id)
    if b.user_id == current_user.id:
        db.session.delete(b)
        db.session.commit()
    return redirect(url_for("dashboard"))

# ---------------- DELETE EXPENSE ----------------
@app.route("/delete-expense/<int:id>")
@login_required
def delete_expense(id):
    e = Expense.query.get_or_404(id)
    if e.user_id == current_user.id:
        db.session.delete(e)
        db.session.commit()
    return redirect(url_for("dashboard"))

# ---------------- LOGOUT ----------------
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

# ---------------- RUN ----------------
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
