# Recruitment Management System (RMS)

An end-to-end, enterprise-grade Recruitment Management System built with **FastAPI**, **SQLModel**, **PostgreSQL**, and a modern SPA frontend. The system manages the complete hiring lifecycle: job requisitions, candidate profiles, resume artifacts, structured criteria screening, interview panels with conflict prevention, multi-criteria feedback, and executive offer approvals with strict salary band enforcement.

---

## Table of Contents
1. [Business Workflow & Core Rules](#1-business-workflow--core-rules)
2. [Baseline Volume & Coverage](#2-baseline-volume--coverage)
3. [Injected Business Edge Cases & Ground Truth](#3-injected-business-edge-cases--ground-truth)
4. [Prerequisites](#4-prerequisites)
5. [Local Setup Guide (Step-by-Step for New Users)](#5-local-setup-guide-step-by-step-for-new-users)
   - [Method 1: Docker Compose (Quickest & Recommended)](#method-1-docker-compose-quickest--recommended)
   - [Method 2: Local Python & Virtual Environment](#method-2-local-python--virtual-environment)
6. [How to Test the Web Dashboard (Simple Step-by-Step Guide)](#6-how-to-test-the-web-dashboard-simple-step-by-step-guide)
7. [Running the Test Suite & Verification](#7-running-the-test-suite--verification)
8. [System Architecture & Ports](#8-system-architecture--ports)
9. [Troubleshooting & Common Questions](#9-troubleshooting--common-questions)
10. [Project Directory Map](#10-project-directory-map)

---

## 1. Business Workflow & Core Rules

1. **Master Data First**: Departments, approved Job Requisitions, verified Skills, Candidate profiles, and Resume Artifacts.
2. **Deterministic Nomenclature**:
   - Requisitions: `REQ-2026-000001`
   - Candidates: `CAND-000001`
   - Applications: `APP-<requisition-id>-<candidate-id>`
   - Interviews: `INT-2026-000001`
   - Feedback: `FB-<interview-id>-<interviewer-id>`
   - Offers: `OFF-2026-000001`
3. **Structured Screening**: Scores candidates strictly on stated job criteria (skills match, experience, education). Demographic proxies are excluded.
4. **Interviewer Availability & Conflict Prevention**: Detects and rejects overlapping interview assignments (`(Start_A < End_B) and (End_A > Start_B)`).
5. **Traceability & Auditability**: State changes are persisted as explicit events (`ApplicationStageHistory`, `OfferApprovalHistory`) rather than overwriting history.
6. **Compensation Compliance (EDGE-04)**: Rejects offer salaries outside approved requisition min and max bounds.

---

## 2. Baseline Volume & Coverage

Generated deterministically with fixed random seed **`20261022`**:

| Entity / Dataset | Table Name | Volume / Records | Status |
| :--- | :--- | :--- | :--- |
| **Departments** | `department` | 10 | Generated & Seeded |
| **Job Requisitions** | `jobrequisition` | 100 | Generated & Seeded |
| **Skills Catalog** | `skill` | 50 | Generated & Seeded |
| **Candidate Profiles** | `candidate` | 2,000 | Generated & Seeded |
| **Candidate Skills** | `candidateskill` | 9,035 | Generated & Seeded |
| **Resume Artifacts** | `resumeartifact` | 2,327 | Generated & Seeded |
| **Applications** | `application` | 3,000 | Generated & Seeded |
| **Screening Rules** | `screeningrule` | 400 | Generated & Seeded |
| **Interviewers** | `interviewer` | 50 | Generated & Seeded |
| **Interviews** | `interview` | 600 | Generated & Seeded |
| **Panel Assignments** | `interviewassignment` | 1,200 | Generated & Seeded |
| **Structured Feedback** | `feedback` | 1,000 | Generated & Seeded |
| **Offers** | `offer` | 150 | Generated & Seeded |
| **Offer Approval History** | `offerapprovalhistory` | 150 | Generated & Seeded |
| **Application Stage History** | `applicationstagehistory` | 7,559 | Generated & Seeded |

---

## 3. Injected Business Edge Cases & Ground Truth

All 5 required negative scenarios are explicitly injected, isolated in separate ground-truth files (`data/ground_truth/`), and audited:

1. **EDGE-01: Interviewer Schedule Conflict (`unavailable_interviewer_case.json`)**:
   - Interviewer #23 assigned to interview #1 (01:51–02:51 UTC) is prevented from double-booking for overlapping interview #2.
2. **EDGE-02: Duplicate Candidate Application (`duplicate_application_case.json`)**:
   - Candidate #27 attempting to apply a second time for requisition #38 is blocked with `HTTP 409 Conflict`.
3. **EDGE-03: Missing Feedback Stage Advancement (`missing_feedback_case.json`)**:
   - Interview #1 advanced to `OFFER` despite interviewer #2 not submitting required panel feedback.
4. **EDGE-04: Offer Salary Outside Approved Band (`salary_outside_band_case.json`)**:
   - Offer proposing ₹2,460,000 for requisition #43 (max band: ₹2,050,000) is rejected with `HTTP 422 Unprocessable Entity`.
5. **EDGE-05: Closed Requisition with Active Applications (`closed_requisition_active_applications.json`)**:
   - Requisition #24 (`REQ-2026-000024`) closed while 22 applications remain in active in-flight stages.

---

## 4. Prerequisites

Before running the project on any computer, make sure you have:

* **Git**: [Download Git](https://git-scm.com/downloads)
* **Docker Desktop**: [Download Docker Desktop](https://www.docker.com/products/docker-desktop/) *(Recommended)*
* **Python 3.10 - 3.12** *(Only needed if running outside Docker)*: [Download Python](https://www.python.org/downloads/)
* A modern web browser (Chrome, Edge, Firefox, or Safari)

---

## 5. Local Setup Guide (Step-by-Step for New Users)

Clone the repository to your local computer:

```bash
git clone https://github.com/Khansahab-ai/Recruitment-Management-System.git
cd Recruitment-Management-System
```

Choose **Method 1** (Docker) or **Method 2** (Local Python):

---

### Method 1: Docker Compose (Quickest & Recommended)

This method runs PostgreSQL, the FastAPI Backend, and the Nginx Frontend inside Docker containers with a single command.

#### Step 1: Start All Services
```bash
docker compose up -d --build
```

#### Step 2: Load the Seed Data into PostgreSQL
Run this one-time command to populate the database with the 15 tables and 3,000 baseline records:
```bash
docker compose exec backend python /app/scripts/load_data.py
```

#### Step 3: Open the Application
* **Frontend Web Dashboard**: Open [http://localhost:3000](http://localhost:3000)
* **Backend OpenAPI Docs**: Open [http://localhost:8000/docs](http://localhost:8000/docs)
* **API Health Status**: Open [http://localhost:8000/health/database](http://localhost:8000/health/database)

#### To Stop the Containers:
```bash
docker compose down
```

---

### Method 2: Local Python & Virtual Environment

Follow these steps if you want to run the Python backend directly on your host machine.

#### Step 1: Start PostgreSQL Database Container
Make sure Docker is running, then start the database service:
```bash
docker compose up -d db
```
*(The PostgreSQL database will be accessible on `localhost:5432` with user `recruitment_user` and password `dev_password_123`)*

#### Step 2: Create and Activate Python Virtual Environment

* **On Windows (PowerShell)**:
  ```powershell
  python -m venv .venv
  .\.venv\Scripts\Activate.ps1
  ```
  *(If you get a script permission error in PowerShell, run: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`)*

* **On macOS / Linux**:
  ```bash
  python3 -m venv .venv
  source .venv/bin/activate
  ```

#### Step 3: Install Required Python Packages
```bash
pip install -r backend/requirements.txt
pip install pytest
```

#### Step 4: Configure Environment Variables
Copy the example environment file:
* **Windows (PowerShell)**:
  ```powershell
  Copy-Item backend\.env.example backend\.env
  ```
* **macOS / Linux**:
  ```bash
  cp backend/.env.example backend/.env
  ```

#### Step 5: Initialize Database & Seed Baseline Data
Run the database loader script to create tables, populate all 15 master & event tables, and synchronize auto-increment IDs:

* **Windows (PowerShell)**:
  ```powershell
  $env:PYTHONPATH="backend"
  python scripts/load_data.py
  ```

* **macOS / Linux**:
  ```bash
  export PYTHONPATH="backend"
  python scripts/load_data.py
  ```

#### Step 6: Start the FastAPI Backend Server

* **Windows (PowerShell)**:
  ```powershell
  $env:PYTHONPATH="backend"
  uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
  ```

* **macOS / Linux**:
  ```bash
  export PYTHONPATH="backend"
  uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
  ```
*The backend API will now be running at [http://localhost:8000](http://localhost:8000)*.

#### Step 7: Start the Frontend Web UI
Open a **new terminal window** in the project root folder and run:

```bash
python -m http.server 3000 --directory frontend
```

Now open **[http://localhost:3000](http://localhost:3000)** in your browser!

---

## 6. How to Test the Web Dashboard (Simple Step-by-Step Guide)

Open your browser at **[http://localhost:3000](http://localhost:3000)**. Use the tabs across the top to test each workflow:

### Quick 5-Minute Testing Checklist:

```
[1. Dashboard Tab]     Check KPIs & Visual Recruitment Funnel
[2. Screening Tab]     Run Criteria Evaluation for Application #1
[3. Interviews Tab]    Click "+ Schedule Round" to advance candidate to INTERVIEW
[4. Feedback Tab]      Submit 3-Score Ratings & HIRE Recommendation
[5. Offers Tab]        Test Salary Band Policy Guardrail (EDGE-04)
[6. Audit Tab]         Review Injected Anomalies & Ground-Truth Matches
```

---

### Test 1: Check Live Dashboard & Hiring Funnel
1. Click the **"Dashboard"** tab.
2. **What to look for**:
   - The top cards display live metrics: **100+ Requisitions**, **3,000+ Applications**, **600+ Interviews**, and **Offer Acceptance Rate (%)**.
   - The visual **Recruitment Funnel** shows volume drop-offs from `APPLIED` $\rightarrow$ `SCREENING` $\rightarrow$ `INTERVIEW` $\rightarrow$ `OFFER`.
   - The **Department Performance** table details openings, applications, and time-to-hire across Engineering, Product, Sales, and Marketing.

---

### Test 2: Test Structured Candidate Screening
1. Click the **"Screening"** tab.
2. Enter **Application ID: `1`** (or `5`) into the input box.
3. Click the blue **"Evaluate Application"** button.
4. **What to look for**:
   - The screening engine calculates a weighted job fit score (0–100) based strictly on job criteria (Skills match, Experience, Education) with non-bias exclusions.
   - An itemized breakdown table shows evidence, weight %, raw score, and pass/fail status.

---

### Test 3: Schedule an Interview Round
1. Click the **"Interview Panels"** tab.
2. Click the **"+ Schedule Round"** button at the top right.
3. Enter:
   * **Application ID**: `1`
   * **Round Name**: Select `Technical Round 1` or `Coding Assessment`
   * Start and End times are pre-filled automatically.
4. Click **"Schedule Round"**.
5. **What to look for**:
   - A success alert confirms the created round code (e.g. `INT-2026-000601`).
   - The candidate automatically advances from `SCREENING` to the `INTERVIEW` stage in the applications table.

---

### Test 4: Submit Structured Interview Feedback
1. Click the **"Feedback"** tab.
2. Click the **"+ Submit Feedback"** button.
3. Enter:
   * **Interview ID**: `1`
   * **Interviewer ID**: `1`
   * Ratings (0-10): Technical (`9`), Problem Solving (`8.5`), Communication (`8`)
   * **Recommendation**: Select `STRONG_HIRE` or `HIRE`
   * **Comments**: e.g., "Demonstrated strong distributed systems knowledge."
4. Click **"Submit Feedback"**.
5. **What to look for**:
   - The overall weighted score is calculated and stored.
   - The feedback code (e.g. `FB-1-1`) appears in the Feedback table.

---

### Test 5: Test the Salary Band Guardrail (EDGE-04)
*This demonstrates that the system prevents offers that exceed or fall below the approved budget.*

1. Click the **"Offers & Approvals"** tab.
2. Click **"+ Propose Offer"**.
3. **Negative Test (Salary Band Policy Violation)**:
   * **Application ID**: `21` *(DevOps Engineer — Requisition salary band: ₹600,000 to ₹800,000)*
   * **Offered Annual Salary (INR)**: Enter `5000` *(or `2000000`, which is outside the band)*
   * Click **"Propose Offer"**.
   * **Result**: The system blocks the offer with an alert:
     ```text
     Offer Policy Blocked:
     Offered salary 5,000.00 is outside the approved salary band [600,000.00 - 800,000.00] for requisition REQ-2026-000009
     ```
4. **Positive Test (Compliant Offer Proposal)**:
   * Change **Offered Annual Salary (INR)** to `700000` *(within ₹600k–₹800k)*.
   * Click **"Propose Offer"**.
   * **Result**: The offer is successfully proposed with status **`PENDING_APPROVAL`**.
5. **Executive Approval**:
   * Find the newly proposed offer in the table.
   * Click the green **"Approve"** button. The offer transitions to `APPROVED`, the candidate moves to `OFFER` stage, and an approval event is logged in `offer_approval_history`!

---

### Test 6: Explore Injected Anomaly Audit & Ground Truth
1. Click the **"Audit / Exceptions"** tab.
2. **What to look for**:
   - Displays real-time detection of the 5 injected edge cases (interviewer double-booking, duplicate candidate applications, skipped feedback advancements, out-of-band salaries, and closed requisitions with active applications).
   - Each card displays the issue severity (`CRITICAL` or `WARNING`), affected entity ID, and policy explanation.
   - Click **"Re-scan Database"** to see the system audit all tables on demand.

---

## 7. Running the Test Suite & Verification

The project includes automated validation checks and a full integration test suite.

### 1. Run Data Integrity Validation (56 Checks)
Verifies foreign keys, primary key uniqueness, arithmetic balances, enum types, and ground-truth edge cases:
```bash
python data/validation/validate_data.py
```
> **Expected Result**: `56 checks passed, 0 failures (100% success rate)`

### 2. Run Step 10 Bit-for-Bit Reproducibility Verification
Regenerates the complete dataset and verifies identical SHA-256 hashes across runs:
```bash
python scripts/verify_reproducibility.py
```
> **Expected Result**: `36 of 36 files bit-for-bit identical (0 mismatches)`

### 3. Run Automated Pytest Suite (28 Tests)
Executes all end-to-end API tests across all workflows, conflict detection, screening scoring, and offer guardrails:

* **Windows (PowerShell)**:
  ```powershell
  $env:PYTHONPATH="backend"
  pytest tests/ -v
  ```

* **macOS / Linux**:
  ```bash
  export PYTHONPATH="backend"
  pytest tests/ -v
  ```
> **Expected Result**: `28 passed in ~1.5s`

---

## 8. System Architecture & Ports

| Service | Port | Description |
| :--- | :---: | :--- |
| **Frontend Dashboard** | `3000` | Single-page application UI for recruiters, hiring managers, and audit teams |
| **Backend REST API** | `8000` | FastAPI server powering 41 endpoints, business logic, screening engine, and audit scanner |
| **Swagger / OpenAPI Docs** | `8000` | Interactive endpoint testing at `http://localhost:8000/docs` |
| **PostgreSQL Database** | `5432` | Relational store with ACID constraints and foreign key relationships |

---

## 9. Troubleshooting & Common Questions

### 1. Port Already in Use (e.g. 5432, 8000, 3000)
If you already have a local PostgreSQL or process using port 5432:
* Stop the existing service or change the port mapping in `docker-compose.yml` (e.g. `"5433:5432"`).

### 2. "ModuleNotFoundError: No module named 'app'"
Make sure you set the `PYTHONPATH` before running scripts or backend:
* Windows PowerShell: `$env:PYTHONPATH="backend"`
* Linux / macOS: `export PYTHONPATH="backend"`

### 3. Resetting / Re-seeding the Database
If you want to completely wipe and recreate the database from scratch:
```powershell
$env:PYTHONPATH="backend"
python scripts/generate_data.py
python scripts/load_data.py
```

### 4. PowerShell "Running Scripts is Disabled on This System"
Run this command in an administrator PowerShell prompt:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

## 10. Project Directory Map

```
RecruitmentManagementSystem/
├── backend/
│   ├── app/
│   │   ├── api/v1/endpoints/  # 41 REST endpoints across all entities
│   │   ├── core/              # Settings & database configuration
│   │   ├── db/                # Engine & session management
│   │   ├── models/            # 15 SQLModel domain entities
│   │   ├── schemas/           # Pydantic input & output schemas
│   │   ├── services/          # Screening, Interview, Offer, Analytics, Audit logic
│   │   └── main.py            # FastAPI entry point & CORS configuration
│   ├── alembic.ini            # Database migration configuration
│   ├── requirements.txt       # Python production dependencies
│   └── .env.example           # Example environment variables
├── data/
│   ├── generated/             # Deterministic CSV, JSON & SQL seed data
│   ├── ground_truth/          # Ground truth edge cases (EDGE-01 to EDGE-05)
│   └── validation/            # 56 validation checks & automated reports
├── deployment/
│   ├── backend.Dockerfile     # Production backend container (Python 3.12-slim)
│   ├── frontend.Dockerfile    # Production frontend container (Nginx Alpine)
│   ├── nginx.conf             # Nginx reverse proxy routing
│   └── README.md
├── docs/
│   ├── data_dictionary.md     # Step 1 comprehensive data dictionary (15 tables)
│   ├── architecture.md        # System design, ERD diagram & state transitions
│   ├── api_reference.md       # Complete REST API manual
│   ├── reproducibility_report.md # Step 10 checksum verification report
│   └── source_manifest.json   # Step 9 provenance & lawful dataset manifest
├── frontend/                  # Responsive web dashboard
│   ├── css/styles.css
│   ├── js/app.js
│   └── index.html
├── scripts/
│   ├── generate_data.py       # Seeded synthetic data generator (Seed: 20261022)
│   ├── load_data.py           # Database loader & sequence synchronizer
│   └── verify_reproducibility.py # Step 10 double-run reproducibility verifier
├── tests/                     # 28 Pytest unit & integration tests
├── .dockerignore
├── .gitignore
├── docker-compose.yml         # Container orchestration (PostgreSQL + Backend + Frontend)
└── README.md
```

---

## License

This project is licensed under the MIT License. Developed for enterprise hiring lifecycle automation, structured screening, and compensation compliance.
