
import json
from pathlib import Path

import pandas as pd


# =====================================================
# 1. CONFIGURATION
# =====================================================

ROOT_DIR = Path(__file__).resolve().parents[2]

GENERATED_DIR = ROOT_DIR / "data" / "generated"
GROUND_TRUTH_DIR = ROOT_DIR / "data" / "ground_truth"
VALIDATION_DIR = ROOT_DIR / "data" / "validation"

VALIDATION_DIR.mkdir(parents=True, exist_ok=True)

results = []


# =====================================================
# 2. HELPER FUNCTIONS
# =====================================================

def load_dataset(filename):
    path = GENERATED_DIR / f"{filename}.csv"

    if not path.exists():
        raise FileNotFoundError(f"Dataset not found: {path}")

    return pd.read_csv(path)


def load_ground_truth(filename):
    path = GROUND_TRUTH_DIR / filename

    if not path.exists():
        raise FileNotFoundError(f"Ground truth not found: {path}")

    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def add_result(check_name, passed, details):
    results.append({
        "check": check_name,
        "status": "PASS" if passed else "FAIL",
        "details": str(details)
    })

    symbol = "PASS" if passed else "FAIL"

    print(f"[{symbol}] {check_name}: {details}")


def check_primary_key(df, column, dataset_name):
    passed = (
        column in df.columns
        and df[column].notna().all()
        and df[column].is_unique
    )

    add_result(
        f"Primary key - {dataset_name}",
        passed,
        f"Column: {column}, Rows: {len(df)}"
    )


def check_foreign_key(
    child_df,
    child_column,
    parent_df,
    parent_column,
    relationship_name
):
    if child_column not in child_df.columns:
        add_result(
            f"Foreign key - {relationship_name}",
            False,
            f"Missing child column: {child_column}"
        )
        return

    if parent_column not in parent_df.columns:
        add_result(
            f"Foreign key - {relationship_name}",
            False,
            f"Missing parent column: {parent_column}"
        )
        return

    valid_ids = set(parent_df[parent_column].dropna())

    invalid = child_df[
        child_df[child_column].isna()
        | ~child_df[child_column].isin(valid_ids)
    ]

    add_result(
        f"Foreign key - {relationship_name}",
        len(invalid) == 0,
        f"Invalid references: {len(invalid)}"
    )


# =====================================================
# 3. LOAD ALL DATASETS
# =====================================================

