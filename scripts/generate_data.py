
import json
import random
from pathlib import Path
from datetime import datetime, timezone, timedelta

import numpy as np
import pandas as pd
from faker import Faker


# -------------------------------------------------
# 1. Configuration
# -------------------------------------------------

SEED = 20261022
YEAR = 2026
DATA_AS_OF = datetime(2026, 11, 14, tzinfo=timezone.utc)

random.seed(SEED)
np.random.seed(SEED)

fake = Faker("en_IN")
Faker.seed(SEED)

ROOT_DIR = Path(__file__).resolve().parent.parent

GENERATED_DIR = ROOT_DIR / "data" / "generated"
GENERATED_DIR.mkdir(parents=True, exist_ok=True)
GROUND_TRUTH_DIR = ROOT_DIR / "data" / "ground_truth"
GROUND_TRUTH_DIR.mkdir(parents=True, exist_ok=True)

# -------------------------------------------------
# 2. Department master data
# -------------------------------------------------

DEPARTMENTS = [
    ("Engineering", "Software and technology development"),
    ("Human Resources", "Recruitment and employee management"),
    ("Finance", "Financial planning and accounting"),
    ("Marketing", "Brand management and marketing"),
    ("Sales", "Business development and sales"),
    ("Operations", "Business operations and delivery"),
    ("Data Science", "Analytics and artificial intelligence"),
    ("Product", "Product strategy and management"),
    ("Customer Support", "Customer service and support"),
    ("Information Technology", "Infrastructure and IT services"),
]


def generate_departments():

    records = []

    for department_id, (name, description) in enumerate(
        DEPARTMENTS, start=1
    ):
        records.append({
            "department_id": department_id,
            "name": name,
            "description": description
        })

    return pd.DataFrame(records)


# -------------------------------------------------
# 3. Job requisition master data
# -------------------------------------------------

JOB_TITLES = [
    "Software Engineer",
    "Python Developer",
    "Data Analyst",
    "Data Scientist",
    "Machine Learning Engineer",
    "AI Engineer",
    "Backend Developer",
    "Frontend Developer",
    "DevOps Engineer",
    "Product Manager",
    "HR Executive",
    "Financial Analyst",
    "Business Analyst",
    "Cloud Engineer",
    "QA Engineer",
]

DEPARTMENT_IDS = list(range(1, len(DEPARTMENTS) + 1))


def generate_requisitions(count=100):

    records = []

    for requisition_id in range(1, count + 1):

        department_id = random.choice(DEPARTMENT_IDS)

        job_title = random.choice(JOB_TITLES)

        min_salary = random.randrange(
            300000, 1200000, 50000
        )

        max_salary = min_salary + random.randrange(
            200000, 1000000, 50000
        )

        created_at = fake.date_time_between(
            start_date=datetime(2026, 1, 1, tzinfo=timezone.utc),
            end_date=DATA_AS_OF,
            tzinfo=timezone.utc
        )

        status = random.choices(
            ["DRAFT", "OPEN", "ON_HOLD", "CLOSED"],
            weights=[10, 55, 10, 25],
            k=1
        )[0]

        records.append({
            "requisition_id": requisition_id,
            "job_code": f"REQ-{YEAR}-{requisition_id:06d}",
            "job_title": job_title,
            "department_id": department_id,
            "openings": random.randint(1, 5),
            "min_salary": min_salary,
            "max_salary": max_salary,
            "experience_required": round(
                random.uniform(0, 8), 1
            ),
            "status": status,
            "created_at": created_at.isoformat()
        })

    return pd.DataFrame(records)



# -------------------------------------------------
# 4. Skills master data
# -------------------------------------------------

SKILL_GROUPS = {
    "Programming": [
        "Python", "Java", "JavaScript", "C++", "C#",
        "SQL", "R", "Go", "TypeScript", "PHP"
    ],
    "AI_ML": [
        "Machine Learning", "Deep Learning", "NLP",
        "Computer Vision", "Generative AI", "LLMs",
        "TensorFlow", "PyTorch", "Scikit-learn", "LangChain"
    ],
    "Data": [
        "Pandas", "NumPy", "Power BI", "Tableau",
        "Excel", "Data Analysis", "Statistics",
        "Data Engineering", "Spark", "Data Visualization"
    ],
    "Cloud_DevOps": [
        "AWS", "Azure", "GCP", "Docker", "Kubernetes",
        "Git", "Linux", "CI/CD", "Terraform", "Jenkins"
    ],
    "Web_Backend": [
        "FastAPI", "Django", "Flask", "React",
        "Node.js", "REST APIs", "PostgreSQL",
        "MongoDB", "Redis", "Microservices"
    ]
}


def generate_skills():

    records = []
    skill_id = 1

    for category, skill_names in SKILL_GROUPS.items():

        for skill_name in skill_names:

            records.append({
                "skill_id": skill_id,
                "skill_name": skill_name,
                "category": category
            })

            skill_id += 1

    return pd.DataFrame(records)


# -------------------------------------------------
# 5. Candidate generation
# -------------------------------------------------

EDUCATION_LEVELS = [
    "Bachelor's Degree",
    "Master's Degree",
    "PhD",
    "Diploma",
    "Other"
]


