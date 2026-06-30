# RetailPOS — Point of Sale System

A web-based POS (Point of Sale) system I built for my SDE course project. It handles inventory management, sales checkout, and gives you a nice dashboard with sales stats. Built with Flask and SQLite.

---

## What it does

Basically, there are two types of users — **Admin** and **Cashier**.

- **Admin** can manage the product inventory (add, edit, delete products), and see a dashboard with daily revenue, top-selling products, and low stock alerts.
- **Cashier** gets a POS screen where they can search products, add them to a cart, and checkout. Stock gets deducted automatically.

The whole thing runs in the browser. No fancy frameworks on the frontend — just Flask templates, vanilla CSS, and a bit of JavaScript for the cart.

---

## Screenshots

| Login | Dashboard | POS Checkout |
|-------|-----------|-------------|
| Clean login/signup flow | Revenue charts + low stock alerts | Product tiles + cart sidebar |

*(run the app locally to see it in action)*

---

## Tech Stack

- **Backend:** Python, Flask, Flask-SQLAlchemy, Flask-Login
- **Database:** SQLite (can be swapped for PostgreSQL)
- **Frontend:** Jinja2 templates, vanilla CSS, Chart.js for graphs
- **Auth:** Session-based auth with Werkzeug password hashing (PBKDF2)

---

## Project Structure

```
├── backend/
│   ├── __init__.py        # flask app factory
│   ├── config.py          # app configuration
│   ├── models.py          # database models
│   └── routes/            # separated blueprints
│       ├── auth.py
│       ├── dashboard.py
│       ├── inventory.py
│       └── pos.py
│
├── frontend/
│   ├── static/
│   │   └── style.css      # all the styling
│   └── templates/
│       ├── base.html      # base layout with navbar
│       ├── login.html
│       ├── signup.html
│       ├── dashboard.html # admin stats + charts
│       ├── inventory.html # product table with CRUD
│       ├── add_product.html
│       ├── edit_product.html
│       └── pos.html       # cashier checkout screen
│
├── app.py                 # thin entry point
├── requirements.txt
│
├── docs/
│   ├── SRS.md             # software requirements spec
│   └── UML.md             # class diagram (mermaid)
│
└── instance/
    └── pos.db             # sqlite database (auto-generated)
```

---

## How to run it

**Prerequisites:** Python 3.10 or higher

```bash
# clone the repo
git clone https://github.com/your-username/RetailPOS.git
cd RetailPOS

# install dependencies
pip install -r requirements.txt

# run the app
python app.py
```

Then open [http://127.0.0.1:5000](http://127.0.0.1:5000) in your browser.

The database gets created automatically on first run — you don't need to set anything up.

---

## Quick start guide

1. **Sign up** as an Admin first (pick "Admin (Manager)" from the role dropdown)
2. Go to **Inventory** → add a few products with name, barcode, price, and stock
3. **Log out**, then sign up as a Cashier
4. Use the **POS** screen to add items to cart and checkout
5. Log back in as Admin to see the **Dashboard** — revenue, charts, alerts

---

## Features

### Authentication
- Sign up / Login / Logout
- Password hashing with Werkzeug (never stored in plain text)
- Role-based access control — admins and cashiers see different things

### Inventory (Admin only)
- Add, edit, delete products
- Search by product name or barcode
- Low stock warnings (below 10 units)

### Point of Sale (Cashier)
- Browse products with a visual tile grid
- Client-side search (filters as you type)
- Add to cart, adjust quantities, remove items
- One-click checkout — creates transaction records and deducts stock
- Stock validation (won't let you sell more than what's available)

### Dashboard (Admin)
- Today's revenue and transaction count
- Daily revenue chart (last 7 days) using Chart.js
- Top 10 selling products bar chart
- Low stock alert list

---

## Database design

Four main tables — here's the relationship:

```
User (1) ──→ (*) Transaction
Transaction (1) ──→ (*) TransactionItem
Product (1) ──→ (*) TransactionItem
```

Check out [docs/UML.md](docs/UML.md) for the full class diagram and [docs/SRS.md](docs/SRS.md) for the requirements spec.

---

## Things I'd improve with more time

- [ ] Add pagination for the inventory table
- [ ] Receipt printing / PDF export after checkout
- [ ] Restrict admin signup (only existing admins should create new ones)
- [ ] Add barcode scanner support
- [ ] Switch to PostgreSQL for production
- [ ] Add proper unit tests
- [ ] Deploy to a cloud platform (Render, Railway, etc.)

---

## Course info

This was built as part of my Software Development Engineering coursework. The project covers:

- **SRS documentation** — functional and non-functional requirements
- **UML class diagrams** — entity relationships and data modeling
- **Full-stack development** — Flask backend + templated frontend
- **Database design** — relational schema with foreign keys
- **Role-based access** — authentication and authorization

---


