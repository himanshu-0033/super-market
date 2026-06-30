# RetailPOS — Point of Sale System

A full-stack POS (Point of Sale) web application I built as part of my Software Development Engineering course. It handles everything a small retail store needs — managing inventory, processing sales through a cashier checkout screen, and tracking business performance through an analytics dashboard.

I wanted to go beyond just a CRUD app, so I added features like role-based access control, real-time stock validation during checkout, and interactive sales charts with different time ranges. The whole thing is built with Flask and SQLite, with no JavaScript frameworks on the frontend — just clean templating and vanilla JS where needed.

---

## What it does

The system has two types of users, each with their own interface:

**Admin (Store Manager)**
- Manages the product catalog — add, edit, delete products with names, barcodes, prices, stock levels, and categories
- Sees an analytics dashboard showing today's revenue, transaction count, and low stock alerts
- Views interactive sales charts that can be filtered by day, week, month, or year
- Tracks top-selling products and compares available stock vs units sold

**Cashier**
- Gets a clean checkout screen with a product grid and live search
- Adds items to a cart, adjusts quantities, and processes sales
- Stock is validated in real-time — you can't sell more than what's available
- After checkout, inventory is automatically updated

---

## Tech Stack

| Layer | Technology |
|---|---|
| **Backend** | Python 3, Flask, Flask-SQLAlchemy, Flask-Login |
| **Database** | SQLite (easily swappable to PostgreSQL via config) |
| **Frontend** | Jinja2 templates, vanilla CSS, vanilla JavaScript |
| **Charts** | Chart.js for interactive revenue and sales visualizations |
| **Auth** | Session-based authentication with Werkzeug password hashing (PBKDF2) |

---

## Project Structure

The codebase is cleanly separated into backend and frontend:

```
├── app.py                    # Entry point — creates the app and runs the server
├── requirements.txt          # Python dependencies
│
├── backend/                  # All server-side logic
│   ├── __init__.py           # Flask app factory with blueprint registration
│   ├── config.py             # App configuration (secret key, database URI, thresholds)
│   ├── models.py             # SQLAlchemy models (User, Product, Transaction, TransactionItem)
│   └── routes/
│       ├── auth.py           # Login, signup, logout with role-based redirects
│       ├── inventory.py      # CRUD operations for product management (admin only)
│       ├── pos.py            # Checkout flow, product search API, stock validation
│       └── dashboard.py      # Analytics APIs — revenue trends, top products, stock reports
│
├── frontend/                 # All client-side files
│   ├── static/
│   │   └── style.css         # Styling for the entire application
│   └── templates/
│       ├── base.html         # Base layout with navbar (extended by all pages)
│       ├── login.html        # Login page
│       ├── signup.html       # Registration with role selection
│       ├── dashboard.html    # Admin analytics with Chart.js graphs
│       ├── inventory.html    # Product table with search, edit, delete
│       ├── add_product.html  # Form to add a new product
│       ├── edit_product.html # Form to edit an existing product
│       └── pos.html          # Cashier checkout screen with cart
│
├── docs/
│   ├── SRS.md                # Software Requirements Specification
│   └── UML.md                # UML class diagram (Mermaid format)
│
└── instance/
    └── pos.db                # SQLite database (auto-generated on first run)
```

---

## How to run it

**You need:** Python 3.10 or higher

```bash
# 1. Clone the repo
git clone https://github.com/himanshu-0033/super-market.git
cd super-market

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the app
python app.py
```

