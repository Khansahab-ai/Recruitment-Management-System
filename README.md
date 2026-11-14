# Recruitment Management System (RMS)

An end-to-end, enterprise-grade Recruitment Management System built with **FastAPI**, **SQLModel**, **PostgreSQL**, and an interactive SPA frontend. The system manages the full hiring lifecycle: requisitions, candidate profiles, resume artifacts, structured criteria screening, interview panels with conflict prevention, multi-criteria feedback, and executive offer approvals with salary band enforcement.

---

## 1. Business Workflow & Core Rules

1. **Master Data First**: Departments, approved Job Requisitions, verified Skills, Candidate profiles, and Resume Artifacts.
2. **Deterministic IDs**: 
   - Requisitions: `REQ-2026-000001`
   - Candidates: `CAND-000001`
   - Applications: `APP-<requisition-id>-<candidate-id>`
   - Interviews: `INT-2026-000001`
   - Feedback: `FB-<interview-id>-<interviewer-id>`
   - Offers: `OFF-2026-000001`
3. **Structured Screening**: Scores candidates strictly on stated job criteria (skills match, experience, education). Demographic proxies are excluded.
4. **Interviewer Availability & Conflict Prevention**: Detects and rejects overlapping interview assignments.
5. **Traceability & Auditability**: State changes are persisted as explicit events (`ApplicationStageHistory`, `OfferApprovalHistory`) rather than overwriting history.
6. **Compensation Compliance**: Rejects offer salaries outside approved requisition min and max bounds.

---

## 2. Baseline Volume & Coverage

Generated deterministically with fixed random seed **`20261022`**:

| Entity / Dataset | Table Name | Volume / Records | Status |
| :--- | :--- | :--- | :--- |
| **Departments** | `department` | 10 | Generated & Loaded |
| **Job Requisitions** | `jobrequisition` | 100 | Generated & Loaded |
| **Skills Catalog** | `skill` | 50 | Generated & Loaded |
| **Candidate Profiles** | `candidate` | 2,000 | Generated & Loaded |
| **Candidate Skills** | `candidateskill` | 9,035 | Generated & Loaded |
| **Resume Artifacts** | `resumeartifact` | 2,327 | Generated & Loaded |
| **Applications** | `application` | 3,000 | Generated & Loaded |
| **Screening Rules** | `screeningrule` | 400 | Generated & Loaded |
| **Interviewers** | `interviewer` | 50 | Generated & Loaded |
| **Interviews** | `interview` | 600 | Generated & Loaded |
| **Panel Assignments** | `interviewassignment` | 1,200 | Generated & Loaded |
| **Structured Feedback** | `feedback` | 1,000 | Generated & Loaded |
| **Offers** | `offer` | 150 | Generated & Loaded |
| **Offer Approval History** | `offerapprovalhistory` | 150 | Generated & Loaded |
| **Application Stage History** | `applicationstagehistory` | 7,559 | Generated & Loaded |

---

## 3. Injected Business Edge Cases & Ground Truth

All 5 required negative scenarios are explicitly injected, isolated in separate ground-truth files (`data/ground_truth/`), and audited:

1. **EDGE-01: Interviewer Schedule Conflict (`unavailable_interviewer_case.json`)**:
   - Interviewer #23 assigned to interview #1 (01:51–02:51 UTC) is prevented from double-booking for overlapping interview #2.
2. **EDGE-02: Duplicate Candidate Application (`duplicate_application_case.json`)**:
   - Candidate #27 attempting to apply a second time for requisition #38 is blocked with HTTP 409 Conflict.
3. **EDGE-03: Missing Feedback Stage Advancement (`missing_feedback_case.json`)**:
   - Interview #1 advanced to `OFFER` despite interviewer #2 not submitting required panel feedback.
4. **EDGE-04: Offer Salary Outside Approved Band (`salary_outside_band_case.json`)**:
   - Offer proposing ₹2,460,000 for requisition #43 (max band: ₹2,050,000) is rejected with HTTP 422 Unprocessable Entity.
5. **EDGE-05: Closed Requisition with Active Applications (`closed_requisition_active_applications.json`)**:
   - Requisition #24 (`REQ-2026-000024`) closed while 22 applications remain in active in-flight stages.

---

## 4. Quick Start & Execution

### Option A: Full Stack with Docker Compose (Recommended)
```bash
docker compose up -d --build
```
- **Web UI Dashboard**: [http://localhost:3000](http://localhost:3000)
- **FastAPI Interactive Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **PostgreSQL Database**: `localhost:5432`

---

### Option B: Local Python Development
```bash
# 1. Activate Virtual Environment
.\.venv\Scripts\activate

# 2. Start PostgreSQL container
docker compose up -d db

# 3. Generate Synthetic Data (Fixed Seed: 20261022)
python scripts/generate_data.py

# 4. Load Data & Sync Identity Sequences
python scripts/load_data.py

# 5. Run 56 Data Validation Checks
python data/validation/validate_data.py

# 6. Verify Step 10 Bit-for-Bit Reproducibility
python scripts/verify_reproducibility.py

# 7. Run Comprehensive Pytest Test Suite
pytest tests/ -v

# 8. Start FastAPI Backend
$env:PYTHONPATH="backend"
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

---

## 5. Verification & Test Results

- **Data Integrity Validation**: **56 / 56 Checks Passed (100% Success)** (`data/validation/validation_summary.json`)
- **Step 10 Reproducibility Run**: **36 / 36 Files Bit-for-Bit Identical (0 Mismatches)** (`docs/reproducibility_report.md`)
- **Automated Test Suite**: **28 / 28 Pytest Tests Passed** across all endpoints, state machines, and edge cases.

---

## 6. Project Directory Map

```
RecruitmentManagementSystem/
├── backend/
│   ├── app/
│   │   ├── api/v1/endpoints/  # 41 REST endpoints across all entities
│   │   ├── core/              # Config & settings
│   │   ├── db/                # Engine & session management
│   │   ├── models/            # 15 SQLModel domain entities
│   │   ├── schemas/           # Pydantic/SQLModel input & output schemas
│   │   ├── services/          # Screening, Interview, Offer, Analytics, Audit logic
│   │   └── main.py            # FastAPI entry point & CORS
│   └── requirements.txt
├── data/
│   ├── generated/             # Deterministic CSV, JSON & SQL seed data
│   ├── ground_truth/          # Separate ground truth anomaly definitions
│   └── validation/            # Automated validation scripts & reports
├── deployment/
│   ├── backend.Dockerfile     # Production backend container
│   ├── frontend.Dockerfile    # Nginx SPA frontend container
│   ├── nginx.conf             # Reverse proxy config
│   └── README.md
├── docs/
│   ├── data_dictionary.md     # Step 1 comprehensive data dictionary
│   ├── architecture.md        # System design, ERD, and state machines
│   ├── api_reference.md       # Complete REST API manual
│   ├── reproducibility_report.md # Step 10 checksum verification report
│   └── source_manifest.json   # Step 9 provenance & dataset manifest
├── frontend/                  # Interactive HTML5/CSS3/Vanilla JS Dashboard
│   ├── css/styles.css
│   ├── js/app.js
│   └── index.html
├── scripts/
│   ├── generate_data.py       # Seeded synthetic generator
│   ├── load_data.py           # Database loader & sequence synchronizer
│   └── verify_reproducibility.py # Step 10 double-run reproducibility verifier
├── tests/                     # 28 Pytest unit & integration tests
├── docker-compose.yml         # Full multi-container orchestration
└── README.md
```
