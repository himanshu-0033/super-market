from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from backend.models import Product, db
from sqlalchemy import func

inventory_bp = Blueprint('inventory', __name__)

def admin_required(f):
    """Restrict a route to Admin users only."""
    @wraps(f)
    @login_required
    def decorated(*args, **kwargs):
        if not current_user.is_admin():
            flash("Access denied. Admin privileges required.", "danger")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated

@inventory_bp.route("/inventory")
@admin_required
def inventory():
    search_query = request.args.get("q", "").strip()
    threshold = current_app.config.get("LOW_STOCK_THRESHOLD", 10)

    if search_query:
        products = Product.query.filter(
            (Product.name.ilike(f"%{search_query}%"))
            | (Product.barcode_id.ilike(f"%{search_query}%"))
        ).all()
    else:
        products = Product.query.all()

    return render_template("inventory.html", products=products, search_query=search_query, threshold=threshold)


@inventory_bp.route("/inventory/add", methods=["GET", "POST"])
@admin_required
def add_product():
    if request.method == "POST":
        name = request.form.get("name").strip()
        barcode_id = request.form.get("barcode_id").strip()
        price_str = request.form.get("price")
        stock_str = request.form.get("stock_quantity")
        category = request.form.get("category", "").strip()

        try:
            price = float(price_str)
            stock_quantity = int(stock_str)
        except ValueError:
            flash("Price must be a number and stock must be an integer.", "danger")
            return render_template("add_product.html")

        if Product.query.filter_by(barcode_id=barcode_id).first():
            flash(f"Barcode '{barcode_id}' already exists.", "danger")
            return render_template("add_product.html")

        product = Product(
            name=name,
            barcode_id=barcode_id,
            price=price,
            stock_quantity=stock_quantity,
            category=category,
        )
        db.session.add(product)
        db.session.commit()

        flash(f"Product '{name}' added successfully.", "success")
        return redirect(url_for("inventory.inventory"))

    return render_template("add_product.html")


@inventory_bp.route("/inventory/edit/<int:product_id>", methods=["GET", "POST"])
@admin_required
def edit_product(product_id):
    product = Product.query.get_or_404(product_id)

    if request.method == "POST":
        product.name = request.form.get("name").strip()
        product.barcode_id = request.form.get("barcode_id").strip()
        product.category = request.form.get("category", "").strip()
        
        try:
            product.price = float(request.form.get("price"))
            product.stock_quantity = int(request.form.get("stock_quantity"))
        except ValueError:
            flash("Invalid price or stock quantity.", "danger")
            return render_template("edit_product.html", product=product)

        # Check for duplicate barcode on another product
        existing = Product.query.filter(
            Product.barcode_id == product.barcode_id, Product.id != product.id
        ).first()
        if existing:
            flash("Another product is already using this barcode.", "danger")
            return render_template("edit_product.html", product=product)

        db.session.commit()
        flash(f"Product '{product.name}' updated.", "success")
        return redirect(url_for("inventory.inventory"))

    return render_template("edit_product.html", product=product)


@inventory_bp.route("/inventory/delete/<int:product_id>", methods=["POST"])
@admin_required
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    name = product.name
    
    # In a real app with historical data, you might want to "soft delete" 
    # instead of hard delete so you don't break old transaction records.
    # We are doing a hard delete here for simplicity.
    try:
        db.session.delete(product)
        db.session.commit()
        flash(f"Product '{name}' deleted.", "success")
    except Exception:
        db.session.rollback()
        flash(f"Cannot delete '{name}' because it is part of existing sales.", "danger")

    return redirect(url_for("inventory.inventory"))
