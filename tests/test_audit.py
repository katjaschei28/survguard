from survguard import audit_code


def test_audit_code_flags_bad_cox_fit():
    bad_code = """
from lifelines import CoxPHFitter
cph = CoxPHFitter()
cph.fit(df, duration_col="observed_time", event_col="event", formula="age + treatment")
"""
    report = audit_code(
        code=bad_code,
        column_names=[
            "patient_id",
            "entry_time",
            "observed_time",
            "event",
            "age",
            "treatment",
        ],
        context="Patients have delayed entry and entry_time marks when they enter observation.",
    )

    assert len(report.models_checked) == 1
    assert len(report.findings) == 1
    assert report.findings[0].rule_id == "left_truncation_missing"


def test_audit_code_passes_corrected_cox_fit():
    corrected_code = """
from lifelines import CoxPHFitter
cph = CoxPHFitter()
cph.fit(df, duration_col="observed_time", event_col="event", entry_col="entry_time", formula="age + treatment")
"""
    report = audit_code(
        code=corrected_code,
        column_names=[
            "patient_id",
            "entry_time",
            "observed_time",
            "event",
            "age",
            "treatment",
        ],
        context="Patients have delayed entry and entry_time marks when they enter observation.",
    )

    assert len(report.models_checked) == 1
    assert len(report.findings) == 0