def generate_candidates(count=2000):

    records = []

    for candidate_id in range(1, count + 1):

        created_at = fake.date_time_between(
            start_date=datetime(2025, 1, 1, tzinfo=timezone.utc),
            end_date=DATA_AS_OF,
            tzinfo=timezone.utc
        )

        records.append({
            "candidate_id": candidate_id,
            "candidate_code": f"CAND-{candidate_id:06d}",
            "full_name": fake.name(),
            "email": fake.unique.email(),
            "phone": fake.phone_number(),
            "education": random.choice(EDUCATION_LEVELS),
            "total_experience": round(
                random.uniform(0, 15), 1
            ),
            "created_at": created_at.isoformat()
        })

    return pd.DataFrame(records)


def generate_resume_artifacts(candidates_df):
    """
    Generate resume artifacts for candidates using an isolated deterministic RNG
    so downstream sequences for applications and interviews remain identical.
    """
    rng = random.Random(SEED + 999)
    records = []
    resume_id = 1
    file_types = ["PDF", "PDF", "PDF", "DOCX"]
    statuses = ["PARSED", "PARSED", "PARSED", "VERIFIED"]

    for _, row in candidates_df.iterrows():
        candidate_id = int(row["candidate_id"])
        cand_created = row["created_at"]

        # Each candidate has 1 resume; ~15% have an updated v2
        versions = [1, 2] if rng.random() < 0.15 else [1]
        for v in versions:
            ftype = rng.choice(file_types)
            fname = f"CAND_{candidate_id:06d}_Resume_v{v}.{ftype.lower()}"
            fpath = f"/storage/resumes/CAND_{candidate_id:06d}/{fname}"
            records.append({
                "resume_id": resume_id,
                "candidate_id": candidate_id,
                "file_name": fname,
                "file_type": ftype,
                "file_path": fpath,
                "upload_date": cand_created,
                "extraction_status": rng.choice(statuses)
            })
            resume_id += 1

    return pd.DataFrame(records)


# -------------------------------------------------
# 6. Candidate-skill relationships
# -------------------------------------------------

PROFICIENCY_LEVELS = [
    "BEGINNER",
    "INTERMEDIATE",
    "ADVANCED",
    "EXPERT"
]


def generate_candidate_skills(candidates_df, skills_df):

    records = []
    assignment_id = 1

    available_skill_ids = skills_df["skill_id"].tolist()

    for candidate_id in candidates_df["candidate_id"]:

        # Each candidate receives 3-6 distinct skills
        selected_skills = random.sample(
            available_skill_ids,
            random.randint(3, 6)
        )

        for skill_id in selected_skills:

            records.append({
                "id": assignment_id,
                "candidate_id": candidate_id,
                "skill_id": skill_id,
                "proficiency": random.choice(PROFICIENCY_LEVELS)
            })

            assignment_id += 1

    return pd.DataFrame(records)



# -------------------------------------------------
# 7. Application generation
# -------------------------------------------------

APPLICATION_STATUSES = [
    "APPLIED",
    "SCREENING",
    "SHORTLISTED",
    "INTERVIEW",
    "OFFER",
    "REJECTED",
    "WITHDRAWN"
]

APPLICATION_STATUS_WEIGHTS = [
    25, 20, 15, 15, 5, 15, 5
]


def generate_applications(
    candidates_df,
    requisitions_df,
    count=3000
):

    # Build all possible candidate-requisition pairs.
    # random.sample ensures every selected pair is unique.
    all_pairs = [
        (candidate_id, requisition_id)
        for candidate_id in candidates_df["candidate_id"]
        for requisition_id in requisitions_df["requisition_id"]
    ]

    if count > len(all_pairs):
        raise ValueError("Requested applications exceed available pairs.")

    selected_pairs = random.sample(all_pairs, count)

    candidate_lookup = candidates_df.set_index("candidate_id").to_dict("index")
    requisition_lookup = requisitions_df.set_index("requisition_id").to_dict("index")

    records = []

    for application_id, (candidate_id, requisition_id) in enumerate(
        selected_pairs, start=1
    ):

        candidate = candidate_lookup[candidate_id]
        requisition = requisition_lookup[requisition_id]

        # Application must occur after both candidate and requisition creation.
        candidate_created = datetime.fromisoformat(candidate["created_at"])
        requisition_created = datetime.fromisoformat(requisition["created_at"])

        start_date = max(candidate_created, requisition_created)

        applied_at = fake.date_time_between(
            start_date=start_date,
            end_date=DATA_AS_OF,
            tzinfo=timezone.utc
        )

        status = random.choices(
            APPLICATION_STATUSES,
            weights=APPLICATION_STATUS_WEIGHTS,
            k=1
        )[0]

        screening_score = (
            round(random.uniform(30, 100), 2)
            if status not in ["APPLIED", "WITHDRAWN"]
            else None
        )

        records.append({
            "application_id": application_id,
            "application_code": (
                f"APP-{requisition['job_code']}-"
                f"{candidate['candidate_code']}"
            ),
            "candidate_id": candidate_id,
            "requisition_id": requisition_id,
            "status": status,
            "applied_at": applied_at.isoformat(),
            "screening_score": screening_score
        })

    return pd.DataFrame(records)


# -------------------------------------------------
# 8. Duplicate application edge case
# -------------------------------------------------

