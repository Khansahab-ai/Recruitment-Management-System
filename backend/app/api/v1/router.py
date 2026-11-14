from fastapi import APIRouter

from app.api.v1.endpoints import (
    system,
    departments,
    requisitions,
    candidates,
    applications,
    skills,
    resumes,
    screening,
    interviewers,
    interviews,
    feedback,
    offers,
    analytics,
    exceptions
)

api_router = APIRouter()

api_router.include_router(
    system.router,
    prefix="/system",
    tags=["System"]
)

api_router.include_router(
    departments.router,
    prefix="/departments",
    tags=["Departments"]
)

api_router.include_router(
    requisitions.router,
    prefix="/requisitions",
    tags=["Job Requisitions"]
)

api_router.include_router(
    candidates.router,
    prefix="/candidates",
    tags=["Candidates"]
)

api_router.include_router(
    applications.router,
    prefix="/applications",
    tags=["Applications"]
)

api_router.include_router(
    skills.router,
    prefix="/skills",
    tags=["Skills & Competencies"]
)

api_router.include_router(
    resumes.router,
    prefix="/resumes",
    tags=["Resume Artifacts"]
)

api_router.include_router(
    screening.router,
    prefix="/screening",
    tags=["Screening & Scoring"]
)

api_router.include_router(
    interviewers.router,
    prefix="/interviewers",
    tags=["Interviewers"]
)

api_router.include_router(
    interviews.router,
    prefix="/interviews",
    tags=["Interviews & Panel Scheduling"]
)

api_router.include_router(
    feedback.router,
    prefix="/feedback",
    tags=["Feedback & Evaluations"]
)

api_router.include_router(
    offers.router,
    prefix="/offers",
    tags=["Offers & Approvals"]
)

api_router.include_router(
    analytics.router,
    prefix="/analytics",
    tags=["Recruitment Analytics & KPIs"]
)

api_router.include_router(
    exceptions.router,
    prefix="/exceptions",
    tags=["Auditing & Policy Exceptions"]
)