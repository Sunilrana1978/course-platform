# LearnHub — Course Platform

A full-stack e-learning application where users can register, browse courses, purchase individual courses à la carte or buy an all-access subscription (monthly / annual). Payments are processed through an extensible gateway abstraction with a Mock Stripe implementation, and the checkout flow is fully idempotent — no duplicate charges regardless of retries or page refreshes.

---

## Table of Contents

- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Quick Start](#quick-start)
- [Architecture Overview](#architecture-overview)
  - [Backend Apps](#backend-apps)
  - [Frontend Structure](#frontend-structure)
- [Data Models](#data-models)
- [API Reference](#api-reference)
- [Payment Gateway System](#payment-gateway-system)
- [Idempotent Payment Flow](#idempotent-payment-flow)
- [Authentication Flow](#authentication-flow)
- [Environment Variables](#environment-variables)
- [Switching to a Real Database](#switching-to-a-real-database)
- [Adding a New Payment Provider](#adding-a-new-payment-provider)

---

## Tech Stack

| Layer     | Technology                                          |
|-----------|-----------------------------------------------------|
| Frontend  | React 18, TypeScript, Vite, React Router v6, Axios  |
| Backend   | Python 3.11, Django 5, Django REST Framework        |
| Auth      | JWT via `djangorestframework-simplejwt`             |
| Database  | SQLite (ephemeral / in-memory semantics for dev)    |
| Payments  | Mock Stripe gateway (real Stripe-shaped responses)  |

---

## Project Structure

```
course-platform/
├── backend/
│   ├── core/
│   │   ├── settings.py          # Django config, DB, JWT, CORS, gateway env vars
│   │   └── urls.py              # Root URL conf — mounts all app routers
│   ├── apps/
│   │   ├── users/               # Custom User model, register, JWT endpoints
│   │   ├── courses/             # Course catalog, access checks, seed command
│   │   ├── cart/                # Per-user cart (courses + subscription plans)
│   │   ├── subscriptions/       # Plans (Monthly/Annual) + UserSubscription
│   │   └── payments/
│   │       ├── gateways/
│   │       │   ├── base.py      # Abstract PaymentGateway interface
│   │       │   ├── stripe_mock.py  # Mock Stripe implementation
│   │       │   └── factory.py   # get_gateway(name) — add providers here
│   │       ├── models.py        # Payment model with idempotency_key
│   │       └── services.py      # Idempotency logic, grant_access
│   ├── manage.py
│   ├── requirements.txt
│   └── start.sh                 # Wipes DB → migrate → seed → runserver
│
└── frontend/
    ├── src/
    │   ├── api/                 # Axios wrappers (auth, courses, cart, payments, subscriptions)
    │   ├── context/
    │   │   ├── AuthContext.tsx  # User state, JWT storage, login/logout
    │   │   └── CartContext.tsx  # Cart state, add/remove/clear helpers
    │   ├── components/
    │   │   ├── Navbar.tsx
    │   │   ├── CourseCard.tsx
    │   │   └── ProtectedRoute.tsx
    │   └── pages/
    │       ├── Auth/            # LoginPage, RegisterPage
    │       ├── Catalog/         # CatalogPage — browse + filter courses
    │       ├── CourseDetail/    # CourseDetailPage
    │       ├── Cart/            # CartPage
    │       ├── Checkout/        # CheckoutPage — idempotency key lives here
    │       ├── Dashboard/       # DashboardPage — enrolled courses + subscription
    │       └── Subscriptions/   # PlansPage — Monthly vs Annual comparison
    ├── vite.config.ts           # Proxies /api → localhost:8000
    └── start.sh
```

---

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 16+

### 1. Backend

```bash
cd backend

# First-time setup: create virtual environment and install dependencies
python3 -m venv venv
venv/bin/pip install -r requirements.txt

# Start the server (resets DB, runs migrations, seeds data, starts Django)
./start.sh
```

The backend will be available at `http://localhost:8000`.  
Each run of `start.sh` wipes the database and reseeds 10 courses + 2 subscription plans, giving a clean slate every time.

### 2. Frontend

Open a second terminal:

```bash
cd frontend
npm install      # first time only
./start.sh
```

The app will open at `http://localhost:5173`.  
Vite proxies all `/api/*` requests to the Django backend automatically — no CORS config needed during development.

---

## Architecture Overview

### Backend Apps

```
Request → Django URL router → App view → Serializer → Model
                                      ↘ Service (payments)
```

| App             | Responsibility                                                      |
|-----------------|---------------------------------------------------------------------|
| `users`         | Custom `User` model (email as username), register endpoint, JWT login via simplejwt |
| `courses`       | `Course` model, list/detail views with optional category & search filters, access-check endpoint, `seed` management command |
| `cart`          | `CartItem` model linking a user to a course or subscription plan; add/remove/clear endpoints |
| `subscriptions` | `Plan` (Monthly / Annual) and `UserSubscription` models; plan listing and current-subscription endpoints |
| `payments`      | `Payment` model with idempotency key, gateway abstraction layer, `services.py` containing all payment state-machine logic |

### Frontend Structure

```
App.tsx (BrowserRouter)
  └── AuthProvider  ← JWT tokens & user in localStorage
        └── CartProvider  ← cart state, synced with backend
              └── Navbar
              └── Routes
                    /                   → CatalogPage
                    /courses/:id        → CourseDetailPage
                    /subscriptions      → PlansPage
                    /login              → LoginPage
                    /register           → RegisterPage
                    /cart         [🔒] → CartPage
                    /checkout     [🔒] → CheckoutPage
                    /dashboard    [🔒] → DashboardPage
```

`[🔒]` routes are wrapped in `ProtectedRoute` — unauthenticated users are redirected to `/login` and returned to their original destination after logging in.

The API layer (`src/api/`) uses a shared Axios client (`src/api/client.ts`) that:
1. Attaches `Authorization: Bearer <token>` to every request automatically.
2. Intercepts `401` responses, uses the refresh token to get a new access token, and retries the original request — transparent to all callers.

---

## Data Models

```
User
  ├── email (unique, used as login)
  └── username, first_name, last_name, password

Course
  ├── title, description, instructor
  ├── price (Decimal)
  ├── category  (web | data | devops)
  ├── thumbnail_url, duration_hours

CartItem
  ├── user (FK → User)
  ├── item_type  (course | plan)
  ├── course (FK → Course, nullable)
  └── plan   (FK → Plan, nullable)

Plan
  ├── name  (Monthly | Annual)
  ├── price, duration_days, description

UserSubscription
  ├── user (FK → User)
  ├── plan (FK → Plan)
  ├── start_date, end_date, is_active
  └── payment (FK → Payment)

UserCourseAccess
  ├── user (FK → User)
  ├── course (FK → Course)
  └── payment (FK → Payment)

Payment
  ├── id (UUID, primary key)
  ├── idempotency_key (unique, indexed)  ← deduplication key
  ├── user (FK → User)
  ├── amount, currency
  ├── status  (PENDING | PROCESSING | COMPLETED | FAILED)
  ├── gateway  (stripe | ...)
  ├── gateway_ref  (Stripe PaymentIntent id)
  ├── payload (JSON)  ← cart snapshot at payment time
  └── error_detail
```

---

## API Reference

All protected endpoints require `Authorization: Bearer <access_token>`.

### Auth

| Method | Path                    | Auth | Description                          |
|--------|-------------------------|------|--------------------------------------|
| POST   | `/api/auth/register/`   | —    | Register; returns `{ access, refresh, user }` |
| POST   | `/api/auth/login/`      | —    | Login; returns `{ access, refresh }` |
| POST   | `/api/auth/refresh/`    | —    | Exchange refresh token for new access token |
| GET    | `/api/auth/me/`         | ✓    | Current user profile                 |

### Courses

| Method | Path                       | Auth | Description                          |
|--------|----------------------------|------|--------------------------------------|
| GET    | `/api/courses/`            | —    | List courses; supports `?category=web&search=react` |
| GET    | `/api/courses/<id>/`       | —    | Course detail                        |
| GET    | `/api/courses/<id>/access/`| ✓    | `{ has_access, reason }` — checks direct purchase or active subscription |

### Cart

| Method | Path                   | Auth | Description             |
|--------|------------------------|------|-------------------------|
| GET    | `/api/cart/`           | ✓    | Get cart with total     |
| POST   | `/api/cart/items/`     | ✓    | Add course or plan      |
| DELETE | `/api/cart/items/<id>/`| ✓    | Remove item             |
| POST   | `/api/cart/clear/`     | ✓    | Empty the cart          |

**Add item body:**
```json
{ "item_type": "course", "course": 3 }
{ "item_type": "plan",   "plan": 1  }
```

### Subscriptions

| Method | Path                        | Auth | Description              |
|--------|-----------------------------|------|--------------------------|
| GET    | `/api/subscriptions/plans/` | —    | List Monthly & Annual plans |
| GET    | `/api/subscriptions/me/`    | ✓    | Current user's active subscription |

### Payments

| Method | Path                          | Auth | Description                          |
|--------|-------------------------------|------|--------------------------------------|
| POST   | `/api/payments/initiate/`     | ✓    | Create or resume a payment intent    |
| POST   | `/api/payments/confirm/`      | ✓    | Charge the card                      |
| GET    | `/api/payments/<uuid>/status/`| ✓    | Poll payment status                  |

**Initiate body:**
```json
{
  "idempotency_key": "550e8400-e29b-41d4-a716-446655440000",
  "cart_items": [
    { "item_type": "course", "course_id": 3, "price": "59.99" }
  ]
}
```

**Confirm body:**
```json
{
  "payment_id": "374a4abd-d26e-4cb3-9bd2-7a8b684c46f8",
  "card_number": "4242424242424242",
  "card_expiry": "12/27",
  "card_cvc": "123",
  "card_name": "Jane Smith"
}
```

---

## Payment Gateway System

The gateway layer uses the **Strategy pattern** — all providers implement the same abstract interface, and the factory returns the correct one at runtime based on the `PAYMENT_GATEWAY` environment variable.

```
PaymentGateway (base.py — abstract)
    create_intent(amount, currency, metadata) → dict
    confirm_intent(intent_id, payment_method) → dict
    get_intent(intent_id) → dict

StripeMockGateway (stripe_mock.py)
    └── Stores intents in-process memory
    └── Returns Stripe-shaped dicts
    └── Configurable failure rate via MOCK_FAILURE_RATE

factory.py
    get_gateway('stripe') → StripeMockGateway()
    # get_gateway('paypal') → PayPalGateway()   ← future
```

The `Payment.gateway` field stores the registered provider name (e.g., `stripe`) so the correct gateway can be retrieved when confirming a payment that was initiated earlier.

---

## Idempotent Payment Flow

This is the core reliability feature. No matter how many times a user clicks Pay or refreshes the page, exactly one charge is made.

### Step-by-step

```
1. User navigates to /checkout
   └── CheckoutPage reads sessionStorage['idempotency_key']
   └── If absent, generates crypto.randomUUID() and stores it

2. POST /api/payments/initiate/  { idempotency_key, cart_items }
   Backend logic (services.py):
     a. Query: SELECT Payment WHERE idempotency_key = key
     b. COMPLETED  → return existing payment (no new charge)
     c. PROCESSING → HTTP 202 (frontend polls)
     d. PENDING    → return existing payment (user can retry confirm)
     e. Not found  → create Payment(status=PENDING), call gateway.create_intent()

3. User fills card form, clicks Pay
   POST /api/payments/confirm/  { payment_id, card_* }
   Backend (select_for_update prevents race conditions):
     a. Assert status == PENDING
     b. Set status = PROCESSING  (atomic)
     c. Call gateway.confirm_intent()
     d. SUCCESS → status = COMPLETED, call grant_access()
     e. FAILURE → status = FAILED, store error

4. Frontend result handling:
     COMPLETED → clear idempotency_key from sessionStorage → redirect /dashboard
     PROCESSING → start polling /api/payments/<id>/status/ every 2 seconds
     FAILED     → show error, allow retry (same payment_id, re-submit card)

5. grant_access() reads the cart snapshot from Payment.payload:
     course items  → create UserCourseAccess records
     plan items    → deactivate old subscription, create new UserSubscription
```

### Why sessionStorage (not localStorage)?

`sessionStorage` persists across page refreshes within the same tab but is cleared when the tab is closed. This means:
- Refresh mid-payment → same key → same payment resumed (no duplicate)
- Open new tab to pay again → new key → new payment (correct behavior)
- Log out, log back in → key is cleared by logout handler

### Payment state machine

```
         initiate()          confirm()
PENDING ──────────► PENDING ──────────► PROCESSING
                                              │
                                    gateway confirms
                                        │         │
                                   succeeded    failed
                                        │         │
                                   COMPLETED   FAILED
```

`COMPLETED` is terminal — any further `initiate()` with the same key returns the completed payment immediately.

---

## Authentication Flow

```
Register / Login
  └── Backend returns { access (60 min), refresh (7 days), user }
  └── Frontend stores tokens in localStorage, user object in localStorage

Every API request
  └── Axios interceptor adds:  Authorization: Bearer <access_token>

On 401 response (expired access token)
  └── Axios interceptor calls POST /api/auth/refresh/
  └── Stores new access token
  └── Retries the original request transparently
  └── If refresh fails → clear tokens → redirect to /login

Logout
  └── Removes access_token, refresh_token, user from localStorage
  └── Removes idempotency_key from sessionStorage
```

---

## Environment Variables

Set these before running the backend (or add to a `.env` file):

| Variable           | Default    | Description                                             |
|--------------------|------------|---------------------------------------------------------|
| `SECRET_KEY`       | dev key    | Django secret key — change in production                |
| `DEBUG`            | `True`     | Set to `False` in production                            |
| `DB_PATH`          | `/tmp/course_platform_dev.db` | Path to SQLite file; delete to reset |
| `PAYMENT_GATEWAY`  | `stripe`   | Active payment provider key                             |
| `MOCK_FAILURE_RATE`| `0.05`     | Probability (0.0–1.0) that a mock payment fails. Set to `1.0` to test failure handling |

### Example: test payment failures

```bash
MOCK_FAILURE_RATE=1.0 ./start.sh
```

Every payment will fail, letting you verify error messages and retry flows.

---

## Switching to a Real Database

In `backend/core/settings.py`, replace:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': _DB_PATH,
    }
}
```

with:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ['DB_NAME'],
        'USER': os.environ['DB_USER'],
        'PASSWORD': os.environ['DB_PASSWORD'],
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}
```

Then run `pip install psycopg2-binary` and `python manage.py migrate`. No other code changes needed.

---

## Adding a New Payment Provider

1. Create `backend/apps/payments/gateways/paypal.py` implementing the three abstract methods:

```python
from .base import PaymentGateway

class PayPalGateway(PaymentGateway):
    def create_intent(self, amount, currency, metadata) -> dict: ...
    def confirm_intent(self, intent_id, payment_method) -> dict: ...
    def get_intent(self, intent_id) -> dict: ...
```

2. Register it in `backend/apps/payments/gateways/factory.py`:

```python
from .paypal import PayPalGateway

_REGISTRY = {
    'stripe': StripeMockGateway,
    'paypal': PayPalGateway,     # ← add this line
}
```

3. Set the environment variable:

```bash
PAYMENT_GATEWAY=paypal ./start.sh
```

No other code changes are required. The idempotency logic, state machine, and access-granting all operate on the abstract interface.
# course-platform
