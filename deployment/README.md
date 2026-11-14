# Deployment Guide

This directory contains containerization and deployment configurations for the Recruitment Management System.

---

## Architecture Overview

```
[ Browser / User ]
        |
        v  (Port 3000 / 80)
 [ Nginx Frontend Container ]
        |
        |-- Serves SPA Dashboard Assets (HTML/CSS/JS)
        |-- Reverse Proxies /api/* to Backend
        v
 [ FastAPI Backend Container (Port 8000) ]
        |
        v  (Port 5432)
 [ PostgreSQL 16 Database ]
```

---

## 1. Quick Start with Docker Compose

To spin up the entire recruitment system (PostgreSQL + FastAPI Backend + Nginx Frontend):

```bash
# From the project root:
docker compose up -d --build
```

Services will be accessible at:
- **Web UI Dashboard**: http://localhost:3000
- **API Documentation (Swagger UI)**: http://localhost:8000/docs
- **API Root**: http://localhost:8000/api/v1
- **PostgreSQL Database**: `localhost:5432` (`recruitment_user` / `dev_password_123`)

---

## 2. Local Development Setup (Without Docker Compose)

### 1. Database
Ensure the Postgres container is running:
```bash
docker compose up -d db
```

### 2. Backend
Activate Python virtual environment and run Uvicorn:
```bash
# Windows
.\.venv\Scripts\activate
$env:PYTHONPATH="backend"
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Frontend
Open `frontend/index.html` directly in any web browser, or serve it via python:
```bash
python -m http.server 3000 --directory frontend
```

---

## 3. Production Environment Variables

| Variable | Default Value | Description |
| :--- | :--- | :--- |
| `DATABASE_URL` | `postgresql+psycopg://recruitment_user:dev_password_123@localhost:5432/recruitment_db` | Connection string |
| `PROJECT_NAME` | `Recruitment Management System` | App title |
| `API_VERSION` | `1.0.0` | Semantic version |