def generate_duplicate_application_case(applications_df):

    # Select one existing valid application.
    existing = applications_df.iloc[0]

    scenario = {
        "scenario_id": "EDGE-02",
        "scenario_name": "DUPLICATE_APPLICATION",
        "description": (
            "A candidate attempts to apply again for the same requisition."
        ),
        "candidate_id": int(existing["candidate_id"]),
        "requisition_id": int(existing["requisition_id"]),
        "existing_application_code": existing["application_code"],
        "attempted_at": DATA_AS_OF.isoformat(),
        "expected_outcome": "REJECTED_BY_UNIQUE_CONSTRAINT",
        "is_valid_application": False
    }

    output_path = (
        GROUND_TRUTH_DIR / "duplicate_application_case.json"
    )

    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(scenario, file, indent=4)

    print(f"Generated edge case: {output_path}")


# -------------------------------------------------
# 9. Screening rule generation
# -------------------------------------------------

SCREENING_TEMPLATES = [
    [40, 25, 20, 15],
    [35, 30, 20, 15],
    [45, 25, 15, 15],
    [30, 35, 20, 15],
]

SCREENING_CRITERIA = [
    "REQUIRED_SKILLS",
    "RELEVANT_EXPERIENCE",
    "EDUCATION_RELEVANCE",
    "KEYWORD_RELEVANCE"
]

SCREENING_THRESHOLDS = [60, 50, 40, 30]


def generate_screening_rules(requisitions_df):

    records = []
    rule_id = 1

    for requisition_id in requisitions_df["requisition_id"]:

        weights = random.choice(SCREENING_TEMPLATES)

        for index, criteria in enumerate(SCREENING_CRITERIA):

            records.append({
                "rule_id": rule_id,
                "requisition_id": int(requisition_id),
                "criteria_name": criteria,
                "weight": weights[index],
                "minimum_score": SCREENING_THRESHOLDS[index],
                "is_mandatory": index == 0
            })

            rule_id += 1

    return pd.DataFrame(records)


# -------------------------------------------------
# 10. Interviewer generation
# -------------------------------------------------

def generate_interviewers(count=50):

    records = []

    for interviewer_id in range(1, count + 1):

        department_id = random.choice(DEPARTMENT_IDS)

        records.append({
            "interviewer_id": interviewer_id,
            "interviewer_code": f"IVR-{interviewer_id:06d}",
            "full_name": fake.name(),
            "email": fake.unique.email(),
            "department_id": department_id,
            "is_active": random.choices(
                [True, False],
                weights=[90, 10],
                k=1
            )[0]
        })

    return pd.DataFrame(records)



# -------------------------------------------------
# 11. Interview generation
# -------------------------------------------------

INTERVIEW_ROUNDS = [
    "TECHNICAL",
    "MANAGERIAL",
    "HR"
]


def generate_interviews(applications_df, count=600):

    eligible = applications_df[
        ~applications_df["status"].isin(
            ["REJECTED", "WITHDRAWN", "APPLIED"]
        )
    ].copy()

    eligible["applied_at_dt"] = pd.to_datetime(
        eligible["applied_at"], utc=True
    )

    # Ensure enough time exists between application and interview.
    eligible = eligible[
        eligible["applied_at_dt"] <= DATA_AS_OF - timedelta(hours=2)
    ]

    if len(eligible) < count:
        raise ValueError(
            f"Only {len(eligible)} eligible applications available."
        )

    selected = eligible.sample(
        n=count,
        random_state=SEED
    ).sort_values("applied_at_dt")

    records = []

    for interview_id, (_, application) in enumerate(
        selected.iterrows(), start=1
    ):

        applied_at = application["applied_at_dt"].to_pydatetime()

        scheduled_start = fake.date_time_between(
            start_date=applied_at,
            end_date=DATA_AS_OF - timedelta(hours=1),
            tzinfo=timezone.utc
        )

        scheduled_end = scheduled_start + timedelta(hours=1)

        records.append({
            "interview_id": interview_id,
            "interview_code": f"INT-{YEAR}-{interview_id:06d}",
            "application_id": int(application["application_id"]),
            "round_name": random.choice(INTERVIEW_ROUNDS),
            "scheduled_start": scheduled_start.isoformat(),
            "scheduled_end": scheduled_end.isoformat(),
            "status": "COMPLETED"
        })

    # Intentionally create an overlapping time slot
    # for the unavailable-interviewer test scenario.
    first_application = selected.iloc[0]["applied_at_dt"].to_pydatetime()
    second_application = selected.iloc[1]["applied_at_dt"].to_pydatetime()

    overlap_start = max(
        first_application,
        second_application
    ) + timedelta(minutes=5)

    overlap_end = overlap_start + timedelta(hours=1)

    for record in records[:2]:
        record["scheduled_start"] = overlap_start.isoformat()
        record["scheduled_end"] = overlap_end.isoformat()

    return pd.DataFrame(records)


# -------------------------------------------------
# 12. Interviewer assignments
# -------------------------------------------------

