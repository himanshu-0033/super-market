from datetime import datetime

from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash

db = SQLAlchemy()


class User(UserMixin, db.Model):
    """Application user — either Admin (manager) or Cashier."""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="cashier")  # 'admin' | 'cashier'

    # Relationship
    transactions = db.relationship("Transaction", backref="cashier", lazy=True)

    def set_password(self, password):
        """Hash and store the password. Never store plain-text."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verify a plain-text password against the stored hash."""
        return check_password_hash(self.password_hash, password)

    def is_admin(self):
        """Check if the user has the Admin role."""
        return self.role == "admin"

    def __repr__(self):
        return f"<User {self.username} ({self.role})>"


class Product(db.Model):
    """A product in the store inventory."""

    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    barcode_id = db.Column(db.String(50), unique=True, nullable=False)
    price = db.Column(db.Float, nullable=False)
    stock_quantity = db.Column(db.Integer, nullable=False, default=0)
    category = db.Column(db.String(50), nullable=True)

    # Relationship
    transaction_items = db.relationship("TransactionItem", backref="product", lazy=True)

    def __repr__(self):
        return f"<Product {self.name} (stock: {self.stock_quantity})>"


class Transaction(db.Model):
    """A completed sales transaction processed by a cashier."""

    __tablename__ = "transactions"

    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    total_amount = db.Column(db.Float, nullable=False)
    cashier_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    # Relationship
    items = db.relationship("TransactionItem", backref="transaction", lazy=True)

    def __repr__(self):
        return f"<Transaction #{self.id} — ${self.total_amount:.2f}>"


class TransactionItem(db.Model):
    """A single line-item within a transaction, linking a product to a transaction."""

    __tablename__ = "transaction_items"

    id = db.Column(db.Integer, primary_key=True)
    transaction_id = db.Column(
        db.Integer, db.ForeignKey("transactions.id"), nullable=False
    )
    product_id = db.Column(
        db.Integer, db.ForeignKey("products.id"), nullable=False
    )
    quantity = db.Column(db.Integer, nullable=False)
    price_at_checkout = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f"<TransactionItem txn={self.transaction_id} prod={self.product_id} qty={self.quantity}>"
