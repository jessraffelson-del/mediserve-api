# MediServe API
### Secure Healthcare API with OAuth2, JWT, and RBAC

![CI](https://github.com/jessraffelson-del/mediserve-api/actions/workflows/ci.yml/badge.svg)

A production-ready secure healthcare API built with FastAPI, implementing OAuth2 authentication, JWT tokens, Role-Based Access Control, and protection against common security threats. Built to demonstrate HIPAA-relevant API security patterns for healthcare partner integrations.

---

## Features

- **OAuth2 + JWT Authentication** — Secure token-based authentication with 30-minute expiration
- **Role-Based Access Control** — Doctor, Admin, and Insurance roles with enforced access boundaries
- **HIPAA-Relevant Design** — Minimum necessary access — insurance partners see billing data only, doctors see clinical data
- **bcrypt Password Hashing** — Industry standard password security, never plain text storage
- **Rate Limiting** — DoS protection via slowapi
- **Request Logging** — Every request logged with method, path, status, and duration
- **Global Exception Handler** — Clean error responses, no internal stack traces exposed
- **CORS Middleware** — Configurable cross-origin resource sharing
- **Auto-Generated Swagger Docs** — Interactive documentation with security schemes visible
- **CI/CD** — GitHub Actions pipeline verifies build on every push

---

## Roles and Access

| Endpoint | Doctor | Admin | Insurance |
|---|---|---|---|
| GET /patients/{id} | Full record | Full record | 403 |
| GET /patients/{id}/insurance | 403 | Full record | Name + ID only |
| GET /patients | 403 | All records | 403 |
| GET /me | Yes | Yes | Yes |

---

## Tech Stack

| Layer | Technology |
|---|---|
| Framework | FastAPI |
| Authentication | OAuth2 + JWT (python-jose) |
| Password Security | bcrypt (passlib) |
| Rate Limiting | slowapi |
| Server | Uvicorn (ASGI) |
| CI/CD | GitHub Actions |

---

## Getting Started

### Prerequisites
- Python 3.14+
- pip

### Installation

Clone the repository and navigate to the project folder, create and activate a virtual environment, install dependencies with pip install -r requirements.txt, then start the server with python3 main.py.

---

## API Documentation

Once running, visit Swagger UI at http://127.0.0.1:8000/docs, ReDoc at http://127.0.0.1:8000/redoc, or the health check at http://127.0.0.1:8000/api/v1/health.

---

## Test Credentials

| Username | Password | Role |
|---|---|---|
| dr_smith | doctor123 | Doctor |
| admin_jane | admin123 | Admin |
| insurance_acme | insurance123 | Insurance |

---

## Security Testing

Unauthorized request with no token returns 401 Unauthorized. Invalid token returns 401 Unauthorized. Wrong role returns 403 Forbidden.

---

## Compliance Notes

This API demonstrates several HIPAA-relevant security patterns including minimum necessary access, audit logging of every request with timestamp and outcome, authentication required for all sensitive endpoints, and JWT token expiration after 30 minutes to limit exposure window.