def generate_interview_assignments(
    interviews_df,
    interviewers_df
):

    active_interviewers = interviewers_df[
        interviewers_df["is_active"]
    ]["interviewer_id"].tolist()

    if len(active_interviewers) < 4:
        raise ValueError(
            "At least four active interviewers are required."
        )

    records = []
    assignment_id = 1

    # Reserve two interviewers for the first interview.
    first_pair = random.sample(active_interviewers, 2)

    for _, interview in interviews_df.iterrows():

        interview_id = int(interview["interview_id"])

        if interview_id == 1:
            selected_interviewers = first_pair

        elif interview_id == 2:
            # Do not assign the first interview's panel members.
            # This leaves them unavailable for the overlapping slot.
            available = [
                interviewer_id
                for interviewer_id in active_interviewers
                if interviewer_id not in first_pair
            ]

            selected_interviewers = random.sample(available, 2)

        else:
            selected_interviewers = random.sample(
                active_interviewers, 2
            )

        for interviewer_id in selected_interviewers:

            records.append({
                "assignment_id": assignment_id,
                "interview_id": interview_id,
                "interviewer_id": interviewer_id
            })

            assignment_id += 1

    return pd.DataFrame(records), first_pair


# -------------------------------------------------
# 13. Unavailable interviewer edge case
# -------------------------------------------------

def generate_unavailable_interviewer_case(
    interviews_df,
    interviewers_df,
    first_pair
):

    conflicting_interview = interviews_df[
        interviews_df["interview_id"] == 1
    ].iloc[0]

    target_interview = interviews_df[
        interviews_df["interview_id"] == 2
    ].iloc[0]

    interviewer_id = first_pair[0]

    interviewer = interviewers_df[
        interviewers_df["interviewer_id"] == interviewer_id
    ].iloc[0]

    scenario = {
        "scenario_id": "EDGE-01",
        "scenario_name": "INTERVIEWER_UNAVAILABLE",
        "description": (
            "An interviewer is already assigned to an interview "
            "during the requested time slot."
        ),
        "interviewer_id": int(interviewer_id),
        "interviewer_code": interviewer["interviewer_code"],
        "conflicting_interview_id": 1,
        "target_interview_id": 2,
        "conflicting_start": conflicting_interview["scheduled_start"],
        "conflicting_end": conflicting_interview["scheduled_end"],
        "attempted_start": target_interview["scheduled_start"],
        "attempted_end": target_interview["scheduled_end"],
        "expected_outcome": "REJECTED_INTERVIEWER_UNAVAILABLE",
        "assignment_persisted": False
    }

    output_path = (
        GROUND_TRUTH_DIR / "unavailable_interviewer_case.json"
    )

    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(scenario, file, indent=4)

    print(f"Generated edge case: {output_path}")



# -------------------------------------------------
# 14. Interview feedback generation
# -------------------------------------------------

def generate_feedback(
    interviews_df,
    interview_assignments_df,
    interviewers_df,
    applications_df,
    count=1000
):

    # Select one assignment that will deliberately have
    # missing feedback for our edge-case scenario.
    target_assignments = interview_assignments_df[
        interview_assignments_df["interview_id"] == 1
    ]

    if len(target_assignments) != 2:
        raise ValueError("Interview 1 must have exactly two interviewers.")

    missing_assignment = target_assignments.iloc[1]

    missing_interview_id = int(
        missing_assignment["interview_id"]
    )

    missing_interviewer_id = int(
        missing_assignment["interviewer_id"]
    )

    # Exclude this assignment from feedback generation.
    eligible_assignments = interview_assignments_df[
        ~(
            (interview_assignments_df["interview_id"] == missing_interview_id)
            &
            (interview_assignments_df["interviewer_id"] == missing_interviewer_id)
        )
    ].copy()

    if count > len(eligible_assignments):
        raise ValueError("Not enough eligible assignments for feedback.")

    # Select exactly 1,000 assignments deterministically.
    selected_assignments = eligible_assignments.sample(
        n=count,
        random_state=SEED
    )

    interview_lookup = interviews_df.set_index(
        "interview_id"
    ).to_dict("index")

    interviewer_lookup = interviewers_df.set_index(
        "interviewer_id"
    ).to_dict("index")

    records = []

    for feedback_id, (_, assignment) in enumerate(
        selected_assignments.iterrows(), start=1
    ):

        interview_id = int(assignment["interview_id"])
        interviewer_id = int(assignment["interviewer_id"])

        interview = interview_lookup[interview_id]
        interviewer = interviewer_lookup[interviewer_id]

        # Generate scores
        technical_score = round(random.uniform(3, 10), 1)
        problem_solving_score = round(random.uniform(3, 10), 1)
        communication_score = round(random.uniform(3, 10), 1)

        # Weighted overall score
        overall_score = round(
            technical_score * 0.4
            + problem_solving_score * 0.3
            + communication_score * 0.3,
            2
        )

        if overall_score >= 8:
            recommendation = "STRONG_HIRE"
        elif overall_score >= 7:
            recommendation = "HIRE"
        elif overall_score >= 5:
            recommendation = "HOLD"
        else:
            recommendation = "NO_HIRE"

        # Feedback is submitted after the interview ends.
        interview_end = datetime.fromisoformat(
            interview["scheduled_end"]
        )

        remaining_seconds = max(
            0,
            int((DATA_AS_OF - interview_end).total_seconds())
        )

        feedback_at = interview_end + timedelta(
            seconds=random.randint(0, remaining_seconds)
        )

        records.append({
            "feedback_id": feedback_id,
            "feedback_code": (
                f"FB-{interview['interview_code']}-"
                f"{interviewer['interviewer_code']}"
            ),
            "interview_id": interview_id,
            "interviewer_id": interviewer_id,
            "technical_score": technical_score,
            "problem_solving_score": problem_solving_score,
            "communication_score": communication_score,
            "overall_score": overall_score,
            "recommendation": recommendation,
            "comments": fake.sentence(),
            "submitted_at": feedback_at.isoformat()
        })

    feedback_df = pd.DataFrame(records)

    # -------------------------------------------------
    # Missing feedback edge case
    # -------------------------------------------------

    applications_df = applications_df.copy()

    target_interview = interviews_df[
        interviews_df["interview_id"] == missing_interview_id
    ].iloc[0]

    target_application_id = int(
        target_interview["application_id"]
    )

    # Deliberately advance the application despite
    # one interviewer not submitting feedback.
    applications_df.loc[
        applications_df["application_id"] == target_application_id,
        "status"
    ] = "OFFER"

    scenario = {
        "scenario_id": "EDGE-03",
        "scenario_name": "MISSING_FEEDBACK_STAGE_ADVANCED",
        "description": (
            "An application advances despite one interviewer "
            "not submitting the required feedback."
        ),
        "interview_id": missing_interview_id,
        "application_id": target_application_id,
        "missing_interviewer_id": missing_interviewer_id,
        "expected_feedback_count": 2,
        "actual_feedback_count": int(
            feedback_df[
                feedback_df["interview_id"] == missing_interview_id
            ].shape[0]
        ),
        "application_status": "OFFER",
        "expected_outcome": "FLAG_INCOMPLETE_FEEDBACK",
        "is_business_exception": True
    }

    output_path = (
        GROUND_TRUTH_DIR / "missing_feedback_case.json"
    )

    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(scenario, file, indent=4)

    print(f"Generated edge case: {output_path}")

    return feedback_df, applications_df



