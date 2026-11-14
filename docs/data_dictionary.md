# Recruitment Management System (RMS) - Data Dictionary

This document serves as the formal specification for all core entities, transaction tables, bridge entities, and event history logs within the Recruitment Management System, strictly fulfilling **Step 1** of the problem statement.

---

## 1. Department (`department`)
Represents functional business organizational units within the enterprise.

| Field Name | Type | Required / Optional | Allowed Values / Enum | Units | Uniqueness | Validation Rule |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `department_id` | Integer | Required | 1 to $N$ | Count | Unique (PK) | Auto-incrementing primary key |
| `name` | String | Required | Text (2–100 chars) | None | Unique | Department name must be unique |
| `description` | String | Optional | Text (max 500 chars) | None | Non-unique | Explanatory description |

---

## 2. Job Requisition (`jobrequisition`)
Master record representing an approved position opening requiring staffing.

| Field Name | Type | Required / Optional | Allowed Values / Enum | Units | Uniqueness | Validation Rule |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `requisition_id` | Integer | Required | 1 to $N$ | Count | Unique (PK) | Auto-incrementing primary key |
| `job_code` | String | Required | Pattern: `REQ-YYYY-NNNNNN` | Code | Unique | Deterministic formatting (e.g., `REQ-2026-000001`) |
| `job_title` | String | Required | Text (2–150 chars) | None | Non-unique | Valid job title |
| `department_id` | Integer | Required | Foreign Key | ID | Non-unique | Must reference valid `department.department_id` |
| `openings` | Integer | Required | $\ge 1$ | Count | Non-unique | Must be strictly positive integer |
| `min_salary` | Float | Required | $> 0$ | INR / Currency | Non-unique | Strictly positive |
| `max_salary` | Float | Required | $\ge \text{min\_salary}$ | INR / Currency | Non-unique | Must be greater than or equal to `min_salary` |
| `experience_required` | Float | Required | $\ge 0.0$ | Years | Non-unique | Minimum required experience in years |
| `status` | String | Required | `DRAFT`, `OPEN`, `ON_HOLD`, `CLOSED` | State | Non-unique | Must match allowed requisition lifecycle states |
| `created_at` | DateTime (UTC) | Required | Valid ISO 8601 Timestamp | UTC Time | Non-unique | Creation timestamp |

---

## 3. Skill (`skill`)
Catalog of technical, functional, and domain competencies.

| Field Name | Type | Required / Optional | Allowed Values / Enum | Units | Uniqueness | Validation Rule |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `skill_id` | Integer | Required | 1 to $N$ | Count | Unique (PK) | Auto-incrementing primary key |
| `skill_name` | String | Required | Text (1–100 chars) | None | Unique | Skill name must be unique across catalog |
| `category` | String | Optional | `Programming`, `Data`, `DevOps`, `Product`, `Domain` | Category | Non-unique | Competency classification |

---

## 4. Candidate (`candidate`)
Master profile of individual talent applying for requisitions.

| Field Name | Type | Required / Optional | Allowed Values / Enum | Units | Uniqueness | Validation Rule |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `candidate_id` | Integer | Required | 1 to $N$ | Count | Unique (PK) | Auto-incrementing primary key |
| `candidate_code` | String | Required | Pattern: `CAND-NNNNNN` | Code | Unique | Deterministic formatting (e.g., `CAND-000001`) |
| `full_name` | String | Required | Text (2–150 chars) | None | Non-unique | Synthetic full name |
| `email` | String | Required | Valid RFC 5322 Email | None | Unique | Globally unique valid email address |
| `phone` | String | Optional | International phone format | None | Non-unique | Valid telephone string |
| `education` | String | Optional | `PhD`, `Master's`, `Bachelor's`, `Diploma`, `Other` | Degree | Non-unique | Stated academic qualification |
| `total_experience` | Float | Required | $\ge 0.0$ | Years | Non-unique | Years of professional work experience |
| `created_at` | DateTime (UTC) | Required | Valid ISO 8601 Timestamp | UTC Time | Non-unique | Profile creation timestamp |

---

## 5. Candidate Skill (`candidateskill`)
Bridge table capturing many-to-many relationship between candidates and verified skills.

