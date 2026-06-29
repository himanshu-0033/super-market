"""
RetailPOS — Flask Point of Sale Application
=============================================
Main application file containing all routes:
- Authentication (login, signup, logout)
- Inventory Management (CRUD — Admin only)
- Point of Sale / Checkout (Cashier)
- Dashboard & Analytics (Admin)
"""

from datetime import date, datetime, timedelta
from functools import wraps

from flask import (
    Flask,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import (
    LoginManager,
    current_user,
    login_required,
    login_user,
    logout_user,
)
from sqlalchemy import func

from config import Config
from models import Product, Transaction, TransactionItem, User, db

# ─── App Factory ─────────────────────────────────────────────
app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
login_manager.login_message_category = "warning"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# ─── Role Decorators ────────────────────────────────────────

def admin_required(f):
    """Restrict a route to Admin users only."""

    @wraps(f)
    @login_required
    def decorated(*args, **kwargs):
        if not current_user.is_admin():
            flash("Access denied. Admin privileges required.", "danger")
            return redirect(url_for("login"))
        return f(*args, **kwargs)

    return decorated


def cashier_required(f):
    """Restrict a route to Cashier users only."""

    @wraps(f)
    @login_required
    def decorated(*args, **kwargs):
        if current_user.role != "cashier":
            flash("Access denied. Cashier role required.", "danger")
            return redirect(url_for("login"))
        return f(*args, **kwargs)

    return decorated


# ═══════════════════════════════════════════════════════════════
#  PHASE 3A — Authentication Routes
# ═══════════════════════════════════════════════════════════════


@app.route("/")
def index():
    """Redirect to role-appropriate landing page."""
    if current_user.is_authenticated:
        if current_user.is_admin():
            return redirect(url_for("dashboard"))
        return redirect(url_for("pos"))
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("index"))

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
            return redirect(url_for("index"))

        flash("Invalid username or password.", "danger")

    return render_template("login.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for("index"))

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
        return redirect(url_for("index"))

    return render_template("signup.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("login"))


# ═══════════════════════════════════════════════════════════════
#  PHASE 3B — Inventory Management (Admin Only)
# ═══════════════════════════════════════════════════════════════


@app.route("/inventory")
@admin_required
def inventory():
    search_query = request.args.get("q", "").strip()
    threshold = Config.LOW_STOCK_THRESHOLD

    if search_query:
        products = Product.query.filter(
            (Product.name.ilike(f"%{search_query}%"))
            | (Product.barcode_id.ilike(f"%{search_query}%"))
        ).all()
    else:
        products = Product.query.order_by(Product.name).all()

    return render_template(
        "inventory.html",
        products=products,
        search_query=search_query,
        threshold=threshold,
    )


@app.route("/add_product", methods=["GET", "POST"])
@admin_required
def add_product():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        barcode_id = request.form.get("barcode_id", "").strip()
        category = request.form.get("category", "").strip() or None
        price = request.form.get("price", type=float)
        stock_quantity = request.form.get("stock_quantity", type=int, default=0)

        # Validation
        if not name or not barcode_id or price is None:
            flash("Name, barcode, and price are required.", "danger")
            return render_template("add_product.html")

        if Product.query.filter_by(barcode_id=barcode_id).first():
            flash("A product with this barcode already exists.", "danger")
            return render_template("add_product.html")

        product = Product(
            name=name,
            barcode_id=barcode_id,
            category=category,
            price=price,
            stock_quantity=stock_quantity,
        )
        db.session.add(product)
        db.session.commit()

        flash(f"Product '{name}' added successfully.", "success")
        return redirect(url_for("inventory"))

    return render_template("add_product.html")


@app.route("/edit_product/<int:product_id>", methods=["GET", "POST"])
@admin_required
def edit_product(product_id):
    product = Product.query.get_or_404(product_id)

    if request.method == "POST":
        product.name = request.form.get("name", "").strip()
        product.barcode_id = request.form.get("barcode_id", "").strip()
        product.category = request.form.get("category", "").strip() or None
        product.price = request.form.get("price", type=float)
        product.stock_quantity = request.form.get("stock_quantity", type=int, default=0)

        # Check barcode uniqueness (excluding self)
        existing = Product.query.filter(
            Product.barcode_id == product.barcode_id,
            Product.id != product.id,
        ).first()
        if existing:
            flash("Another product with this barcode already exists.", "danger")
            return render_template("edit_product.html", product=product)

        db.session.commit()
        flash(f"Product '{product.name}' updated.", "success")
        return redirect(url_for("inventory"))

    return render_template("edit_product.html", product=product)


@app.route("/delete_product/<int:product_id>", methods=["POST"])
@admin_required
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    name = product.name
    db.session.delete(product)
    db.session.commit()
    flash(f"Product '{name}' deleted.", "success")
    return redirect(url_for("inventory"))


# ═══════════════════════════════════════════════════════════════
#  PHASE 3C — Point of Sale / Checkout (Cashier)
# ═══════════════════════════════════════════════════════════════


@app.route("/pos")
@cashier_required
def pos():
    products = Product.query.filter(Product.stock_quantity > 0).order_by(Product.name).all()
    return render_template("pos.html", products=products)


@app.route("/checkout", methods=["POST"])
@cashier_required
def checkout():
    """
    Process a cart checkout.

    Expects JSON: { "items": [{ "product_id": int, "quantity": int }, ...] }

    Steps:
    1. Validate each item has sufficient stock.
    2. Create a Transaction record.
    3. Create TransactionItem records (snapshot price_at_checkout).
    4. Deduct stock_quantity from each Product.
    5. Return transaction summary.
    """
    data = request.get_json()
    if not data or not data.get("items"):
        return jsonify({"success": False, "error": "No items provided."}), 400

    cart_items = data["items"]
    total_amount = 0.0
    line_items = []

    # Validate all items first
    for item in cart_items:
        product_id = item.get("product_id")
        quantity = item.get("quantity", 0)

        if not product_id or quantity <= 0:
            return jsonify({"success": False, "error": "Invalid cart item."}), 400

        product = Product.query.get(product_id)
        if not product:
            return jsonify(
                {"success": False, "error": f"Product ID {product_id} not found."}
            ), 404

        if product.stock_quantity < quantity:
            return jsonify(
                {
                    "success": False,
                    "error": f"Insufficient stock for '{product.name}'. "
                    f"Available: {product.stock_quantity}, Requested: {quantity}.",
                }
            ), 400

        line_total = product.price * quantity
        total_amount += line_total
        line_items.append(
            {
                "product": product,
                "quantity": quantity,
                "price_at_checkout": product.price,
                "line_total": line_total,
            }
        )

    # All validated — commit the transaction atomically
    transaction = Transaction(
        total_amount=total_amount,
        cashier_id=current_user.id,
    )
    db.session.add(transaction)
    db.session.flush()  # Get the transaction.id

    response_items = []

    for item in line_items:
        # Create TransactionItem
        txn_item = TransactionItem(
            transaction_id=transaction.id,
            product_id=item["product"].id,
            quantity=item["quantity"],
            price_at_checkout=item["price_at_checkout"],
        )
        db.session.add(txn_item)

        # Deduct stock
        item["product"].stock_quantity -= item["quantity"]

        response_items.append(
            {
                "product_id": item["product"].id,
                "name": item["product"].name,
                "quantity": item["quantity"],
                "price": item["price_at_checkout"],
                "line_total": item["line_total"],
            }
        )

    db.session.commit()

    return jsonify(
        {
            "success": True,
            "transaction_id": transaction.id,
            "total": total_amount,
            "items": response_items,
        }
    )


# ═══════════════════════════════════════════════════════════════
#  PHASE 4 — Dashboard & Analytics (Admin)
# ═══════════════════════════════════════════════════════════════


@app.route("/dashboard")
@admin_required
def dashboard():
    threshold = Config.LOW_STOCK_THRESHOLD
    today = date.today()

    # ── Today's stats ────────────────────────────────────────
    today_revenue = (
        db.session.query(func.coalesce(func.sum(Transaction.total_amount), 0))
        .filter(func.date(Transaction.timestamp) == today)
        .scalar()
    )

    today_transactions = (
        db.session.query(func.count(Transaction.id))
        .filter(func.date(Transaction.timestamp) == today)
        .scalar()
    )

    total_products = Product.query.count()

    # ── Low stock alerts ─────────────────────────────────────
    low_stock_products = (
        Product.query.filter(Product.stock_quantity < threshold)
        .order_by(Product.stock_quantity.asc())
        .all()
    )
    low_stock_count = len(low_stock_products)

    # ── Daily revenue (last 7 days) ──────────────────────────
    seven_days_ago = today - timedelta(days=6)

    daily_revenue = (
        db.session.query(
            func.date(Transaction.timestamp).label("day"),
            func.sum(Transaction.total_amount).label("revenue"),
        )
        .filter(func.date(Transaction.timestamp) >= seven_days_ago)
        .group_by(func.date(Transaction.timestamp))
        .order_by(func.date(Transaction.timestamp))
        .all()
    )

    # Build full 7-day list (fill in zeros for missing days)
    revenue_map = {str(row.day): float(row.revenue) for row in daily_revenue}
    daily_labels = []
    daily_values = []
    for i in range(7):
        d = seven_days_ago + timedelta(days=i)
        label = d.strftime("%b %d")
        daily_labels.append(label)
        daily_values.append(revenue_map.get(str(d), 0))

    # ── Top selling products (top 10 by qty) ─────────────────
    top_products = (
        db.session.query(
            Product.name,
            func.sum(TransactionItem.quantity).label("total_qty"),
        )
        .join(TransactionItem, TransactionItem.product_id == Product.id)
        .group_by(Product.id, Product.name)
        .order_by(func.sum(TransactionItem.quantity).desc())
        .limit(10)
        .all()
    )

    top_labels = [row.name for row in top_products]
    top_values = [int(row.total_qty) for row in top_products]

    return render_template(
        "dashboard.html",
        today_revenue=today_revenue,
        today_transactions=today_transactions,
        total_products=total_products,
        low_stock_count=low_stock_count,
        low_stock_products=low_stock_products,
        threshold=threshold,
        daily_labels=daily_labels,
        daily_values=daily_values,
        top_labels=top_labels,
        top_values=top_values,
    )


# ═══════════════════════════════════════════════════════════════
#  API — Product Search (AJAX for POS)
# ═══════════════════════════════════════════════════════════════


@app.route("/api/search_products")
@login_required
def api_search_products():
    q = request.args.get("q", "").strip()
    if not q:
        products = Product.query.filter(Product.stock_quantity > 0).all()
    else:
        products = Product.query.filter(
            (Product.name.ilike(f"%{q}%")) | (Product.barcode_id.ilike(f"%{q}%")),
            Product.stock_quantity > 0,
        ).all()

    return jsonify(
        [
            {
                "id": p.id,
                "name": p.name,
                "barcode_id": p.barcode_id,
                "price": p.price,
                "stock_quantity": p.stock_quantity,
                "category": p.category,
            }
            for p in products
        ]
    )


# ═══════════════════════════════════════════════════════════════
#  Bootstrap
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        print("[OK] Database tables created.")
    app.run(debug=True)
