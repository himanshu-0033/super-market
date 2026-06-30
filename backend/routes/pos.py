from functools import wraps
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
from backend.models import Product, Transaction, TransactionItem, db

pos_bp = Blueprint('pos', __name__)

def cashier_required(f):
    """Restrict a route to Cashier users only."""
    @wraps(f)
    @login_required
    def decorated(*args, **kwargs):
        if current_user.role != "cashier":
            flash("Access denied. Cashier role required.", "danger")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated

@pos_bp.route("/pos")
@cashier_required
def pos():
    return render_template("pos.html")


@pos_bp.route("/api/products")
@login_required
def api_products():
    """Returns product list as JSON for the POS frontend."""
    search = request.args.get("q", "").strip()
    if search:
        products = Product.query.filter(
            (Product.name.ilike(f"%{search}%")) | (Product.barcode_id.ilike(f"%{search}%"))
        ).all()
    else:
        products = Product.query.all()
    
    return jsonify([{
        "id": p.id,
        "name": p.name,
        "barcode_id": p.barcode_id,
        "price": p.price,
        "stock": p.stock_quantity,
    } for p in products])


@pos_bp.route("/api/checkout", methods=["POST"])
@cashier_required
def api_checkout():
    """Handles checkout: verifies stock, deducts inventory, creates transaction."""
    data = request.get_json()
    items = data.get("items", [])

    if not items:
        return jsonify({"success": False, "message": "Cart is empty"}), 400

    total_amount = 0.0
    transaction_items = []

    # Verify stock and calculate totals
    for item in items:
        product_id = item.get("id")
        qty = item.get("qty", 0)

        if qty <= 0:
            return jsonify({"success": False, "message": "Invalid quantity"}), 400

        product = Product.query.get(product_id)
        if not product:
            return jsonify({"success": False, "message": f"Product {product_id} not found"}), 404

        if product.stock_quantity < qty:
            return jsonify({
                "success": False, 
                "message": f"Not enough stock for {product.name} (only {product.stock_quantity} left)"
            }), 400

        total_amount += product.price * qty

        # Prepare line item
        t_item = TransactionItem(
            product_id=product.id,
            quantity=qty,
            price_at_checkout=product.price
        )
        transaction_items.append((product, t_item, qty))

    # All checks passed — commit transaction
    try:
        new_tx = Transaction(
            total_amount=total_amount,
            cashier_id=current_user.id
        )
        db.session.add(new_tx)
        db.session.flush() # Get the new transaction ID

        for product, t_item, qty in transaction_items:
            product.stock_quantity -= qty
            t_item.transaction_id = new_tx.id
            db.session.add(t_item)

        db.session.commit()
        return jsonify({"success": True, "transaction_id": new_tx.id})

    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500