| Field Name | Type | Required / Optional | Allowed Values / Enum | Units | Uniqueness | Validation Rule |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `id` | Integer | Required | 1 to $N$ | Count | Unique (PK) | Auto-incrementing primary key |
| `candidate_id` | Integer | Required | Foreign Key | ID | Non-unique | Must reference valid `candidate.candidate_id` |
| `skill_id` | Integer | Required | Foreign Key | ID | Non-unique | Must reference valid `skill.skill_id` |
| `proficiency` | String | Required | `BEGINNER`, `INTERMEDIATE`, `ADVANCED`, `EXPERT` | Level | Non-unique | Standardized competency rating |

> **Compound Constraint**: Unique across (`candidate_id`, `skill_id`).

---

## 6. Resume Artifact (`resumeartifact`)
Master document metadata tracking uploaded resume files and extraction status.

| Field Name | Type | Required / Optional | Allowed Values / Enum | Units | Uniqueness | Validation Rule |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `resume_id` | Integer | Required | 1 to $N$ | Count | Unique (PK) | Auto-incrementing primary key |
| `candidate_id` | Integer | Required | Foreign Key | ID | Non-unique | Must reference valid `candidate.candidate_id` |
| `file_name` | String | Required | Text (e.g., `CAND_000001_Resume_v1.pdf`) | None | Non-unique | File basename |
| `file_type` | String | Required | `PDF`, `DOCX` | Extension | Non-unique | Allowed mime type extension |
| `file_path` | String | Optional | URI / Storage Path | Path | Non-unique | Relative filesystem or object storage path |
| `upload_date` | DateTime (UTC) | Required | Valid ISO 8601 Timestamp | UTC Time | Non-unique | Timestamp of upload |
| `extraction_status` | String | Required | `PENDING`, `PARSED`, `VERIFIED` | State | Non-unique | Resume parsing state |

---

## 7. Application (`application`)
Transactional link between a candidate and an open job requisition.

| Field Name | Type | Required / Optional | Allowed Values / Enum | Units | Uniqueness | Validation Rule |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `application_id` | Integer | Required | 1 to $N$ | Count | Unique (PK) | Auto-incrementing primary key |
| `application_code` | String | Required | Pattern: `APP-<job_code>-<candidate_code>` | Code | Unique | E.g. `APP-REQ-2026-000001-CAND-000001` |
| `candidate_id` | Integer | Required | Foreign Key | ID | Non-unique | Must reference valid `candidate.candidate_id` |
| `requisition_id` | Integer | Required | Foreign Key | ID | Non-unique | Must reference valid `jobrequisition.requisition_id` |
| `status` | String | Required | `APPLIED`, `SCREENING`, `SHORTLISTED`, `INTERVIEW`, `OFFER`, `REJECTED`, `WITHDRAWN` | State | Non-unique | Must follow strict transition policy |
| `applied_at` | DateTime (UTC) | Required | Valid ISO 8601 Timestamp | UTC Time | Non-unique | Timestamp application submitted |
| `screening_score` | Float | Optional | $0.0 \le x \le 100.0$ | Points | Non-unique | Derived score calculated strictly on job criteria |

> **Compound Constraint**: Unique across (`candidate_id`, `requisition_id`). Enforces single active application policy (EDGE-02).

---

## 8. Screening Rule (`screeningrule`)
Structured criteria configuration for scoring applications against job requirements.

| Field Name | Type | Required / Optional | Allowed Values / Enum | Units | Uniqueness | Validation Rule |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `rule_id` | Integer | Required | 1 to $N$ | Count | Unique (PK) | Auto-incrementing primary key |
| `requisition_id` | Integer | Required | Foreign Key | ID | Non-unique | Must reference valid `jobrequisition.requisition_id` |
| `criteria_name` | String | Required | Text (e.g. `REQUIRED_SKILLS`, `EXPERIENCE_FIT`) | None | Non-unique | Non-demographic job-related criterion |
| `weight` | Float | Required | $0 < x \le 100.0$ | Percentage | Non-unique | Weight percentage |
| `minimum_score` | Float | Optional | $0.0 \le x \le 100.0$ | Points | Non-unique | Minimum required threshold |
| `is_mandatory` | Boolean | Required | `TRUE`, `FALSE` | Boolean | Non-unique | If true, failing this criterion disqualifies candidate |

