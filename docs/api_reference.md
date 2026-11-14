# API Reference Manual

The Recruitment Management System REST API is versioned under `/api/v1` and adheres strictly to OpenAPI 3.1 and JSON formatting standards.

---

## 1. System & Health Endpoints
- `GET /` — API root status.
- `GET /health` — Service health probe.
- `GET /health/database` — Direct database connection probe.

---

## 2. Master Data Endpoints

### Departments
- `GET /api/v1/departments/` — List all departments.
- `GET /api/v1/departments/{department_id}` — Get single department details.
- `POST /api/v1/departments/` — Create department.

### Job Requisitions
- `GET /api/v1/requisitions/` — List requisitions (optional filters: `department_id`, `status`, pagination).
- `GET /api/v1/requisitions/{requisition_id}` — Single requisition with department details.
- `POST /api/v1/requisitions/` — Create requisition (generates `REQ-YYYY-NNNNNN` business code).
- `PATCH /api/v1/requisitions/{requisition_id}` — Update requisition status or salary bounds.
- `POST /api/v1/requisitions/{requisition_id}/close` — Close requisition.

### Candidates
- `GET /api/v1/candidates/` — Search candidate profiles (search by name, email, code).
- `GET /api/v1/candidates/{candidate_id}` — Candidate details with associated skills and resumes.
- `POST /api/v1/candidates/` — Register synthetic candidate profile (`CAND-NNNNNN`).

### Skills & Competencies
- `GET /api/v1/skills/` — List skills catalog (filter by category).
- `POST /api/v1/skills/` — Add new skill competency.
- `GET /api/v1/skills/candidates/{candidate_id}` — View candidate verified skills.
- `POST /api/v1/skills/candidates/{candidate_id}` — Add skill and proficiency rating to candidate.

### Resume Artifacts
- `GET /api/v1/resumes/` — List resume document metadata (filter by `candidate_id`, `extraction_status`).
- `GET /api/v1/resumes/{resume_id}` — View specific resume artifact details.
- `POST /api/v1/resumes/` — Register resume metadata.

---

## 3. Workflow Transaction Endpoints

### Applications & Stage Progression
- `GET /api/v1/applications/` — Filter applications by candidate, requisition, or stage.
- `GET /api/v1/applications/{application_id}` — View application details.
- `POST /api/v1/applications/` — Submit candidate application (`APP-<job_code>-<candidate_code>`). Enforces duplicate application prevention.
- `PATCH /api/v1/applications/{application_id}/status` — Update stage following state machine policy; creates audit trail in `ApplicationStageHistory`.
- `GET /api/v1/applications/{application_id}/history` — Retrieve chronological stage audit timeline.

### Structured Screening & Scoring Engine
- `GET /api/v1/screening/rules` — List screening rules configured for requisitions.
- `POST /api/v1/screening/rules` — Create rule with weight and minimum threshold (enforces $\sum \text{weight} \le 100\%$).
- `POST /api/v1/screening/evaluate/{application_id}` — Run automated screening scoring based strictly on job criteria (skills match, experience, education). Updates application score and records stage progression.
- `GET /api/v1/screening/evaluation/{application_id}` — Detailed score breakdown by rule.

### Interviewers & Panels
- `GET /api/v1/interviewers/` — List interviewers by department and active status.
- `GET /api/v1/interviewers/{interviewer_id}` — View interviewer details.
- `POST /api/v1/interviewers/` — Register interviewer (`IVR-NNNNNN`).
- `GET /api/v1/interviewers/{interviewer_id}/schedule` — View interviewer booked slots.

### Interviews & Scheduling
- `GET /api/v1/interviews/` — List interviews with panel members.
- `GET /api/v1/interviews/{interview_id}` — Interview round details.
- `POST /api/v1/interviews/` — Schedule interview round (`INT-YYYY-NNNNNN`).
- `PATCH /api/v1/interviews/{interview_id}` — Reschedule or update round status.
- `POST /api/v1/interviews/{interview_id}/assign` — Assign panel member with **Interviewer Availability Conflict Prevention (EDGE-01)**.

### Feedback Collection
- `GET /api/v1/feedback/` — List feedback submissions.
- `POST /api/v1/feedback/` — Submit structured assessment (`FB-<interview_id>-<interviewer_id>`). Scores technical, problem solving, and communication (0–10).
- `GET /api/v1/feedback/completeness/{interview_id}` — Checks whether all panel members submitted feedback (detects EDGE-03).

### Offers & Approvals
- `GET /api/v1/offers/` — List employment offers.
- `GET /api/v1/offers/{offer_id}` — View offer details and approval audit history.
- `POST /api/v1/offers/` — Propose job offer with **Strict Salary Band Validation (EDGE-04)** against requisition min and max bounds.
- `POST /api/v1/offers/{offer_id}/approve` — Record executive approval decision in `OfferApprovalHistory`.
- `PATCH /api/v1/offers/{offer_id}/status` — Progress offer status (`SENT`, `ACCEPTED`, `DECLINED`).
- `GET /api/v1/offers/{offer_id}/history` — Retrieve immutable approval history.

---

## 4. Evaluation Metrics & Audit Endpoints

### Operational KPIs & Funnel Analytics
- `GET /api/v1/analytics/funnel` — Conversion counts and percentage drop-off across `APPLIED` $\rightarrow$ `ACCEPTED`.
- `GET /api/v1/analytics/kpis` — Total requisitions, open positions, candidate volume, interviews, offer acceptance rate, average time-to-hire.
- `GET /api/v1/analytics/departments` — Departmental performance comparison.

### Exception Scanner & Ground Truth Auditing
- `GET /api/v1/exceptions/detect` — Live anomaly scanner detecting EDGE-01 through EDGE-05 violations.
- `GET /api/v1/exceptions/ground-truth` — Ground-truth specifications and scenario parameters.
