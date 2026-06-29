# Software Requirements Specification (SRS)
## POS System — Retail Point of Sale

**Version:** 1.0  
**Date:** 2026-06-29  
**Author:** Himanshu

---

## 1. Introduction

### 1.1 Purpose
This document specifies the functional and non-functional requirements for a web-based Point of Sale (POS) system designed for small-to-medium retail stores. The system manages inventory, processes sales transactions, and provides sales analytics dashboards.

### 1.2 Scope
The system comprises:
- A **Flask** web application serving as both API backend and frontend renderer.
- An **SQLite** relational database (swappable to PostgreSQL).
- Role-based access control for **Admin** (store manager) and **Cashier** users.

### 1.3 Definitions & Acronyms
| Term | Definition |
|------|-----------|
| POS | Point of Sale |
| CRUD | Create, Read, Update, Delete |
| ORM | Object-Relational Mapper |
| FK | Foreign Key |
| PBKDF2 | Password-Based Key Derivation Function 2 |

---

## 2. Overall Description

### 2.1 Product Perspective
A standalone web application accessible via any modern browser. The system runs on a local server or can be deployed to a cloud platform.

### 2.2 User Classes
| Role | Capabilities |
|------|-------------|
| **Admin** | Full system access: manage inventory, view dashboard & analytics, manage users |
| **Cashier** | POS checkout interface: search products, build cart, process transactions |

### 2.3 Operating Environment
- Python 3.10+
- Flask 3.x
- SQLite 3 (development) / PostgreSQL (production)
- Modern web browser (Chrome, Firefox, Edge)

---

## 3. Functional Requirements

| ID | Requirement | Priority | Actor |
|----|-------------|----------|-------|
| FR-01 | The system shall allow users to register with a username, password, and role (Admin/Cashier). | High | All |
| FR-02 | The system shall authenticate users via username and password, establishing a session. | High | All |
| FR-03 | The system shall hash all passwords using PBKDF2 before storage. | High | System |
| FR-04 | The system shall restrict inventory management routes to Admin users only. | High | System |
| FR-05 | Admins shall be able to create new products with name, barcode, price, stock quantity, and category. | High | Admin |
| FR-06 | Admins shall be able to view, edit, and delete existing products. | High | Admin |
| FR-07 | The system shall support product search by name or barcode ID. | High | All |
| FR-08 | Cashiers shall be able to add products to a virtual cart with specified quantities. | High | Cashier |
| FR-09 | The system shall calculate the total price of all items in the cart at checkout. | High | System |
| FR-10 | On successful checkout, the system shall create a Transaction record and corresponding TransactionItem records. | High | System |
| FR-11 | On successful checkout, the system shall deduct purchased quantities from product stock. | High | System |
| FR-12 | The system shall reject checkout if any product has insufficient stock. | High | System |
| FR-13 | The system shall display a daily revenue report grouped by date. | Medium | Admin |
| FR-14 | The system shall display a top-selling products report ranked by total quantity sold. | Medium | Admin |
| FR-15 | The system shall alert the admin when any product's stock falls below 10 units. | Medium | Admin |

---

## 4. Non-Functional Requirements

| ID | Requirement | Category |
|----|-------------|----------|
| NFR-01 | The POS checkout operation must complete in under 500 ms. | Performance |
| NFR-02 | All passwords must be hashed using Werkzeug's PBKDF2 implementation. | Security |
| NFR-03 | The system must use parameterized queries (via SQLAlchemy ORM) to prevent SQL injection. | Security |
| NFR-04 | The UI must be responsive and usable on screens ≥ 768px wide. | Usability |
| NFR-05 | The system must use CSRF-safe session management via Flask-Login. | Security |
| NFR-06 | The database schema must support migration to PostgreSQL without code changes. | Portability |

---

## 5. Data Flow

```
User Login → Session Established → Role-Based Routing
                                        │
                        ┌───────────────┼───────────────┐
                        ▼                               ▼
                   Admin Routes                   Cashier Routes
                   ┌──────────┐                   ┌──────────┐
                   │Dashboard │                   │  POS     │
                   │Inventory │                   │  Cart    │
                   │Analytics │                   │ Checkout │
                   └──────────┘                   └──────────┘
                        │                               │
                        ▼                               ▼
                   Product CRUD                  Transaction Creation
                                                 Stock Deduction
```

---

## 6. Constraints
- Development database limited to SQLite (single-writer concurrency).
- No payment gateway integration in v1.0.
- No barcode scanner hardware integration; barcodes entered manually.
