from datetime import datetime
from typing import Optional, Literal

from sqlmodel import SQLModel, Field


# -------------------------
# Department Schemas
# -------------------------

class DepartmentCreate(SQLModel):
    name: str = Field(min_length=2, max_length=100)
    description: Optional[str] = None


class DepartmentRead(SQLModel):
    department_id: int
    name: str
    description: Optional[str] = None


# -------------------------
# Job Requisition Schemas
# -------------------------

RequisitionStatus = Literal["DRAFT", "OPEN", "ON_HOLD", "CLOSED"]


class RequisitionCreate(SQLModel):
    job_title: str = Field(min_length=2)
    department_id: int
    openings: int = Field(gt=0)
    min_salary: float = Field(gt=0)
    max_salary: float = Field(gt=0)
    experience_required: float = Field(default=0, ge=0)


class RequisitionUpdate(SQLModel):
    job_title: Optional[str] = Field(default=None, min_length=2)
    department_id: Optional[int] = None
    openings: Optional[int] = Field(default=None, gt=0)
    min_salary: Optional[float] = Field(default=None, gt=0)
    max_salary: Optional[float] = Field(default=None, gt=0)
    experience_required: Optional[float] = Field(default=None, ge=0)
    status: Optional[RequisitionStatus] = None


class RequisitionRead(SQLModel):
    requisition_id: int
    job_code: str
    job_title: str
    department_id: int
    openings: int
    min_salary: float
    max_salary: float
    experience_required: float
    status: str
    created_at: datetime

from pydantic import EmailStr


# -------------------------
# Candidate Schemas
# -------------------------

class CandidateCreate(SQLModel):
    full_name: str = Field(min_length=2, max_length=150)
    email: EmailStr
    phone: Optional[str] = None
    education: Optional[str] = None
    total_experience: float = Field(default=0, ge=0)


class CandidateRead(SQLModel):
    candidate_id: int
    candidate_code: str
    full_name: str
    email: str
    phone: Optional[str] = None
    education: Optional[str] = None
    total_experience: float
    created_at: datetime


# -------------------------
# Application Schemas
# -------------------------

ApplicationStatus = Literal[
    "APPLIED",
    "SCREENING",
    "SHORTLISTED",
    "INTERVIEW",
    "OFFER",
    "REJECTED",
    "WITHDRAWN"
]


class ApplicationCreate(SQLModel):
    candidate_id: int
    requisition_id: int


class ApplicationRead(SQLModel):
    application_id: int
    application_code: str
    candidate_id: int
    requisition_id: int
    status: str
    applied_at: datetime
    screening_score: Optional[float] = None


class ApplicationStatusUpdate(SQLModel):
    status: ApplicationStatus
    changed_by: Optional[str] = None
    reason: Optional[str] = None


class ApplicationHistoryRead(SQLModel):
    event_id: int
    application_id: int
    previous_status: Optional[str] = None
    new_status: str
    changed_by: Optional[str] = None
    reason: Optional[str] = None
    changed_at: datetime


# -------------------------
# Skill & Candidate Skill Schemas
# -------------------------

class SkillCreate(SQLModel):
    skill_name: str = Field(min_length=1, max_length=100)
    category: Optional[str] = None


class SkillRead(SQLModel):
    skill_id: int
    skill_name: str
    category: Optional[str] = None


class CandidateSkillCreate(SQLModel):
    skill_id: int
    proficiency: Literal["BEGINNER", "INTERMEDIATE", "ADVANCED", "EXPERT"]


class CandidateSkillRead(SQLModel):
    id: int
    candidate_id: int
    skill_id: int
    proficiency: str
    skill_name: Optional[str] = None


# -------------------------
# Resume Artifact Schemas
# -------------------------

class ResumeArtifactCreate(SQLModel):
    candidate_id: int
    file_name: str
    file_type: str = "PDF"
    file_path: Optional[str] = None
    extraction_status: str = "PENDING"


class ResumeArtifactRead(SQLModel):
    resume_id: int
    candidate_id: int
    file_name: str
    file_type: str
    file_path: Optional[str] = None
    upload_date: datetime
    extraction_status: str


# -------------------------
# Screening Rule Schemas
# -------------------------

class ScreeningRuleCreate(SQLModel):
    requisition_id: int
    criteria_name: str
    weight: float = Field(gt=0, le=100)
    minimum_score: Optional[float] = Field(default=None, ge=0, le=100)
    is_mandatory: bool = False


class ScreeningRuleRead(SQLModel):
    rule_id: int
    requisition_id: int
    criteria_name: str
    weight: float
    minimum_score: Optional[float] = None
    is_mandatory: bool


class ScreeningEvaluationDetail(SQLModel):
    rule_id: int
    criteria_name: str
    weight: float
    raw_score: float
    weighted_score: float
    passed: bool
    comments: str