# -------------------------------------------------
# 15. Offer generation
# -------------------------------------------------

OFFER_STATUSES = [
    "PENDING_APPROVAL",
    "APPROVED",
    "REJECTED",
    "SENT",
    "ACCEPTED",
    "DECLINED"
]

OFFER_STATUS_WEIGHTS = [20, 35, 10, 15, 10, 10]


def generate_offers(
    applications_df,
    requisitions_df,
    count=150
):

    # Generate offers for applications that reached
    # the interview or offer stage.
    eligible = applications_df[
        applications_df["status"].isin(["INTERVIEW", "OFFER"])
    ].copy()

    if len(eligible) < count:
        raise ValueError(
            f"Only {len(eligible)} eligible applications available."
        )

    selected = eligible.sample(
        n=count,
        random_state=SEED
    )

    requisition_lookup = requisitions_df.set_index(
        "requisition_id"
    ).to_dict("index")

    records = []

    for offer_id, (_, application) in enumerate(
        selected.iterrows(), start=1
    ):

        requisition_id = int(application["requisition_id"])
        requisition = requisition_lookup[requisition_id]

        min_salary = float(requisition["min_salary"])
        max_salary = float(requisition["max_salary"])

        # Valid offers must remain within the approved salary band.
        offered_salary = round(
            random.uniform(min_salary, max_salary), 2
        )

        status = random.choices(
            OFFER_STATUSES,
            weights=OFFER_STATUS_WEIGHTS,
            k=1
        )[0]

        created_at = fake.date_time_between(
            start_date=datetime(2026, 1, 1, tzinfo=timezone.utc),
            end_date=DATA_AS_OF,
            tzinfo=timezone.utc
        )

        joining_date = created_at + timedelta(
            days=random.randint(30, 90)
        )

        records.append({
            "offer_id": offer_id,
            "offer_code": f"OFF-{YEAR}-{offer_id:06d}",
            "application_id": int(application["application_id"]),
            "offered_salary": offered_salary,
            "joining_date": joining_date.isoformat(),
            "status": status,
            "created_at": created_at.isoformat()
        })

    return pd.DataFrame(records)


# -------------------------------------------------
# 16. Offer approval history
# -------------------------------------------------

def generate_offer_approval_history(offers_df):

    records = []

    for approval_id, (_, offer) in enumerate(
        offers_df.iterrows(), start=1
    ):

        offer_status = offer["status"]

        if offer_status == "PENDING_APPROVAL":
            decision = "PENDING"

        elif offer_status == "REJECTED":
            decision = "REJECTED"

        else:
            decision = "APPROVED"

        records.append({
            "approval_id": approval_id,
            "offer_id": int(offer["offer_id"]),
            "approver_id": None,
            "decision": decision,
            "comments": (
                "Awaiting approval"
                if decision == "PENDING"
                else fake.sentence()
            ),
            "approved_at": offer["created_at"]
        })

    return pd.DataFrame(records)


# -------------------------------------------------
# 17. Salary outside approved band edge case
# -------------------------------------------------

