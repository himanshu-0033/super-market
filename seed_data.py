"""
Seed script — Populates the database with 100 products, stock, and
realistic dummy sales transactions spread over the last 30 days.

Usage:  python seed_data.py
"""

import random
from datetime import datetime, timedelta

from app import app, db
from models import Product, Transaction, TransactionItem, User

# ── Product catalog ──────────────────────────────────────────

PRODUCTS = [
    # (name, category, price_range_low, price_range_high)
    ("Whole Milk 1L", "Dairy", 2.50, 3.50),
    ("Skimmed Milk 1L", "Dairy", 2.00, 3.00),
    ("Greek Yogurt 500g", "Dairy", 3.50, 5.00),
    ("Cheddar Cheese 200g", "Dairy", 4.00, 6.00),
    ("Butter 250g", "Dairy", 3.00, 4.50),
    ("Cream Cheese 150g", "Dairy", 2.50, 4.00),
    ("Mozzarella 200g", "Dairy", 3.50, 5.50),
    ("Whipped Cream 250ml", "Dairy", 2.80, 4.20),
    ("White Bread Loaf", "Bakery", 2.00, 3.50),
    ("Whole Wheat Bread", "Bakery", 2.50, 4.00),
    ("Croissants 4-pack", "Bakery", 3.50, 5.50),
    ("Bagels 6-pack", "Bakery", 4.00, 6.00),
    ("Chocolate Muffins 4-pack", "Bakery", 4.50, 6.50),
    ("Sourdough Loaf", "Bakery", 4.00, 6.00),
    ("Banana", "Fruits", 0.30, 0.80),
    ("Apple Gala 1kg", "Fruits", 3.00, 5.00),
    ("Orange Navel 1kg", "Fruits", 3.50, 5.50),
    ("Strawberries 250g", "Fruits", 4.00, 6.00),
    ("Blueberries 150g", "Fruits", 3.50, 5.50),
    ("Grapes Red 500g", "Fruits", 3.00, 5.00),
    ("Mango", "Fruits", 1.50, 3.00),
    ("Watermelon Whole", "Fruits", 5.00, 8.00),
    ("Avocado", "Fruits", 1.00, 2.50),
    ("Pineapple", "Fruits", 3.00, 5.00),
    ("Lemon 3-pack", "Fruits", 1.50, 2.50),
    ("Broccoli 500g", "Vegetables", 2.00, 3.50),
    ("Carrots 1kg", "Vegetables", 1.50, 3.00),
    ("Tomatoes 500g", "Vegetables", 2.00, 3.50),
    ("Onions 1kg", "Vegetables", 1.00, 2.50),
    ("Potatoes 2kg", "Vegetables", 2.50, 4.00),
    ("Spinach 200g", "Vegetables", 2.00, 3.50),
    ("Bell Peppers 3-pack", "Vegetables", 3.00, 5.00),
    ("Cucumber", "Vegetables", 0.80, 1.50),
    ("Garlic 3-pack", "Vegetables", 1.50, 3.00),
    ("Mushrooms 250g", "Vegetables", 2.50, 4.00),
    ("Chicken Breast 500g", "Meat", 5.00, 8.00),
    ("Ground Beef 500g", "Meat", 6.00, 9.00),
    ("Pork Chops 4-pack", "Meat", 7.00, 11.00),
    ("Salmon Fillet 200g", "Seafood", 8.00, 12.00),
    ("Shrimp 250g", "Seafood", 7.00, 10.00),
    ("Tuna Steak 200g", "Seafood", 9.00, 14.00),
    ("Bacon 200g", "Meat", 4.00, 6.50),
    ("Sausages 6-pack", "Meat", 5.00, 7.50),
    ("Turkey Slices 150g", "Meat", 3.50, 5.50),
    ("Ham Slices 200g", "Meat", 4.00, 6.00),
    ("Coca-Cola 2L", "Beverages", 1.50, 2.50),
    ("Pepsi 2L", "Beverages", 1.50, 2.50),
    ("Orange Juice 1L", "Beverages", 3.00, 5.00),
    ("Apple Juice 1L", "Beverages", 3.00, 4.50),
    ("Sparkling Water 1.5L", "Beverages", 1.00, 2.00),
    ("Green Tea 20-bags", "Beverages", 3.00, 5.00),
    ("Coffee Beans 250g", "Beverages", 6.00, 10.00),
    ("Energy Drink 500ml", "Beverages", 2.00, 3.50),
    ("Lemonade 1L", "Beverages", 2.00, 3.50),
    ("Coconut Water 500ml", "Beverages", 2.50, 4.00),
    ("Pasta Spaghetti 500g", "Pantry", 1.50, 3.00),
    ("Pasta Penne 500g", "Pantry", 1.50, 3.00),
    ("Rice Basmati 1kg", "Pantry", 3.00, 5.00),
    ("Rice Jasmine 1kg", "Pantry", 3.00, 5.00),
    ("Olive Oil 500ml", "Pantry", 5.00, 8.00),
    ("Vegetable Oil 1L", "Pantry", 3.00, 5.00),
    ("Tomato Sauce 500g", "Pantry", 2.00, 3.50),
    ("Soy Sauce 250ml", "Pantry", 2.50, 4.00),
    ("Vinegar 500ml", "Pantry", 1.50, 3.00),
    ("Flour All-Purpose 1kg", "Pantry", 1.50, 3.00),
    ("Sugar 1kg", "Pantry", 1.50, 2.50),
    ("Salt 500g", "Pantry", 0.80, 1.50),
    ("Black Pepper 100g", "Pantry", 2.00, 3.50),
    ("Canned Tuna 3-pack", "Pantry", 4.00, 6.00),
    ("Canned Beans 400g", "Pantry", 1.00, 2.00),
    ("Peanut Butter 350g", "Pantry", 3.50, 5.50),
    ("Nutella 400g", "Pantry", 4.50, 6.50),
    ("Honey 500g", "Pantry", 5.00, 8.00),
    ("Cereal Corn Flakes 500g", "Breakfast", 3.00, 5.00),
    ("Oatmeal 500g", "Breakfast", 2.50, 4.00),
    ("Granola 400g", "Breakfast", 4.00, 6.00),
    ("Pancake Mix 500g", "Breakfast", 3.00, 5.00),
    ("Maple Syrup 250ml", "Breakfast", 5.00, 8.00),
    ("Eggs 12-pack", "Breakfast", 3.00, 5.00),
    ("Potato Chips 150g", "Snacks", 2.50, 4.00),
    ("Tortilla Chips 200g", "Snacks", 3.00, 4.50),
    ("Popcorn 100g", "Snacks", 1.50, 3.00),
    ("Dark Chocolate Bar 100g", "Snacks", 2.50, 4.50),
    ("Milk Chocolate Bar 100g", "Snacks", 2.00, 3.50),
    ("Gummy Bears 200g", "Snacks", 2.00, 3.50),
    ("Trail Mix 250g", "Snacks", 4.00, 6.00),
    ("Cookies 300g", "Snacks", 3.00, 5.00),
    ("Ice Cream Vanilla 500ml", "Frozen", 4.00, 6.00),
    ("Ice Cream Chocolate 500ml", "Frozen", 4.00, 6.00),
    ("Frozen Pizza", "Frozen", 5.00, 8.00),
    ("Frozen Vegetables 500g", "Frozen", 2.50, 4.00),
    ("Frozen French Fries 1kg", "Frozen", 3.00, 5.00),
    ("Dish Soap 500ml", "Household", 2.00, 3.50),
    ("Laundry Detergent 1L", "Household", 5.00, 8.00),
    ("Paper Towels 4-roll", "Household", 3.00, 5.00),
    ("Toilet Paper 12-roll", "Household", 6.00, 10.00),
    ("Trash Bags 30-pack", "Household", 4.00, 6.00),
    ("Toothpaste 100ml", "Personal Care", 2.00, 4.00),
    ("Shampoo 250ml", "Personal Care", 4.00, 7.00),
    ("Hand Soap 300ml", "Personal Care", 2.50, 4.50),
]

