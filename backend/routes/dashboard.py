from datetime import date, datetime, timedelta
from functools import wraps
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from backend.models import Product, Transaction, TransactionItem, db
from sqlalchemy import func

dashboard_bp = Blueprint('dashboard', __name__)

def admin_required(f):
    @wraps(f)
    @login_required
    def decorated(*args, **kwargs):
        if not current_user.is_admin():
            flash("Access denied. Admin privileges required.", "danger")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated

@dashboard_bp.route("/dashboard")
@admin_required
def dashboard():
    today = date.today()
    
    # Calculate today's revenue
    todays_sales = db.session.query(func.sum(Transaction.total_amount)).filter(
        func.date(Transaction.timestamp) == today
    ).scalar() or 0.0

    # Calculate today's transactions
    todays_transactions = Transaction.query.filter(
        func.date(Transaction.timestamp) == today
    ).count()

    # Find low stock products
    threshold = current_app.config.get("LOW_STOCK_THRESHOLD", 10)
    low_stock = Product.query.filter(Product.stock_quantity <= threshold).order_by(Product.stock_quantity).all()

    return render_template(
        "dashboard.html",
        todays_sales=todays_sales,
        todays_transactions=todays_transactions,
        low_stock=low_stock,
        threshold=threshold
    )

@dashboard_bp.route("/api/sales_data")
@admin_required
def api_sales_data():
    """Return sales data for charts based on selected range (day, week, month, year)."""
    range_type = request.args.get('range', 'week')
    today = datetime.now().date()
    
    labels = []
    revenue = []

    if range_type == 'day':
        # Group by hour for today
        sales_by_hour = db.session.query(
            func.strftime('%H:00', Transaction.timestamp).label('hour'),
            func.sum(Transaction.total_amount).label('total')
        ).filter(
            func.date(Transaction.timestamp) == today
        ).group_by('hour').all()
        
        sales_dict = {row.hour: row.total for row in sales_by_hour}
        for i in range(9, 22): # Store hours 9AM to 9PM
            hour_str = f"{i:02d}:00"
            labels.append(hour_str)
            revenue.append(sales_dict.get(hour_str, 0))

    elif range_type == 'week':
        # Last 7 days
        for i in range(6, -1, -1):
            d = today - timedelta(days=i)
            labels.append(d.strftime("%a (%d %b)"))
            total = db.session.query(func.sum(Transaction.total_amount)).filter(
                func.date(Transaction.timestamp) == d
            ).scalar()
            revenue.append(total or 0.0)

    elif range_type == 'month':
        # Every 3rd day for the last 30 days to keep chart clean
        for i in range(29, -1, -3):
            d = today - timedelta(days=i)
            labels.append(d.strftime("%d %b"))
            
            # Sum for a 3-day window
            window_end = d + timedelta(days=2)
            total = db.session.query(func.sum(Transaction.total_amount)).filter(
                func.date(Transaction.timestamp) >= d,
                func.date(Transaction.timestamp) <= window_end
            ).scalar()
            revenue.append(total or 0.0)

    elif range_type == 'year':
        # Group by month for the last 12 months
        for i in range(11, -1, -1):
            target_date = today.replace(day=1) - timedelta(days=30*i)
            labels.append(target_date.strftime("%b %Y"))
            
            total = db.session.query(func.sum(Transaction.total_amount)).filter(
                func.strftime('%Y-%m', Transaction.timestamp) == target_date.strftime('%Y-%m')
            ).scalar()
            revenue.append(total or 0.0)
    else:
        return jsonify({"error": "Invalid range"}), 400

    return jsonify({
        "labels": labels,
        "revenue": revenue
    })

@dashboard_bp.route("/api/sales_share")
@admin_required
def api_sales_share():
    """Return top N products by quantity sold."""
    limit = int(request.args.get("limit", 5))
    
    # Sum up quantities per product
    top_items = (
        db.session.query(
            Product.name,
            func.sum(TransactionItem.quantity).label("total_qty")
        )
        .join(TransactionItem, TransactionItem.product_id == Product.id)
        .group_by(Product.id)
        .order_by(func.sum(TransactionItem.quantity).desc())
        .limit(limit)
        .all()
    )

    return jsonify({
        "labels": [item.name for item in top_items],
        "values": [item.total_qty for item in top_items]
    })

@dashboard_bp.route("/api/stock_vs_sold")
@admin_required
def api_stock_vs_sold():
    """Return available stock vs total units sold for each product."""
    products = (
        db.session.query(
            Product.name,
            Product.stock_quantity,
            func.coalesce(func.sum(TransactionItem.quantity), 0).label("total_sold"),
        )
        .outerjoin(TransactionItem, TransactionItem.product_id == Product.id)
        .group_by(Product.id, Product.name, Product.stock_quantity)
        .order_by(Product.name)
        .all()
    )

    return jsonify({
        "labels": [row.name for row in products],
        "available": [int(row.stock_quantity) for row in products],
        "sold": [int(row.total_sold) for row in products],
    })