Open [http://127.0.0.1:5000](http://127.0.0.1:5000) in your browser. The database tables get created automatically on the first run — no manual setup needed.

---

## Quick start guide

1. **Sign up** as an Admin — select "Admin (Manager)" from the role dropdown
2. Go to **Inventory** → add some products (name, barcode, price, stock, category)
3. **Log out**, then create a second account with the Cashier role
4. Use the **POS** screen — search for products, add them to your cart, and checkout
5. Log back in as Admin → check the **Dashboard** to see revenue charts, top sellers, and stock levels

---

## Features in detail

### Authentication & Authorization
- Signup and login with username/password
- Passwords are hashed using Werkzeug's PBKDF2 — never stored in plain text
- Role-based access control: Admins see Dashboard + Inventory, Cashiers see the POS screen
- Automatic redirect after login based on user role
- Protected routes with custom `admin_required` and `cashier_required` decorators

### Inventory Management (Admin)
- Full CRUD — add, view, edit, and delete products
- Each product has: name, barcode ID (unique), price, stock quantity, and category
- Search products by name or barcode
- Low stock warnings for items below the configurable threshold (default: 10 units)
- Barcode uniqueness validation to prevent duplicates

### Point of Sale — Checkout (Cashier)
- Product grid with a clean tile layout
- Real-time search via a REST API (`/api/products?q=...`)
- Client-side cart management — add items, adjust quantities, remove items
- Stock validation before checkout — prevents overselling
- Atomic transactions — if anything fails, the entire checkout rolls back
- Records every sale with line-item details and the price at time of checkout

### Analytics Dashboard (Admin)
- **Today's snapshot** — total revenue and number of transactions
- **Revenue trends** — interactive Chart.js line chart with selectable time ranges:
  - By hour (today), daily (last 7 days), bi-weekly (last 30 days), monthly (last 12 months)
- **Top-selling products** — bar chart showing most sold items by quantity
- **Stock vs Sold** — comparison chart showing available inventory against total units sold
- **Low stock alerts** — list of products running low, sorted by quantity

### REST API Endpoints
The dashboard and POS communicate with the backend through JSON APIs:

| Endpoint | Method | Description |
|---|---|---|
| `/api/products` | GET | Product list (with optional `?q=` search) |
| `/api/checkout` | POST | Process a sale (validates stock, deducts inventory) |
| `/api/sales_data?range=` | GET | Revenue data for charts (day/week/month/year) |
| `/api/sales_share?limit=` | GET | Top N products by quantity sold |
| `/api/stock_vs_sold` | GET | Available stock vs total sold per product |

---

## Database Design

Four tables with clear relationships:

```
User (1) ────→ (*) Transaction
                      │
Transaction (1) ──→ (*) TransactionItem
                              │
Product (1) ──────→ (*) TransactionItem
```

- **User** — stores username, hashed password, and role (admin/cashier)
- **Product** — name, barcode, price, stock quantity, category
- **Transaction** — timestamp, total amount, linked to the cashier who processed it
- **TransactionItem** — links a product to a transaction with quantity and price at checkout time

Full class diagram available in [docs/UML.md](docs/UML.md) and requirements spec in [docs/SRS.md](docs/SRS.md).

---

## Design decisions

- **App Factory pattern** — the Flask app is created via `create_app()` in `backend/__init__.py`, making it testable and configurable
- **Blueprints** — routes are organized into 4 blueprints (auth, inventory, pos, dashboard) for clean separation
- **Frontend/Backend split** — templates and static files live in `frontend/`, Python logic in `backend/`
- **Price at checkout** — `TransactionItem` stores `price_at_checkout` so historical records stay accurate even if product prices change later
- **Soft error handling** — the POS checkout validates everything before committing, and rolls back on failure

---

## Future improvements

- [ ] Pagination for the inventory table (currently loads all products)
- [ ] Receipt generation — PDF export or print after checkout
- [ ] Restrict admin signup — only existing admins should be able to create new admin accounts
- [ ] Barcode scanner integration for faster checkout
- [ ] Migrate to PostgreSQL for production use
- [ ] Add unit tests with pytest
- [ ] Deploy to a cloud platform (Render, Railway, or similar)

---

## Course context

Built as part of my Software Development Engineering coursework. The project demonstrates:

- **Requirements engineering** — SRS document with functional and non-functional requirements
- **System design** — UML class diagrams and relational database modeling
- **Full-stack development** — Flask backend with Jinja2 templated frontend
- **Database design** — normalized schema with foreign key relationships
- **Authentication & authorization** — session-based auth with role-based access control
- **REST API design** — JSON endpoints for dynamic frontend interaction
- **Software architecture** — app factory pattern, blueprint-based route organization