# Popularity weights — higher = sells more often
POPULARITY = {
    "Dairy": 8, "Bakery": 7, "Fruits": 9, "Vegetables": 6,
    "Meat": 5, "Seafood": 3, "Beverages": 10, "Pantry": 6,
    "Breakfast": 7, "Snacks": 8, "Frozen": 4, "Household": 3,
    "Personal Care": 3,
}


def seed():
    with app.app_context():
        # ── Clear old data ────────────────────────────────────
        TransactionItem.query.delete()
        Transaction.query.delete()
        Product.query.delete()
        db.session.commit()
        print("[1/4] Cleared old products and transactions.")

        # ── Ensure an admin + cashier user exist ──────────────
        admin = User.query.filter_by(username="admin").first()
        if not admin:
            admin = User(username="admin", role="admin")
            admin.set_password("admin123")
            db.session.add(admin)

        cashier = User.query.filter_by(username="cashier1").first()
        if not cashier:
            cashier = User(username="cashier1", role="cashier")
            cashier.set_password("cashier123")
            db.session.add(cashier)

        cashier2 = User.query.filter_by(username="cashier2").first()
        if not cashier2:
            cashier2 = User(username="cashier2", role="cashier")
            cashier2.set_password("cashier123")
            db.session.add(cashier2)

        db.session.commit()
        cashiers = [cashier, cashier2]
        print("[2/4] Users ready (admin / cashier1 / cashier2).")

        # ── Create 100 products ───────────────────────────────
        products = []
        for idx, (name, category, price_low, price_high) in enumerate(PRODUCTS):
            price = round(random.uniform(price_low, price_high), 2)
            stock = random.randint(20, 500)
            barcode = f"SKU{idx + 1:04d}"

            product = Product(
                name=name,
                barcode_id=barcode,
                category=category,
                price=price,
                stock_quantity=stock,
            )
            products.append(product)
            db.session.add(product)

        db.session.commit()
        print(f"[3/4] Created {len(products)} products.")

        # ── Generate transactions over the last 10 weeks ──────
        now = datetime.now()
        txn_count = 0
        item_count = 0

        for days_ago in range(70, -1, -1):
            day = now - timedelta(days=days_ago)

            # More transactions on weekends, fewer on weekdays
            if day.weekday() >= 5:  # Sat/Sun
                num_transactions = random.randint(15, 35)
            else:
                num_transactions = random.randint(8, 22)

            for _ in range(num_transactions):
                # Random time during business hours (8am–9pm)
                hour = random.randint(8, 21)
                minute = random.randint(0, 59)
                second = random.randint(0, 59)
                txn_time = day.replace(hour=hour, minute=minute, second=second)

                # Pick 1–6 products per transaction, weighted by popularity
                weights = [POPULARITY.get(p.category, 5) for p in products]
                num_items = random.choices([1, 2, 3, 4, 5, 6], weights=[25, 30, 20, 12, 8, 5])[0]
                chosen = random.choices(products, weights=weights, k=num_items)

                # Deduplicate — merge same products
                cart = {}
                for p in chosen:
                    qty = random.randint(1, 4)
                    if p.id in cart:
                        cart[p.id] = (p, cart[p.id][1] + qty)
                    else:
                        cart[p.id] = (p, qty)

                total = 0.0
                items = []
                for product, qty in cart.values():
                    line_total = round(product.price * qty, 2)
                    total += line_total
                    items.append((product, qty, product.price))

                txn = Transaction(
                    timestamp=txn_time,
                    total_amount=round(total, 2),
                    cashier_id=random.choice(cashiers).id,
                )
                db.session.add(txn)
                db.session.flush()

                for product, qty, price_at_checkout in items:
                    ti = TransactionItem(
                        transaction_id=txn.id,
                        product_id=product.id,
                        quantity=qty,
                        price_at_checkout=price_at_checkout,
                    )
                    db.session.add(ti)
                    item_count += 1

                txn_count += 1

        db.session.commit()
        print(f"[4/4] Created {txn_count} transactions with {item_count} line items.")

        # ── Adjust stock to reflect sales ─────────────────────
        # Deduct sold quantities from stock to make it realistic
        for product in products:
            total_sold = (
                db.session.query(
                    db.func.coalesce(db.func.sum(TransactionItem.quantity), 0)
                )
                .filter(TransactionItem.product_id == product.id)
                .scalar()
            )
            # Make some products go low-stock
            product.stock_quantity = max(0, product.stock_quantity - int(total_sold))

        db.session.commit()
        print("\n[OK] Database seeded successfully!")
        print(f"   Products: {len(products)}")
        print(f"   Transactions: {txn_count}")
        print(f"   Line Items: {item_count}")
        print("\n   Login credentials:")
        print("   Admin:    admin / admin123")
        print("   Cashier:  cashier1 / cashier123")
        print("   Cashier:  cashier2 / cashier123")


if __name__ == "__main__":
    seed()