def generate_salary_outside_band_case(
    offers_df,
    applications_df,
    requisitions_df
):

    # Select an existing valid offer as the reference.
    reference_offer = offers_df.iloc[0]

    application_id = int(
        reference_offer["application_id"]
    )

    application = applications_df[
        applications_df["application_id"] == application_id
    ].iloc[0]

    requisition_id = int(application["requisition_id"])

    requisition = requisitions_df[
        requisitions_df["requisition_id"] == requisition_id
    ].iloc[0]

    min_salary = float(requisition["min_salary"])
    max_salary = float(requisition["max_salary"])

    # Deliberately exceed the approved maximum salary.
    invalid_salary = round(max_salary * 1.20, 2)

    scenario = {
        "scenario_id": "EDGE-04",
        "scenario_name": "OFFER_OUTSIDE_APPROVED_SALARY_BAND",
        "description": (
            "An offer is proposed with a salary above "
            "the approved requisition salary range."
        ),
        "application_id": application_id,
        "requisition_id": requisition_id,
        "approved_min_salary": min_salary,
        "approved_max_salary": max_salary,
        "attempted_offered_salary": invalid_salary,
        "expected_outcome": "REJECTED_OUTSIDE_APPROVED_BAND",
        "offer_persisted": False,
        "is_business_exception": True
    }

    output_path = (
        GROUND_TRUTH_DIR / "salary_outside_band_case.json"
    )

    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(scenario, file, indent=4)

    print(f"Generated edge case: {output_path}")



def generate_closed_requisition_active_applications_case(
    requisitions_df,
    applications_df
):
    """
    Creates an exception where a closed requisition
    still has active applications.
    """

    # Identify the actual ID columns in the generated data
    requisition_id_col = (
        "requisition_id"
        if "requisition_id" in requisitions_df.columns
        else "id"
    )

    application_requisition_col = "requisition_id"

    active_statuses = [
        "APPLIED",
        "SCREENING",
        "SHORTLISTED",
        "INTERVIEW",
        "OFFER"
    ]

    active_apps = applications_df[
        applications_df["status"].isin(active_statuses)
    ]

    closed_requisitions = requisitions_df[
        requisitions_df["status"] == "CLOSED"
    ]

    matching_apps = active_apps[
        active_apps[application_requisition_col].isin(
            closed_requisitions[requisition_id_col]
        )
    ]

    # If no matching case exists, close a requisition
    # that currently has active applications.
    if matching_apps.empty:

        if active_apps.empty:
            raise ValueError(
                "No active applications available for EDGE-05"
            )

        requisition_id = int(
            active_apps.iloc[0][application_requisition_col]
        )

        requisitions_df.loc[
            requisitions_df[requisition_id_col] == requisition_id,
            "status"
        ] = "CLOSED"

        matching_apps = active_apps[
            active_apps[application_requisition_col] == requisition_id
        ]

    requisition_id = int(
        matching_apps.iloc[0][application_requisition_col]
    )

    req_active_apps = active_apps[
        active_apps[application_requisition_col] == requisition_id
    ]

    requisition = requisitions_df[
        requisitions_df[requisition_id_col] == requisition_id
    ].iloc[0]

    case = {
        "scenario_id": "EDGE-05",
        "scenario_name": "CLOSED_REQUISITION_WITH_ACTIVE_APPLICATIONS",
        "requisition_id": requisition_id,
        "requisition_code": requisition["job_code"],
        "active_application_ids": [
            int(x) for x in req_active_apps["application_id"].tolist()
        ],
        "active_application_count": len(req_active_apps),
        "expected_outcome": (
            "FLAG_ACTIVE_APPLICATIONS_ON_CLOSED_REQUISITION"
        ),
        "is_business_exception": True
    }

    output_path = (
        GROUND_TRUTH_DIR /
        "closed_requisition_active_applications.json"
    )

    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(case, file, indent=4, default=str)

    print(
        "Generated EDGE-05: Closed requisition with active applications"
    )

    return requisitions_df

def generate_application_stage_history(applications_df):
    """
    Creates a simple audit history for every application.
    The final history status matches the current application status.
    """

    stage_paths = {
        "APPLIED": ["APPLIED"],
        "SCREENING": ["APPLIED", "SCREENING"],
        "SHORTLISTED": ["APPLIED", "SCREENING", "SHORTLISTED"],
        "INTERVIEW": [
            "APPLIED", "SCREENING", "SHORTLISTED", "INTERVIEW"
        ],
        "OFFER": [
            "APPLIED", "SCREENING", "SHORTLISTED",
            "INTERVIEW", "OFFER"
        ],
        "REJECTED": ["APPLIED", "SCREENING", "REJECTED"],
        "WITHDRAWN": ["APPLIED", "WITHDRAWN"]
    }

    history = []
    event_id = 1

    for _, application in applications_df.iterrows():

        application_id = int(application["application_id"])
        current_status = application["status"]

        stages = stage_paths[current_status]

        applied_at = pd.to_datetime(
            application["applied_at"], utc=True
        )

        end_time = pd.Timestamp(DATA_AS_OF)

        duration = max(
            (end_time - applied_at).total_seconds(),
            0
        )

        for index, stage in enumerate(stages):

            previous_status = (
                stages[index - 1] if index > 0 else None
            )

            # Spread the events between application and data dates
            event_time = applied_at + pd.to_timedelta(
                duration * index / max(len(stages) - 1, 1),
                unit="s"
            )

            history.append({
                "id": event_id,
                "application_id": application_id,
                "previous_status": previous_status,
                "new_status": stage,
                "changed_by": (
                    "SYSTEM" if index == 0 else "RECRUITER"
                ),
                "reason": (
                    "Application submitted"
                    if index == 0
                    else f"Application moved to {stage}"
                ),
                "changed_at": event_time.isoformat()
            })

            event_id += 1

    return pd.DataFrame(history)