class ScreeningEvaluationResult(SQLModel):
    application_id: int
    candidate_id: int
    requisition_id: int
    total_score: float
    is_qualified: bool
    recommended_stage: str
    rule_breakdown: list[ScreeningEvaluationDetail]


# -------------------------
# Interviewer Schemas
# -------------------------

class InterviewerCreate(SQLModel):
    full_name: str = Field(min_length=2, max_length=150)
    email: EmailStr
    department_id: int
    is_active: bool = True


class InterviewerUpdate(SQLModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    department_id: Optional[int] = None
    is_active: Optional[bool] = None


class InterviewerRead(SQLModel):
    interviewer_id: int
    interviewer_code: str
    full_name: str
    email: str
    department_id: int
    is_active: bool


# -------------------------
# Interview & Assignment Schemas
# -------------------------

InterviewStatus = Literal["SCHEDULED", "COMPLETED", "CANCELLED", "RESCHEDULED"]


class InterviewCreate(SQLModel):
    application_id: int
    round_name: str
    scheduled_start: datetime
    scheduled_end: datetime


class InterviewUpdate(SQLModel):
    round_name: Optional[str] = None
    scheduled_start: Optional[datetime] = None
    scheduled_end: Optional[datetime] = None
    status: Optional[InterviewStatus] = None


class InterviewAssignmentCreate(SQLModel):
    interviewer_id: int


class InterviewAssignmentRead(SQLModel):
    assignment_id: int
    interview_id: int
    interviewer_id: int
    interviewer_name: Optional[str] = None
    interviewer_email: Optional[str] = None


class InterviewRead(SQLModel):
    interview_id: int
    interview_code: str
    application_id: int
    round_name: str
    scheduled_start: datetime
    scheduled_end: datetime
    status: str
    created_at: datetime
    assignments: list[InterviewAssignmentRead] = []


# -------------------------
# Feedback Schemas
# -------------------------

RecommendationType = Literal["STRONG_HIRE", "HIRE", "HOLD", "NO_HIRE", "STRONG_NO_HIRE"]


class FeedbackCreate(SQLModel):
    interview_id: int
    interviewer_id: int
    technical_score: float = Field(ge=0, le=10)
    problem_solving_score: float = Field(ge=0, le=10)
    communication_score: float = Field(ge=0, le=10)
    recommendation: RecommendationType
    comments: Optional[str] = None


class FeedbackRead(SQLModel):
    feedback_id: int
    feedback_code: str
    interview_id: int
    interviewer_id: int
    technical_score: float
    problem_solving_score: float
    communication_score: float
    overall_score: float
    recommendation: str
    comments: Optional[str] = None
    submitted_at: datetime


class FeedbackCompletenessCheck(SQLModel):
    interview_id: int
    application_id: int
    expected_feedback_count: int
    submitted_feedback_count: int
    is_complete: bool
    missing_interviewer_ids: list[int] = []


# -------------------------
# Offer & Approval Schemas
# -------------------------

OfferStatus = Literal["PENDING_APPROVAL", "APPROVED", "REJECTED", "SENT", "ACCEPTED", "DECLINED"]


class OfferCreate(SQLModel):
    application_id: int
    offered_salary: float = Field(gt=0)
    joining_date: Optional[datetime] = None


class OfferApprovalCreate(SQLModel):
    decision: Literal["APPROVED", "REJECTED"]
    approver_id: Optional[int] = None
    comments: Optional[str] = None


class OfferApprovalRead(SQLModel):
    approval_id: int
    offer_id: int
    approver_id: Optional[int] = None
    decision: str
    comments: Optional[str] = None
    approved_at: datetime


class OfferStatusUpdate(SQLModel):
    status: OfferStatus
    comments: Optional[str] = None


class OfferRead(SQLModel):
    offer_id: int
    offer_code: str
    application_id: int
    offered_salary: float
    joining_date: Optional[datetime] = None
    status: str
    created_at: datetime
    approvals: list[OfferApprovalRead] = []


# -------------------------
# Analytics & Exception Schemas
# -------------------------

class FunnelStageMetric(SQLModel):
    stage: str
    count: int
    conversion_rate_percent: float


class FunnelMetricsResponse(SQLModel):
    total_applications: int
    funnel: list[FunnelStageMetric]


class OperationalKPIsResponse(SQLModel):
    total_requisitions: int
    open_requisitions: int
    closed_requisitions: int
    total_candidates: int
    total_applications: int
    total_interviews: int
    total_offers: int
    accepted_offers: int
    offer_acceptance_rate_percent: float
    avg_screening_score: float
    avg_time_to_hire_days: float


class AnomalyItem(SQLModel):
    scenario_id: str
    scenario_name: str
    severity: str
    entity_type: str
    entity_id: str
    description: str
    details: dict


class ExceptionAuditReport(SQLModel):
    total_anomalies_detected: int
    ground_truth_matches: int
    anomalies: list[AnomalyItem]