> **Reconciliation Rule**: For each requisition, $\sum \text{weight} = 100.0$.

---

## 9. Interviewer (`interviewer`)
Enterprise employee authorized to conduct interview rounds.

| Field Name | Type | Required / Optional | Allowed Values / Enum | Units | Uniqueness | Validation Rule |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `interviewer_id` | Integer | Required | 1 to $N$ | Count | Unique (PK) | Auto-incrementing primary key |
| `interviewer_code` | String | Required | Pattern: `IVR-NNNNNN` | Code | Unique | Deterministic formatting (e.g., `IVR-000001`) |
| `full_name` | String | Required | Text (2–150 chars) | None | Non-unique | Synthetic full name |
| `email` | String | Required | Valid RFC 5322 Email | None | Unique | Unique enterprise email |
| `department_id` | Integer | Required | Foreign Key | ID | Non-unique | Must reference valid `department.department_id` |
| `is_active` | Boolean | Required | `TRUE`, `FALSE` | Boolean | Non-unique | Inactive interviewers cannot be scheduled |

---

## 10. Interview (`interview`)
Scheduled round of technical, behavioral, or architectural evaluation.

| Field Name | Type | Required / Optional | Allowed Values / Enum | Units | Uniqueness | Validation Rule |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `interview_id` | Integer | Required | 1 to $N$ | Count | Unique (PK) | Auto-incrementing primary key |
| `interview_code` | String | Required | Pattern: `INT-YYYY-NNNNNN` | Code | Unique | Deterministic formatting (e.g., `INT-2026-000001`) |
| `application_id` | Integer | Required | Foreign Key | ID | Non-unique | Must reference valid `application.application_id` |
| `round_name` | String | Required | Text (e.g. `Technical Round 1`, `System Design`) | None | Non-unique | Round identifier |
| `scheduled_start` | DateTime (UTC) | Required | Valid ISO 8601 Timestamp | UTC Time | Non-unique | Must be strictly after application date |
| `scheduled_end` | DateTime (UTC) | Required | Valid ISO 8601 Timestamp | UTC Time | Non-unique | Must be strictly greater than `scheduled_start` |
| `status` | String | Required | `SCHEDULED`, `COMPLETED`, `CANCELLED`, `RESCHEDULED` | State | Non-unique | Interview lifecycle status |
| `created_at` | DateTime (UTC) | Required | Valid ISO 8601 Timestamp | UTC Time | Non-unique | Creation timestamp |

---

## 11. Interview Assignment (`interviewassignment`)
Panel bridge table assigning interviewers to interview rounds.

| Field Name | Type | Required / Optional | Allowed Values / Enum | Units | Uniqueness | Validation Rule |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `assignment_id` | Integer | Required | 1 to $N$ | Count | Unique (PK) | Auto-incrementing primary key |
| `interview_id` | Integer | Required | Foreign Key | ID | Non-unique | Must reference valid `interview.interview_id` |
| `interviewer_id` | Integer | Required | Foreign Key | ID | Non-unique | Must reference valid `interviewer.interviewer_id` |

> **Compound Constraint**: Unique across (`interview_id`, `interviewer_id`).  
> **Business Rule (EDGE-01)**: An interviewer cannot be assigned to two interviews that have overlapping time windows.

---

## 12. Feedback (`feedback`)
Structured multi-criteria assessment submitted by assigned interviewers.

| Field Name | Type | Required / Optional | Allowed Values / Enum | Units | Uniqueness | Validation Rule |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `feedback_id` | Integer | Required | 1 to $N$ | Count | Unique (PK) | Auto-incrementing primary key |
| `feedback_code` | String | Required | Pattern: `FB-<interview_id>-<interviewer_id>` | Code | Unique | Deterministic formatting |
| `interview_id` | Integer | Required | Foreign Key | ID | Non-unique | Must reference valid `interview.interview_id` |
| `interviewer_id` | Integer | Required | Foreign Key | ID | Non-unique | Must reference valid `interviewer.interviewer_id` (must be assigned) |
| `technical_score` | Float | Required | $0.0 \le x \le 10.0$ | Points | Non-unique | Technical competence score |
| `problem_solving_score` | Float | Required | $0.0 \le x \le 10.0$ | Points | Non-unique | Problem solving & reasoning score |
| `communication_score` | Float | Required | $0.0 \le x \le 10.0$ | Points | Non-unique | Communication & articulation score |
| `overall_score` | Float | Required | $0.0 \le x \le 10.0$ | Points | Non-unique | Derived weighted average |
| `recommendation` | String | Required | `STRONG_HIRE`, `HIRE`, `HOLD`, `NO_HIRE`, `STRONG_NO_HIRE` | Recommendation | Non-unique | Hiring recommendation |
| `comments` | String | Optional | Text | None | Non-unique | Structured notes and evaluation evidence |
| `submitted_at` | DateTime (UTC) | Required | Valid ISO 8601 Timestamp | UTC Time | Non-unique | Must be on or after interview end |

