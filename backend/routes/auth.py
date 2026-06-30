from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from backend.models import User, db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        if current_user.is_admin():
            return redirect(url_for("dashboard.dashboard"))
        return redirect(url_for("pos.pos"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user)
            flash(f"Welcome back, {user.username}!", "success")
            next_page = request.args.get("next")
            if next_page:
                return redirect(next_page)
            if user.is_admin():
                return redirect(url_for("dashboard.dashboard"))
            return redirect(url_for("pos.pos"))

        flash("Invalid username or password.", "danger")

    return render_template("login.html")


@auth_bp.route("/signup", methods=["GET", "POST"])
def signup():
    if current_user.is_authenticated:
        if current_user.is_admin():
            return redirect(url_for("dashboard.dashboard"))
        return redirect(url_for("pos.pos"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        role = request.form.get("role", "cashier")

        # Validation
        if not username or not password:
            flash("Username and password are required.", "danger")
            return render_template("signup.html")

        if len(password) < 4:
            flash("Password must be at least 4 characters.", "danger")
            return render_template("signup.html")

        if role not in ("admin", "cashier"):
            role = "cashier"

        # Check uniqueness
        if User.query.filter_by(username=username).first():
            flash("Username already taken.", "danger")
            return render_template("signup.html")

        user = User(username=username, role=role)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        login_user(user)
        flash(f"Account created! Welcome, {user.username}.", "success")
        if user.is_admin():
            return redirect(url_for("dashboard.dashboard"))
        return redirect(url_for("pos.pos"))

    return render_template("signup.html")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))
