# Finance Data Processing and Access Control Backend

Backend assignment submission implemented with Django + Django REST Framework.

## 1. Submission Summary

This project implements a finance dashboard backend with:
- JWT authentication
- Role-based access control (viewer, analyst, admin)
- Financial record CRUD with filtering and pagination
- Dashboard summary and analytics endpoints
- Soft delete for users and records
- Input validation and structured error responses
- API documentation via OpenAPI/Swagger/ReDoc
- Docker support
- Automated tests

Stack:
- Python 3.9+
- Django 4.2
- Django REST Framework
- djangorestframework-simplejwt
- django-filter
- drf-spectacular
- SQLite

## 2. How This Matches Assignment Requirements

### 2.1 User and Role Management
Implemented:
- User creation/registration
- User listing and management (admin)
- Role assignment and role update (admin)
- Active/inactive and soft-delete behavior
- Action restrictions by role

Roles:
- `viewer`: read-only access to records and basic dashboard endpoints
- `analyst`: viewer access + category/trend analytics
- `admin`: full management of users and records

Key files:
- `users/models.py`
- `users/views.py`
- `users/permissions.py`
- `users/serializers.py`

### 2.2 Financial Records Management
Implemented:
- Create, list, detail, update, soft-delete records
- Filter by type/category/date/amount
- Search by text
- Pagination

Record fields:
- amount
- type (`income` or `expense`)
- category
- date
- description

Key files:
- `finance/models.py`
- `finance/views.py`
- `finance/filters.py`
- `finance/serializers.py`

### 2.3 Dashboard Summary APIs
Implemented endpoints for:
- Total income
- Total expenses
- Net balance
- Category-wise totals
- Recent activity
- Trends (daily/weekly/monthly)

Key file:
- `finance/views.py`

### 2.4 Access Control Logic
Implemented with DRF permission classes:
- `IsAdmin`
- `IsAnalystOrAdmin`
- `IsAnyRole`

Access control is enforced per endpoint in views.

Key file:
- `users/permissions.py`

### 2.5 Validation and Error Handling
Implemented:
- Serializer validation for payloads
- Strong password validation
- Proper HTTP status codes (`200`, `201`, `400`, `401`, `403`, `404`)
- Consistent error responses from DRF and view-level checks

### 2.6 Data Persistence
Implemented with SQLite via Django ORM.

DB file:
- `finance.db`

Models:
- `users.User`
- `finance.FinancialRecord`

## 3. Optional Enhancements Included

Included from optional list:
- JWT auth
- Pagination
- Search
- Soft delete
- Rate limiting config
- Unit/integration tests
- API docs (Swagger/ReDoc)
- Docker setup

## 4. API Endpoints

Base path: `/api/v1`

Auth:
- `POST /api/v1/auth/register/`
- `POST /api/v1/auth/login/`
- `POST /api/v1/auth/logout/`
- `POST /api/v1/auth/refresh/`

Users:
- `GET /api/v1/users/` (admin)
- `GET /api/v1/users/me/` (authenticated)
- `GET /api/v1/users/{id}/` (admin)
- `PUT /api/v1/users/{id}/` (admin)
- `PATCH /api/v1/users/{id}/` (admin)
- `PATCH /api/v1/users/{id}/role/` (admin)
- `DELETE /api/v1/users/{id}/` (admin, soft-delete)

Records:
- `GET /api/v1/records/` (authenticated)
- `POST /api/v1/records/` (admin)
- `GET /api/v1/records/{id}/` (authenticated)
- `PUT /api/v1/records/{id}/` (admin)
- `PATCH /api/v1/records/{id}/` (admin)
- `DELETE /api/v1/records/{id}/` (admin, soft-delete)

Dashboard:
- `GET /api/v1/dashboard/summary/` (authenticated)
- `GET /api/v1/dashboard/categories/` (analyst/admin)
- `GET /api/v1/dashboard/trends/` (analyst/admin)
- `GET /api/v1/dashboard/recent/` (authenticated)

Schema/docs:
- `GET /schema/`
- `GET /docs/`
- `GET /redoc/`

## 5. RBAC Matrix

| Action | Viewer | Analyst | Admin |
|---|---|---|---|
| View records | Yes | Yes | Yes |
| Create/update/delete records | No | No | Yes |
| View summary/recent | Yes | Yes | Yes |
| View categories/trends | No | Yes | Yes |
| Manage users | No | No | Yes |

## 6. Local Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[test]"
cp .env.example .env
python manage.py migrate
python manage.py runserver
```

API server:
- `http://127.0.0.1:8000`

Docs:
- Swagger: `http://127.0.0.1:8000/docs/`
- ReDoc: `http://127.0.0.1:8000/redoc/`

## 7. Run Tests

```bash
pytest tests/ -v
```

## 8. Docker

```bash
docker compose up --build
```

Default container port:
- `8000`

## 9. GitHub Pages Docs

This repository includes a static docs site in `docs/` deployed via GitHub Actions.

- Workflow: `.github/workflows/pages-deploy.yml`
- Trigger: pushes to `main` that change docs/workflow/readme
- Artifact: static files copied from `docs/` into `_site/`

Important:
- GitHub Pages hosts static docs only.
- The Django API runtime must be hosted separately.

## 10. Assumptions and Tradeoffs

Assumptions:
- SQLite is acceptable for assignment scope.
- Single-instance deployment is sufficient for evaluation.
- Email verification and external identity providers are out of scope.

Tradeoffs:
- SQLite chosen for setup speed and simplicity.
- Soft delete used for auditability over hard delete.
- Throttling is configured; dedicated throttling stress tests are not included.

## 11. Notes for Evaluator

This implementation prioritizes:
- clean endpoint design
- explicit business rules in permissions
- maintainable model/serializer/view separation
- practical testing coverage across auth, users, records, and dashboard

The project can be directly reviewed through Swagger endpoints and test output.

Credits - Ansh Singhal