# -------------------------------------------------
# 4. Export datasets
# -------------------------------------------------

def export_dataset(df, filename):

    csv_path = GENERATED_DIR / f"{filename}.csv"
    json_path = GENERATED_DIR / f"{filename}.json"

    df.to_csv(csv_path, index=False)

    records = json.loads(
        df.to_json(orient="records", date_format="iso")
    )

    with open(json_path, "w", encoding="utf-8") as file:
        json.dump(records, file, indent=4, ensure_ascii=False)

    print(f"Generated: {filename}")
    print(f"  CSV:  {csv_path}")
    print(f"  JSON: {json_path}")
    print(f"  Rows: {len(df)}")


def export_unified_ground_truth():
    """
    Produce a consolidated ground_truth.json and ground_truth.csv combining
    all 5 negative scenarios / edge cases as required by Step 7 of the specification.
    """
    gt_specs = [
        ("EDGE-01", "unavailable_interviewer_case.json"),
        ("EDGE-02", "duplicate_application_case.json"),
        ("EDGE-03", "missing_feedback_case.json"),
        ("EDGE-04", "salary_outside_band_case.json"),
        ("EDGE-05", "closed_requisition_active_applications.json"),
    ]

    records = []
    for edge_id, filename in gt_specs:
        file_path = GROUND_TRUTH_DIR / filename
        if file_path.exists():
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                records.append({
                    "scenario_id": data.get("scenario_id", edge_id),
                    "scenario_name": data.get("scenario_name", ""),
                    "description": data.get("description", ""),
                    "expected_outcome": str(data.get("expected_outcome", "")),
                    "is_business_exception": bool(data.get("is_business_exception", True)),
                    "raw_details": json.dumps(data)
                })

    df = pd.DataFrame(records)
    csv_path = GROUND_TRUTH_DIR / "ground_truth.csv"
    json_path = GROUND_TRUTH_DIR / "ground_truth.json"

    df.to_csv(csv_path, index=False)
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=4, ensure_ascii=False)

    print(f"Generated: unified ground truth")
    print(f"  CSV:  {csv_path}")
    print(f"  JSON: {json_path}")


def export_sql_seed(datasets):
    """
    Export all datasets as SQL INSERT statements into data/generated/seed_data.sql
    as required by Step 9.
    """
    sql_path = GENERATED_DIR / "seed_data.sql"
    table_mapping = {
        "departments": "department",
        "job_requisitions": "jobrequisition",
        "skills": "skill",
        "candidates": "candidate",
        "candidate_skills": "candidateskill",
        "resume_artifacts": "resumeartifact",
        "applications": "application",
        "screening_rules": "screeningrule",
        "interviewers": "interviewer",
        "interviews": "interview",
        "interview_assignments": "interviewassignment",
        "feedback": "feedback",
        "offers": "offer",
        "offer_approval_history": "offerapprovalhistory",
        "application_stage_history": "applicationstagehistory",
    }

    with open(sql_path, "w", encoding="utf-8") as f:
        f.write("-- ====================================================\n")
        f.write("-- RECRUITMENT MANAGEMENT SYSTEM - SEED DATA\n")
        f.write(f"-- Deterministic Generation Seed: {SEED}\n")
        f.write(f"-- Generated At: {datetime.now(timezone.utc).isoformat()}\n")
        f.write("-- ====================================================\n\n")
        f.write("BEGIN;\n\n")

        for name, df in datasets:
            tbl = table_mapping.get(name, name)
            f.write(f"-- ---------------------------------------------------\n")
            f.write(f"-- Table: {tbl} ({len(df)} rows)\n")
            f.write(f"-- ---------------------------------------------------\n")
            cols = list(df.columns)
            cols_sql = [("event_id" if c == "id" and tbl == "applicationstagehistory" else c) for c in cols]
            col_list_str = ", ".join(cols_sql)

            for i in range(0, len(df), 500):
                chunk = df.iloc[i : i + 500]
                values_list = []
                for _, row in chunk.iterrows():
                    row_vals = []
                    for val in row:
                        if pd.isna(val) or val is None:
                            row_vals.append("NULL")
                        elif isinstance(val, (int, np.integer)):
                            row_vals.append(str(int(val)))
                        elif isinstance(val, (float, np.floating)):
                            row_vals.append(str(float(val)))
                        elif isinstance(val, bool):
                            row_vals.append("TRUE" if val else "FALSE")
                        else:
                            s = str(val).replace("'", "''")
                            row_vals.append(f"'{s}'")
                    values_list.append(f"({', '.join(row_vals)})")
                f.write(f"INSERT INTO {tbl} ({col_list_str}) VALUES\n" + ",\n".join(values_list) + ";\n")
            f.write("\n")

        f.write("COMMIT;\n")

    print(f"Generated: SQL seed data")
    print(f"  SQL:  {sql_path}")