def main():

    print("\n======================================")
    print(" RECRUITMENT DATA VALIDATION")
    print("======================================\n")

    departments = load_dataset("departments")
    requisitions = load_dataset("job_requisitions")
    skills = load_dataset("skills")
    candidates = load_dataset("candidates")
    candidate_skills = load_dataset("candidate_skills")
    applications = load_dataset("applications")
    screening_rules = load_dataset("screening_rules")
    interviewers = load_dataset("interviewers")
    interviews = load_dataset("interviews")
    assignments = load_dataset("interview_assignments")
    feedback = load_dataset("feedback")
    offers = load_dataset("offers")
    approval_history = load_dataset("offer_approval_history")
    stage_history = load_dataset("application_stage_history")
    resume_artifacts = load_dataset("resume_artifacts")

    print("All datasets loaded successfully.\n")

    # =================================================
    # 4. PRIMARY KEY VALIDATION
    # =================================================

    print("\n--- PRIMARY KEY VALIDATION ---")

    primary_keys = [
        (departments, "department_id", "Departments"),
        (requisitions, "requisition_id", "Requisitions"),
        (skills, "skill_id", "Skills"),
        (candidates, "candidate_id", "Candidates"),
        (candidate_skills, "id", "Candidate Skills"),
        (resume_artifacts, "resume_id", "Resume Artifacts"),
        (applications, "application_id", "Applications"),
        (screening_rules, "rule_id", "Screening Rules"),
        (interviewers, "interviewer_id", "Interviewers"),
        (interviews, "interview_id", "Interviews"),
        (assignments, "assignment_id", "Interview Assignments"),
        (feedback, "feedback_id", "Feedback"),
        (offers, "offer_id", "Offers"),
        (approval_history, "approval_id", "Approval History"),
        (stage_history, "id", "Application Stage History")
    ]

    for df, column, name in primary_keys:
        check_primary_key(df, column, name)

    # =================================================
    # 5. FOREIGN KEY VALIDATION
    # =================================================

    print("\n--- FOREIGN KEY VALIDATION ---")

    foreign_keys = [
        (requisitions, "department_id",
         departments, "department_id", "Requisition -> Department"),

        (interviewers, "department_id",
         departments, "department_id", "Interviewer -> Department"),

        (candidate_skills, "candidate_id",
         candidates, "candidate_id", "Candidate Skill -> Candidate"),

        (candidate_skills, "skill_id",
         skills, "skill_id", "Candidate Skill -> Skill"),

        (resume_artifacts, "candidate_id",
         candidates, "candidate_id", "Resume Artifact -> Candidate"),

        (applications, "candidate_id",
         candidates, "candidate_id", "Application -> Candidate"),

        (applications, "requisition_id",
         requisitions, "requisition_id", "Application -> Requisition"),

        (screening_rules, "requisition_id",
         requisitions, "requisition_id", "Screening Rule -> Requisition"),

        (interviews, "application_id",
         applications, "application_id", "Interview -> Application"),

        (assignments, "interview_id",
         interviews, "interview_id", "Assignment -> Interview"),

        (assignments, "interviewer_id",
         interviewers, "interviewer_id", "Assignment -> Interviewer"),

        (feedback, "interview_id",
         interviews, "interview_id", "Feedback -> Interview"),

        (feedback, "interviewer_id",
         interviewers, "interviewer_id", "Feedback -> Interviewer"),

        (offers, "application_id",
         applications, "application_id", "Offer -> Application"),

        (approval_history, "offer_id",
         offers, "offer_id", "Approval History -> Offer"),

        (stage_history, "application_id",
         applications, "application_id", "Stage History -> Application")
    ]

    for child, child_col, parent, parent_col, name in foreign_keys:
        check_foreign_key(
            child,
            child_col,
            parent,
            parent_col,
            name
        )

    # =================================================
    # 6. DUPLICATE VALIDATION
    # =================================================

    print("\n--- DUPLICATE VALIDATION ---")

    duplicate_applications = applications.duplicated(
        subset=["candidate_id", "requisition_id"]
    ).sum()

    add_result(
        "Duplicate applications",
        duplicate_applications == 0,
        f"Duplicate pairs: {duplicate_applications}"
    )

    duplicate_assignments = assignments.duplicated(
        subset=["interview_id", "interviewer_id"]
    ).sum()

    add_result(
        "Duplicate interview assignments",
        duplicate_assignments == 0,
        f"Duplicate assignments: {duplicate_assignments}"
    )

    duplicate_feedback = feedback.duplicated(
        subset=["interview_id", "interviewer_id"]
    ).sum()

    add_result(
        "Duplicate interviewer feedback",
        duplicate_feedback == 0,
        f"Duplicate feedback records: {duplicate_feedback}"
    )

    # =================================================
    # 7. ENUM / STATUS VALIDATION
    # =================================================

    print("\n--- STATUS VALIDATION ---")

    valid_application_statuses = {
        "APPLIED",
        "SCREENING",
        "SHORTLISTED",
        "INTERVIEW",
        "OFFER",
        "REJECTED",
        "WITHDRAWN"
    }

    invalid_statuses = set(
        applications["status"].dropna()
    ) - valid_application_statuses

    add_result(
        "Application status values",
        len(invalid_statuses) == 0,
        f"Invalid statuses: {invalid_statuses}"
    )

    valid_requisition_statuses = {
        "DRAFT", "OPEN", "ON_HOLD", "CLOSED"
    }

    invalid_requisition_statuses = set(
        requisitions["status"].dropna()
    ) - valid_requisition_statuses

    add_result(
        "Requisition status values",
        len(invalid_requisition_statuses) == 0,
        f"Invalid statuses: {invalid_requisition_statuses}"
    )

    valid_offer_statuses = {
        "PENDING_APPROVAL",
        "APPROVED",
        "REJECTED",
        "SENT",
        "ACCEPTED",
        "DECLINED"
    }

    invalid_offer_statuses = set(
        offers["status"].dropna()
    ) - valid_offer_statuses

    add_result(
        "Offer status values",
        len(invalid_offer_statuses) == 0,
        f"Invalid statuses: {invalid_offer_statuses}"
    )

    valid_resume_types = {"PDF", "DOCX"}
    invalid_resume_types = set(resume_artifacts["file_type"].dropna()) - valid_resume_types
    add_result(
        "Resume artifact file types",
        len(invalid_resume_types) == 0,
        f"Invalid types: {invalid_resume_types}"
    )

    valid_resume_statuses = {"PARSED", "VERIFIED", "PENDING"}
    invalid_resume_statuses = set(resume_artifacts["extraction_status"].dropna()) - valid_resume_statuses
    add_result(
        "Resume artifact extraction status",
        len(invalid_resume_statuses) == 0,
        f"Invalid statuses: {invalid_resume_statuses}"
    )

    # =================================================
    # 8. SALARY VALIDATION
    # =================================================

    print("\n--- SALARY VALIDATION ---")

    invalid_requisition_salary = requisitions[
        requisitions["max_salary"] < requisitions["min_salary"]
    ]

    add_result(
        "Requisition salary range",
        len(invalid_requisition_salary) == 0,
        f"Invalid salary ranges: {len(invalid_requisition_salary)}"
    )

    offer_check = offers.merge(
        applications[["application_id", "requisition_id"]],
        on="application_id",
        how="left"
    ).merge(
        requisitions[
            ["requisition_id", "min_salary", "max_salary"]
        ],
        on="requisition_id",
        how="left"
    )

    invalid_offers = offer_check[
        (offer_check["offered_salary"] < offer_check["min_salary"])
        | (offer_check["offered_salary"] > offer_check["max_salary"])
    ]

    add_result(
        "Offer salary within approved band",
        len(invalid_offers) == 0,
        f"Invalid offers: {len(invalid_offers)}"
    )

    # =================================================
    # 9. SCREENING RULE VALIDATION
    # =================================================

    print("\n--- SCREENING RULE VALIDATION ---")

    weights = screening_rules.groupby(
        "requisition_id"
    )["weight"].sum()

    invalid_weights = weights[weights != 100]

    add_result(
        "Screening weights total 100",
        len(invalid_weights) == 0
        and len(weights) == len(requisitions),
        f"Requisitions with invalid weights: {len(invalid_weights)}"
    )

    invalid_individual_weights = screening_rules[
        (screening_rules["weight"] <= 0)
        | (screening_rules["weight"] > 100)
    ]

    add_result(
        "Individual screening weights",
        len(invalid_individual_weights) == 0,
        f"Invalid rules: {len(invalid_individual_weights)}"
    )

    # =================================================
    # 10. DATE VALIDATION
    # =================================================

    print("\n--- DATE VALIDATION ---")

    requisitions["created_at"] = pd.to_datetime(
        requisitions["created_at"], utc=True
    )

    candidates["created_at"] = pd.to_datetime(
        candidates["created_at"], utc=True
    )

    applications["applied_at"] = pd.to_datetime(
        applications["applied_at"], utc=True
    )

    interviews["scheduled_start"] = pd.to_datetime(
        interviews["scheduled_start"], utc=True
    )

    interviews["scheduled_end"] = pd.to_datetime(
        interviews["scheduled_end"], utc=True
    )

    feedback["submitted_at"] = pd.to_datetime(
        feedback["submitted_at"], utc=True
    )

    offers["created_at"] = pd.to_datetime(
        offers["created_at"], utc=True
    )

    offers["joining_date"] = pd.to_datetime(
        offers["joining_date"], utc=True
    )

    stage_history["changed_at"] = pd.to_datetime(
        stage_history["changed_at"],
        format="mixed",
        utc=True
    )

    # Application must be after candidate registration.
    application_dates = applications.merge(
        candidates[["candidate_id", "created_at"]].rename(
            columns={"created_at": "created_at_candidate"}
        ),
        on="candidate_id",
        how="left"
    ).merge(
        requisitions[["requisition_id", "created_at"]].rename(
            columns={"created_at": "created_at_requisition"}
        ),
        on="requisition_id",
        how="left"
    )

    invalid_application_dates = application_dates[
        (application_dates["applied_at"] < application_dates["created_at_candidate"])
        | (application_dates["applied_at"] < application_dates["created_at_requisition"])
    ]

    add_result(
        "Application creation dates",
        len(invalid_application_dates) == 0,
        f"Invalid applications: {len(invalid_application_dates)}"
    )

    invalid_interview_dates = interviews[
        interviews["scheduled_end"] <= interviews["scheduled_start"]
    ]

    add_result(
        "Interview start and end dates",
        len(invalid_interview_dates) == 0,
        f"Invalid interviews: {len(invalid_interview_dates)}"
    )

    interview_dates = interviews.merge(
        applications[["application_id", "applied_at"]],
        on="application_id"
    )

    invalid_interview_sequence = interview_dates[
        interview_dates["scheduled_start"] < interview_dates["applied_at"]
    ]

    add_result(
        "Interview after application",
        len(invalid_interview_sequence) == 0,
        f"Invalid interview sequences: {len(invalid_interview_sequence)}"
    )

    feedback_dates = feedback.merge(
        interviews[["interview_id", "scheduled_end"]],
        on="interview_id"
    )

    invalid_feedback_dates = feedback_dates[
        feedback_dates["submitted_at"] < feedback_dates["scheduled_end"]
    ]

    add_result(
        "Feedback submitted after interview",
        len(invalid_feedback_dates) == 0,
        f"Invalid feedback dates: {len(invalid_feedback_dates)}"
    )

    invalid_joining_dates = offers[
        offers["joining_date"] <= offers["created_at"]
    ]

    add_result(
        "Offer joining dates",
        len(invalid_joining_dates) == 0,
        f"Invalid joining dates: {len(invalid_joining_dates)}"
    )

    # =================================================
    # 11. APPLICATION STAGE HISTORY
    # =================================================

    print("\n--- APPLICATION HISTORY VALIDATION ---")

    applications_with_history = set(
        stage_history["application_id"]
    )

    all_application_ids = set(
        applications["application_id"]
    )

    missing_history = (
        all_application_ids - applications_with_history
    )

    add_result(
        "Every application has history",
        len(missing_history) == 0,
        f"Applications without history: {len(missing_history)}"
    )

    last_history = (
        stage_history.sort_values(
            ["application_id", "changed_at", "id"]
        )
        .groupby("application_id")
        .tail(1)
        .set_index("application_id")
    )

    current_status = applications.set_index(
        "application_id"
    )["status"]

    matching_statuses = (
        last_history["new_status"].reindex(
            current_status.index
        ) == current_status
    )

    add_result(
        "Final history matches application status",
        matching_statuses.all(),
        f"Mismatches: {(~matching_statuses).sum()}"
    )

    # =================================================
    # 12. INTERVIEW AND FEEDBACK VALIDATION
    # =================================================

    print("\n--- INTERVIEW VALIDATION ---")

    assigned_pairs = set(
        zip(
            assignments["interview_id"],
            assignments["interviewer_id"]
        )
    )

    feedback_pairs = set(
        zip(
            feedback["interview_id"],
            feedback["interviewer_id"]
        )
    )

    unassigned_feedback = feedback_pairs - assigned_pairs

    add_result(
        "Feedback belongs to assigned interviewer",
        len(unassigned_feedback) == 0,
        f"Invalid feedback assignments: {len(unassigned_feedback)}"
    )

    # =================================================
    # 13. FIVE EDGE CASE VALIDATION
    # =================================================

    print("\n--- EDGE CASE VALIDATION ---")

    # EDGE-01: Duplicate application attempt

    duplicate_case = load_ground_truth(
        "duplicate_application_case.json"
    )

    duplicate_exists = applications[
        (applications["candidate_id"] == duplicate_case["candidate_id"])
        & (
            applications["requisition_id"]
            == duplicate_case["requisition_id"]
        )
    ]

    add_result(
        "EDGE-01 Duplicate application scenario",
        len(duplicate_exists) == 1,
        f"Valid existing applications: {len(duplicate_exists)}"
    )

    # EDGE-02: Unavailable interviewer

    unavailable_case = load_ground_truth(
        "unavailable_interviewer_case.json"
    )

    conflicting_id = unavailable_case["conflicting_interview_id"]
    target_id = unavailable_case["target_interview_id"]
    unavailable_interviewer_id = unavailable_case["interviewer_id"]

    conflicting_interview = interviews[
        interviews["interview_id"] == conflicting_id
    ].iloc[0]

    target_interview = interviews[
        interviews["interview_id"] == target_id
    ].iloc[0]

    overlap_exists = (
        conflicting_interview["scheduled_start"]
        < target_interview["scheduled_end"]
        and target_interview["scheduled_start"]
        < conflicting_interview["scheduled_end"]
    )

    assigned_to_conflict = (
        (assignments["interview_id"] == conflicting_id)
        & (
            assignments["interviewer_id"]
            == unavailable_interviewer_id
        )
    ).any()

    assigned_to_target = (
        (assignments["interview_id"] == target_id)
        & (
            assignments["interviewer_id"]
            == unavailable_interviewer_id
        )
    ).any()

    edge_02_passed = (
        overlap_exists
        and assigned_to_conflict
        and not assigned_to_target
        and not unavailable_case["assignment_persisted"]
    )

    add_result(
        "EDGE-02 Unavailable interviewer",
        edge_02_passed,
        f"Overlapping: {overlap_exists}, "
        f"Already assigned: {assigned_to_conflict}, "
        f"New assignment persisted: {assigned_to_target}"
    )

    # EDGE-03: Missing feedback

    missing_feedback_case = load_ground_truth(
        "missing_feedback_case.json"
    )

    edge_interview_id = missing_feedback_case["interview_id"]

    expected_feedback = missing_feedback_case[
        "expected_feedback_count"
    ]

    actual_feedback = len(
        feedback[feedback["interview_id"] == edge_interview_id]
    )

    edge_application = applications[
        applications["application_id"]
        == missing_feedback_case["application_id"]
    ]

    edge_03_passed = (
        actual_feedback == missing_feedback_case["actual_feedback_count"]
        and actual_feedback < expected_feedback
        and len(edge_application) == 1
        and edge_application.iloc[0]["status"] == "OFFER"
    )

    add_result(
        "EDGE-03 Missing feedback",
        edge_03_passed,
        f"Expected: {expected_feedback}, "
        f"Actual: {actual_feedback}"
    )

    # EDGE-04: Salary outside approved band

    salary_case = load_ground_truth(
        "salary_outside_band_case.json"
    )

    edge_04_passed = (
        salary_case["attempted_offered_salary"]
        > salary_case["approved_max_salary"]
        and not salary_case["offer_persisted"]
    )

    add_result(
        "EDGE-04 Salary outside approved band",
        edge_04_passed,
        f"Attempted salary: {salary_case['attempted_offered_salary']}, "
        f"Maximum: {salary_case['approved_max_salary']}"
    )

    # EDGE-05: Closed requisition with active applications

    closed_case = load_ground_truth(
        "closed_requisition_active_applications.json"
    )

    closed_requisition = requisitions[
        requisitions["requisition_id"]
        == closed_case["requisition_id"]
    ]

    closed_active_apps = applications[
        (applications["requisition_id"] == closed_case["requisition_id"])
        & (
            applications["status"].isin([
                "APPLIED",
                "SCREENING",
                "SHORTLISTED",
                "INTERVIEW",
                "OFFER"
            ])
        )
    ]

    edge_05_passed = (
        len(closed_requisition) == 1
        and closed_requisition.iloc[0]["status"] == "CLOSED"
        and len(closed_active_apps) > 0
        and len(closed_active_apps)
        == closed_case["active_application_count"]
    )

    add_result(
        "EDGE-05 Closed requisition with active applications",
        edge_05_passed,
        f"Active applications: {len(closed_active_apps)}"
    )

    # =================================================
    # 14. GENERATE VALIDATION REPORT
    # =================================================

    print("\n======================================")
    print(" VALIDATION SUMMARY")
    print("======================================")

    report_df = pd.DataFrame(results)

    total_checks = len(report_df)

    passed_checks = len(
        report_df[report_df["status"] == "PASS"]
    )

    failed_checks = len(
        report_df[report_df["status"] == "FAIL"]
    )

    print(f"Total checks: {total_checks}")
    print(f"Passed: {passed_checks}")
    print(f"Failed: {failed_checks}")

    print("\nFinal status:", "SUCCESS" if failed_checks == 0 else "FAILED")

    # Save CSV report
    report_df.to_csv(
        VALIDATION_DIR / "validation_summary.csv",
        index=False
    )

    # Save JSON report
    report_json = {
        "total_checks": total_checks,
        "passed_checks": passed_checks,
        "failed_checks": failed_checks,
        "overall_status": (
            "SUCCESS" if failed_checks == 0 else "FAILED"
        ),
        "results": results
    }

    with open(
        VALIDATION_DIR / "validation_summary.json",
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(report_json, file, indent=4)

    print("\nValidation reports saved:")
    print(VALIDATION_DIR / "validation_summary.csv")
    print(VALIDATION_DIR / "validation_summary.json")


if __name__ == "__main__":
    main()
