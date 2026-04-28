# AAFES Order Management MVP

A full-stack order management system for AAFES distribution centers with JWT authentication, role-based access control, real-time inventory validation, and comprehensive audit logging.

## Project Overview & Features

- **JWT Authentication** - Secure token-based auth with 8-hour sessions
- **Role-Based Access Control** - 4 user roles (Salesperson, Inventory Manager, Fulfillment Team, Admin)
- **Order Management** - Real-time inventory validation with atomic transactions
- **Inventory Tracking** - Live stock updates with automatic decrement on orders
- **Invoice Generation** - Dynamic HTML invoices with Jinja2 templates
- **Audit Logging** - Complete trail of logins, orders, and inventory changes
- **Notification System** - Mock notification logging for order lifecycle events

## Tech Stack

**Backend**: FastAPI, SQLModel, SQLite/MySQL, JWT, PBKDF2  
**Frontend**: React, Fetch API, Custom CSS  
**Testing**: Pytest, Integration Tests

## Project Structure

```
.
├── backend/
│   ├── main.py              # FastAPI app & endpoints
│   ├── models.py            # Database models
│   ├── auth.py              # JWT authentication
│   ├── authorization.py     # RBAC middleware
│   ├── audit_service.py     # Audit logging
│   ├── invoice_service.py   # Invoice generation
│   └── seed_data.py         # Test data seeding
│
└── ui/
    ├── src/
    │   ├── components/      # React components
    │   └── utils/api.js     # JWT API wrapper
    └── package.json

```

## Quick Start

### Backend

```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install fastapi uvicorn sqlmodel python-jose[cryptography] passlib jinja2
python seed_data.py  # Seeds test users and data
uvicorn main:app --reload
```

**API Docs**: http://localhost:8000/docs

### Frontend

```bash
cd ui
npm install && npm start
```

**App**: http://localhost:3000

### Test Users

| Username            | Password      | Role              |
| ------------------- | ------------- | ----------------- |
| `alice_sales`       | `password123` | Salesperson       |
| `bob_inventory`     | `password123` | Inventory Manager |
| `charlie_admin`     | `password123` | Admin             |
| `diana_fulfillment` | `password123` | Fulfillment Team  |

## User Roles

| Role                  | Permissions                                  |
| --------------------- | -------------------------------------------- |
| **Salesperson**       | Create orders, view own orders               |
| **Inventory Manager** | Adjust inventory, view all orders            |
| **Fulfillment Team**  | Update order status, view fulfillment orders |
| **Admin**             | Full access + audit logs + notification logs |

---

## API Highlights

All endpoints documented at `/docs` (Swagger UI)

**Key Endpoints**:

- `POST /api/auth/login` - JWT authentication
- `POST /api/orders/create` - Create order with validation
- `GET /api/orders` - Get orders (role-filtered)
- `PATCH /api/inventory/{id}/adjust` - Adjust inventory
- `GET /api/orders/{id}/invoice` - Generate HTML invoice
- `GET /api/audit-logs` - Audit trail (Admin only)

**Built with FastAPI, React, and SQLModel** -> [View API Docs](http://localhost:8000/docs)
