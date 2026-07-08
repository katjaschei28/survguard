from survguard.rules.left_truncation import check_left_truncation_missing
from survguard.schemas import DatasetSchema, ModelSpec, StudyContext


def test_left_truncation_missing_with_entry_column_and_context():
    model = ModelSpec(
        model_id="cox_model_1",
        model_type="cox_ph",
        package="lifelines",
        duration_col="observed_time",
        event_col="event",
        entry_col=None,
    )
    dataset = DatasetSchema(columns=["patient_id", "entry_time", "observed_time", "event"])
    context = StudyContext(text="Patients have delayed entry and left truncation.")

    findings = check_left_truncation_missing(
        models=[model],
        dataset_schema=dataset,
        study_context=context,
    )

    assert len(findings) == 1
    assert findings[0].rule_id == "left_truncation_missing"
    assert findings[0].confidence == "high"
    assert findings[0].severity == "high"


def test_no_finding_when_entry_col_provided():
    model = ModelSpec(
        model_id="cox_model_1",
        model_type="cox_ph",
        package="lifelines",
        duration_col="observed_time",
        event_col="event",
        entry_col="entry_time",
    )
    dataset = DatasetSchema(columns=["patient_id", "entry_time", "observed_time", "event"])
    context = StudyContext(text="Patients have delayed entry and left truncation.")

    findings = check_left_truncation_missing(
        models=[model],
        dataset_schema=dataset,
        study_context=context,
    )

    assert len(findings) == 0


def test_no_finding_without_entry_evidence():
    model = ModelSpec(
        model_id="cox_model_1",
        model_type="cox_ph",
        package="lifelines",
        duration_col="observed_time",
        event_col="event",
        entry_col=None,
    )
    dataset = DatasetSchema(columns=["patient_id", "observed_time", "event"])
    context = StudyContext(text=None)

    findings = check_left_truncation_missing(
        models=[model],
        dataset_schema=dataset,
        study_context=context,
    )

    assert len(findings) == 0