def main():

    print("\nStarting synthetic data generation...")
    print(f"Random seed: {SEED}")

    # ------------------------------------------------
    # 1. Generate master data
    # ------------------------------------------------

    departments_df = generate_departments()

    requisitions_df = generate_requisitions(count=100)

    skills_df = generate_skills()

    candidates_df = generate_candidates(count=2000)

    resume_artifacts_df = generate_resume_artifacts(candidates_df)

    # ------------------------------------------------
    # 2. Generate candidate-related data
    # ------------------------------------------------

    candidate_skills_df = generate_candidate_skills(
        candidates_df,
        skills_df
    )

    applications_df = generate_applications(
        candidates_df,
        requisitions_df,
        count=3000
    )

    screening_rules_df = generate_screening_rules(
        requisitions_df
    )

    # ------------------------------------------------
    # 3. Generate interview data
    # ------------------------------------------------

    interviewers_df = generate_interviewers(count=50)

    interviews_df = generate_interviews(
        applications_df,
        count=600
    )

    interview_assignments_df, first_pair = (
        generate_interview_assignments(
            interviews_df,
            interviewers_df
        )
    )

    # ------------------------------------------------
    # 4. Generate feedback and offers
    # ------------------------------------------------

    feedback_df, applications_df = generate_feedback(
        interviews_df,
        interview_assignments_df,
        interviewers_df,
        applications_df,
        count=1000
    )

    offers_df = generate_offers(
        applications_df,
        requisitions_df,
        count=150
    )

    offer_approval_history_df = (
        generate_offer_approval_history(offers_df)
    )

    # ------------------------------------------------
    # 5. Generate all five business edge cases
    # ------------------------------------------------

    # EDGE-01: Duplicate application
    generate_duplicate_application_case(
        applications_df
    )

    # EDGE-02: Unavailable interviewer
    generate_unavailable_interviewer_case(
        interviews_df,
        interviewers_df,
        first_pair
    )

    # EDGE-03: Missing feedback
    # Generated inside generate_feedback()

    # EDGE-04: Salary outside approved band
    generate_salary_outside_band_case(
        offers_df,
        applications_df,
        requisitions_df
    )

    # EDGE-05: Closed requisition with active applications
    requisitions_df = (
        generate_closed_requisition_active_applications_case(
            requisitions_df,
            applications_df
        )
    )

    # ------------------------------------------------
    # 6. Generate application stage history
    # ------------------------------------------------

    application_history_df = (
        generate_application_stage_history(
            applications_df
        )
    )

    # ------------------------------------------------
    # 7. Export all datasets
    # ------------------------------------------------

    export_dataset(
        departments_df,
        "departments"
    )

    export_dataset(
        requisitions_df,
        "job_requisitions"
    )

    export_dataset(
        skills_df,
        "skills"
    )

    export_dataset(
        candidates_df,
        "candidates"
    )

    export_dataset(
        candidate_skills_df,
        "candidate_skills"
    )

    export_dataset(
        resume_artifacts_df,
        "resume_artifacts"
    )

    export_dataset(
        applications_df,
        "applications"
    )

    export_dataset(
        screening_rules_df,
        "screening_rules"
    )

    export_dataset(
        interviewers_df,
        "interviewers"
    )

    export_dataset(
        interviews_df,
        "interviews"
    )

    export_dataset(
        interview_assignments_df,
        "interview_assignments"
    )

    export_dataset(
        feedback_df,
        "feedback"
    )

    export_dataset(
        offers_df,
        "offers"
    )

    export_dataset(
        offer_approval_history_df,
        "offer_approval_history"
    )

    export_dataset(
        application_history_df,
        "application_stage_history"
    )

    # Export unified ground truth and SQL seed
    export_unified_ground_truth()

    all_tables = [
        ("departments", departments_df),
        ("job_requisitions", requisitions_df),
        ("skills", skills_df),
        ("candidates", candidates_df),
        ("candidate_skills", candidate_skills_df),
        ("resume_artifacts", resume_artifacts_df),
        ("applications", applications_df),
        ("screening_rules", screening_rules_df),
        ("interviewers", interviewers_df),
        ("interviews", interviews_df),
        ("interview_assignments", interview_assignments_df),
        ("feedback", feedback_df),
        ("offers", offers_df),
        ("offer_approval_history", offer_approval_history_df),
        ("application_stage_history", application_history_df),
    ]
    export_sql_seed(all_tables)

    # ------------------------------------------------
    # 8. Print generation summary
    # ------------------------------------------------

    print("\n========== DATA GENERATION SUMMARY ==========")

    print(f"Departments: {len(departments_df)}")
    print(f"Requisitions: {len(requisitions_df)}")
    print(f"Skills: {len(skills_df)}")
    print(f"Candidates: {len(candidates_df)}")
    print(f"Candidate Skills: {len(candidate_skills_df)}")
    print(f"Resume Artifacts: {len(resume_artifacts_df)}")
    print(f"Applications: {len(applications_df)}")
    print(f"Screening Rules: {len(screening_rules_df)}")
    print(f"Interviewers: {len(interviewers_df)}")
    print(f"Interviews: {len(interviews_df)}")
    print(f"Interview Assignments: {len(interview_assignments_df)}")
    print(f"Feedback: {len(feedback_df)}")
    print(f"Offers: {len(offers_df)}")
    print(f"Offer Approval History: {len(offer_approval_history_df)}")
    print(f"Application Stage History: {len(application_history_df)}")

    print("\nAll datasets generated successfully!")


if __name__ == "__main__":
    main()
