
import sys
from pathlib import Path
import pandas as pd
from sqlmodel import Session, delete
from sqlalchemy import text, DateTime, Integer, Date as SQLDate
from datetime import datetime

# =====================================================
# 1. PROJECT PATHS AND BACKEND IMPORTS
# =====================================================

ROOT_DIR = Path(__file__).resolve().parents[1]
BACKEND_DIR = ROOT_DIR / "backend"
GENERATED_DIR = ROOT_DIR / "data" / "generated"

# Add backend directory to Python import paths.
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

# Import backend models and database engine.
from app.db.session import engine
from app.models import (
    Department,
    JobRequisition,
    Candidate,
    Skill,
    CandidateSkill,
    ResumeArtifact,
    Application,
    ScreeningRule,
    Interviewer,
    Interview,
    InterviewAssignment,
    Feedback,
    Offer,
    ApplicationStageHistory,
    OfferApprovalHistory,
)


# =====================================================
# 2. DATASET LOADING ORDER
# =====================================================

DATASETS = [
    ("departments", Department),
    ("job_requisitions", JobRequisition),
    ("candidates", Candidate),
    ("skills", Skill),
    ("candidate_skills", CandidateSkill),
    ("resume_artifacts", ResumeArtifact),
    ("applications", Application),
    ("screening_rules", ScreeningRule),
    ("interviewers", Interviewer),
    ("interviews", Interview),
    ("interview_assignments", InterviewAssignment),
    ("feedback", Feedback),
    ("offers", Offer),
    ("application_stage_history", ApplicationStageHistory),
    ("offer_approval_history", OfferApprovalHistory),
]


# =====================================================
# 3. HELPER FUNCTIONS
# =====================================================

def load_csv(filename):
    file_path = GENERATED_DIR / f"{filename}.csv"

    if not file_path.exists():
        return None

    return pd.read_csv(file_path)


def clean_value(value):
    if pd.isna(value):
        return None

    if hasattr(value, "item"):
        return value.item()

    return value



def prepare_records(dataframe, model):
    """
    Convert CSV records into correctly typed SQLModel objects.
    Handles:
    - Missing values (NaN)
    - NumPy data types
    - Timezone-aware datetime fields
    - Date fields
    """

    model_columns = {
        column.name: column
        for column in model.__table__.columns
    }

    records = []

    for row in dataframe.to_dict(orient="records"):

        cleaned_row = {}

        for key, value in row.items():

            # Ignore columns that do not exist in the database model.
            if key not in model_columns:
                continue

            # Convert NaN and NumPy values.
            value = clean_value(value)

            if value is not None:

                column_type = model_columns[key].type

                # Detect standard and SQLModel custom datetime types.
                datetime_type = (
                    column_type
                    if isinstance(column_type, DateTime)
                    else getattr(column_type, "impl", None)
                )

                # Convert datetime strings into Python datetime objects.
                if isinstance(datetime_type, DateTime):

                    timestamp = pd.Timestamp(value)

                    if datetime_type.timezone:

                        if timestamp.tzinfo is None:
                            timestamp = timestamp.tz_localize("UTC")
                        else:
                            timestamp = timestamp.tz_convert("UTC")

                    else:

                        if timestamp.tzinfo is not None:
                            timestamp = timestamp.tz_localize(None)

                    value = timestamp.to_pydatetime()

                # Convert date strings into Python date objects.
                elif isinstance(column_type, SQLDate):

                    value = pd.to_datetime(value).date()

            cleaned_row[key] = value

        # Create the SQLModel object.
        records.append(model(**cleaned_row))

    return records


# =====================================================
# 4. MAIN DATABASE LOADING FUNCTION
# =====================================================

def main():

    print("\n======================================")
    print(" RECRUITMENT DATABASE LOADER")
    print("======================================\n")

    loaded_data = {}

    print("Reading generated CSV datasets...\n")

    # Prepare all datasets before starting the transaction.
    for filename, model in DATASETS:

        dataframe = load_csv(filename)

        if dataframe is None:

            if filename == "resume_artifacts":
                print("[SKIP] resume_artifacts.csv not generated.")
                continue

            raise FileNotFoundError(
                f"Missing required dataset: {filename}.csv"
            )

        records = prepare_records(dataframe, model)

        loaded_data[model] = records

        print(f"[READY] {filename}: {len(records)} records")

    models_in_order = [
        model for _, model in DATASETS
        if model in loaded_data
    ]

    print("\nStarting database transaction...")

    try:

        with Session(engine) as session:

            with session.begin():

                # -------------------------------------
                # 1. Clear existing records
                # -------------------------------------

                print("\nClearing existing development records...")

                for model in reversed(models_in_order):
                    session.exec(delete(model))

                session.flush()

                # -------------------------------------
                # 2. Insert records
                # -------------------------------------

                print("\nInserting records...\n")

                for filename, model in DATASETS:

                    if model not in loaded_data:
                        continue

                    records = loaded_data[model]

                    batch_size = 500

                    for start in range(0, len(records), batch_size):

                        batch = records[start:start + batch_size]

                        session.add_all(batch)
                        session.flush()

                    print(
                        f"[LOADED] {filename}: {len(records)} records"
                    )

            # Sync identity sequences to max(id) so subsequent inserts do not collide
            seq_maps = [
                ('department', 'department_id'),
                ('jobrequisition', 'requisition_id'),
                ('candidate', 'candidate_id'),
                ('skill', 'skill_id'),
                ('candidateskill', 'id'),
                ('resumeartifact', 'resume_id'),
                ('application', 'application_id'),
                ('screeningrule', 'rule_id'),
                ('interviewer', 'interviewer_id'),
                ('interview', 'interview_id'),
                ('interviewassignment', 'assignment_id'),
                ('feedback', 'feedback_id'),
                ('offer', 'offer_id'),
                ('offerapprovalhistory', 'approval_id'),
                ('applicationstagehistory', 'event_id'),
            ]
            for tbl, col in seq_maps:
                try:
                    session.execute(text(f"""
                        SELECT setval(
                            pg_get_serial_sequence('{tbl}', '{col}'),
                            COALESCE((SELECT MAX({col}) FROM {tbl}), 1)
                        );
                    """))
                except Exception:
                    pass

            print("\nTransaction committed successfully.")
            print("[SYNCED] All table primary key sequences aligned with current MAX(id).")

        print("\n======================================")
        print(" DATABASE LOADING SUCCESSFUL")
        print("======================================")

    except Exception as error:

        print("\n[ERROR] Database loading failed.")
        print("Transaction rolled back.")
        print(f"Reason: {error}")

        raise

    finally:
        engine.dispose()


if __name__ == "__main__":
    main()
