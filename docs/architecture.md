# System Architecture & Technical Specification

## 1. System Overview

The Recruitment Management System (RMS) provides a robust, end-to-end platform for orchestrating enterprise hiring workflows. The system models requisitions, talent profiles, resumes, structured non-demographic screening, interviewer panel scheduling with real-time conflict detection, multi-criteria feedback collection, and offer approvals with salary band compliance enforcement.

---

## 2. Primary Actors & Role-Based Responsibilities

| Actor / System Role | Core Responsibilities | Typical Workflows Owned |
| :--- | :--- | :--- |
| **Business Requester** | Initiates staffing requests, specifies openings and target salary bands. | `POST /requisitions`, Draft Requisitions |
| **Process Owner** | Approves requisitions, defines structured screening rules, oversees interviews. | `POST /screening/rules`, `POST /interviews` |
| **Approver** | Reviews proposed employment offers, validates compensation against band limits. | `POST /offers/{id}/approve` |
| **Operations Analyst** | Tracks funnel metrics, time-to-hire, screening scores, and audits policy anomalies. | `GET /analytics/*`, `GET /exceptions/*` |
| **System Administrator** | Manages master data seeds, reproducibility verification, database migrations. | `POST /system/*`, Data generation |

---

## 3. Entity-Relationship Diagram (ERD)

```mermaid
erDiagram
    DEPARTMENT ||--o{ JOBREQUISITION : contains
    DEPARTMENT ||--o{ INTERVIEWER : employs
    JOBREQUISITION ||--o{ APPLICATION : receives
    JOBREQUISITION ||--o{ SCREENINGRULE : defines
    CANDIDATE ||--o{ APPLICATION : submits
    CANDIDATE ||--o{ CANDIDATESKILL : possesses
    SKILL ||--o{ CANDIDATESKILL : categorizes
    CANDIDATE ||--o{ RESUMEARTIFACT : attaches
    APPLICATION ||--o{ INTERVIEW : progresses_to
    APPLICATION ||--o{ OFFER : concludes_with
    APPLICATION ||--o{ APPLICATIONSTAGEHISTORY : logs_events
    INTERVIEW ||--o{ INTERVIEWASSIGNMENT : schedules
    INTERVIEWER ||--o{ INTERVIEWASSIGNMENT : assigned_to
    INTERVIEW ||--o{ FEEDBACK : receives
    INTERVIEWER ||--o{ FEEDBACK : authors
    OFFER ||--o{ OFFERAPPROVALHISTORY : logs_approvals

    DEPARTMENT {
        int department_id PK
        string name
        string description
    }

    JOBREQUISITION {
        int requisition_id PK
        string job_code UK
        string job_title
        int department_id FK
        int openings
        float min_salary
        float max_salary
        float experience_required
        string status
        datetime created_at
    }

    CANDIDATE {
        int candidate_id PK
        string candidate_code UK
        string full_name
        string email UK
        string education
        float total_experience
        datetime created_at
    }

    APPLICATION {
        int application_id PK
        string application_code UK
        int candidate_id FK
        int requisition_id FK
        string status
        float screening_score
        datetime applied_at
    }

    INTERVIEW {
        int interview_id PK
        string interview_code UK
        int application_id FK
        string round_name
        datetime scheduled_start
        datetime scheduled_end
        string status
    }

    OFFER {
        int offer_id PK
        string offer_code UK
        int application_id FK
        float offered_salary
        datetime joining_date
        string status
    }
```

---

## 4. Application Lifecycle State Machine

```mermaid
stateDiagram-v2
    [*] --> APPLIED : Application Submitted
    APPLIED --> SCREENING : Screening Engine Evaluates Rules
    APPLIED --> WITHDRAWN : Candidate Withdraws
    APPLIED --> REJECTED : Disqualified

    SCREENING --> SHORTLISTED : Score >= Threshold (60%)
    SCREENING --> REJECTED : Score < Threshold or Failed Mandatory

    SHORTLISTED --> INTERVIEW : Panel Scheduled
    SHORTLISTED --> REJECTED : Requisition Filled

    INTERVIEW --> OFFER : All Panel Feedback Positive (Hire)
    INTERVIEW --> REJECTED : Panel Recommends No Hire

    OFFER --> [*] : Offer Accepted or Closed
    REJECTED --> [*]
    WITHDRAWN --> [*]
```

---

## 5. Offer Approval State Machine

```mermaid
stateDiagram-v2
    [*] --> PENDING_APPROVAL : Offer Proposed (Within Salary Band)
    PENDING_APPROVAL --> APPROVED : Approver Signs Off
    PENDING_APPROVAL --> REJECTED : Approver Rejects

    APPROVED --> SENT : Extended to Candidate
    SENT --> ACCEPTED : Candidate Accepts
    SENT --> DECLINED : Candidate Declines
```

---

## 6. Policy Rules & Negative Scenarios (Edge Cases)

The architecture exposes policy decisions and retains auditability across 5 specific business exception vectors:

1. **EDGE-01: Interviewer Schedule Conflicts**
   - *Rule*: No interviewer may be assigned to concurrent overlapping interview rounds.
   - *Enforcement*: System calculates `(Start_A < End_B) and (End_A > Start_B)` and throws `409 Conflict`.
2. **EDGE-02: Duplicate Candidate Applications**
   - *Rule*: A candidate may apply only once per job requisition.
   - *Enforcement*: Unique compound constraint on `(candidate_id, requisition_id)` prevents duplicates.
3. **EDGE-03: Missing Feedback with Advanced Stage**
   - *Rule*: Candidate cannot advance to `OFFER` before all assigned panel interviewers submit structured feedback.
   - *Enforcement*: Automated audit service detects applications where `submitted_feedback < expected_feedback`.
4. **EDGE-04: Offer Salary Outside Approved Band**
   - *Rule*: Proposed compensation must reside strictly within `[requisition.min_salary, requisition.max_salary]`.
   - *Enforcement*: `POST /offers` validates salary bounds before persistence; throws `422 Unprocessable Entity` on violation.
5. **EDGE-05: Closed Requisitions with Active In-Flight Applications**
   - *Rule*: When a requisition status transitions to `CLOSED`, no candidate applications may remain in active states (`APPLIED`, `SCREENING`, `SHORTLISTED`, `INTERVIEW`, `OFFER`).
   - *Enforcement*: Audit scanner flags orphaned active applications on closed roles.