> **Compound Constraint**: Unique across (`interview_id`, `interviewer_id`). Enforces single feedback per interviewer per interview.

---

## 13. Offer (`offer`)
Employment offer proposal extended to candidates completing the evaluation pipeline.

| Field Name | Type | Required / Optional | Allowed Values / Enum | Units | Uniqueness | Validation Rule |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `offer_id` | Integer | Required | 1 to $N$ | Count | Unique (PK) | Auto-incrementing primary key |
| `offer_code` | String | Required | Pattern: `OFF-YYYY-NNNNNN` | Code | Unique | Deterministic formatting (e.g., `OFF-2026-000001`) |
| `application_id` | Integer | Required | Foreign Key | ID | Non-unique | Must reference valid `application.application_id` |
| `offered_salary` | Float | Required | $\text{min\_salary} \le x \le \text{max\_salary}$ | INR / Currency | Non-unique | **Enforces EDGE-04**: Must be within requisition salary band |
| `joining_date` | DateTime (UTC) | Optional | Valid ISO 8601 Timestamp | UTC Time | Non-unique | Anticipated start date |
| `status` | String | Required | `PENDING_APPROVAL`, `APPROVED`, `REJECTED`, `SENT`, `ACCEPTED`, `DECLINED` | State | Non-unique | Offer lifecycle state |
| `created_at` | DateTime (UTC) | Required | Valid ISO 8601 Timestamp | UTC Time | Non-unique | Offer generation timestamp |

---

## 14. Offer Approval History (`offerapprovalhistory`)
Immutable audit log recording decision checkpoints across the offer approval chain.

| Field Name | Type | Required / Optional | Allowed Values / Enum | Units | Uniqueness | Validation Rule |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `approval_id` | Integer | Required | 1 to $N$ | Count | Unique (PK) | Auto-incrementing primary key |
| `offer_id` | Integer | Required | Foreign Key | ID | Non-unique | Must reference valid `offer.offer_id` |
| `approver_id` | Integer | Optional | Integer | ID | Non-unique | ID of executive / process owner |
| `decision` | String | Required | `PENDING`, `APPROVED`, `REJECTED` | Decision | Non-unique | Approval decision recorded |
| `comments` | String | Optional | Text | None | Non-unique | Justification or conditions |
| `approved_at` | DateTime (UTC) | Required | Valid ISO 8601 Timestamp | UTC Time | Non-unique | Timestamp decision was finalized |

---

## 15. Application Stage History (`applicationstagehistory`)
Traceable event stream preserving historical state changes for candidate applications.

| Field Name | Type | Required / Optional | Allowed Values / Enum | Units | Uniqueness | Validation Rule |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `event_id` | Integer | Required | 1 to $N$ | Count | Unique (PK) | Auto-incrementing primary key |
| `application_id` | Integer | Required | Foreign Key | ID | Non-unique | Must reference valid `application.application_id` |
| `previous_status` | String | Optional | Application Lifecycle States | State | Non-unique | Null for initial `APPLIED` event |
| `new_status` | String | Required | Application Lifecycle States | State | Non-unique | Destination state |
| `changed_by` | String | Optional | System / Role Name | None | Non-unique | Actor or automated service triggering state change |
| `reason` | String | Optional | Text | None | Non-unique | Business or operational reason for state change |
| `changed_at` | DateTime (UTC) | Required | Valid ISO 8601 Timestamp | UTC Time | Non-unique | Event timestamp |
