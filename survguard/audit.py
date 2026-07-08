"""Public audit API for SurvGuard."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from survguard.parsers.lifelines_parser import parse_lifelines_cox_models
from survguard.rules.left_truncation import check_left_truncation_missing
from survguard.schemas import AuditReport, DatasetSchema, StudyContext


def audit_code(
    code: str,
    column_names: list[str] | None = None,
    context: str | None = None,
) -> AuditReport:
    """
    Audit Python source code for survival-analysis methodological issues.

    Parses lifelines CoxPHFitter calls and runs configured rules against
    optional dataset column names and study context text.
    """
    models = parse_lifelines_cox_models(code)
    dataset_schema = DatasetSchema(columns=column_names or [])
    study_context = StudyContext(text=context)
    findings = check_left_truncation_missing(
        models=models,
        dataset_schema=dataset_schema,
        study_context=study_context,
    )
    return AuditReport(models_checked=models, findings=findings)


def _read_column_names_from_csv(data_path: str) -> list[str]:
    """Read column names from a CSV file without loading the full dataset."""
    df = pd.read_csv(data_path, nrows=5)
    return list(df.columns)


def audit_file(
    code_path: str,
    data_path: str | None = None,
    context_path: str | None = None,
) -> AuditReport:
    """
    Audit a Python analysis file, optionally using CSV columns and context text.

    Raises FileNotFoundError if code_path (or optional paths) do not exist.
    """
    code_file = Path(code_path)
    if not code_file.is_file():
        raise FileNotFoundError(f"Code file not found: {code_path}")

    code = code_file.read_text(encoding="utf-8")

    column_names: list[str] | None = None
    if data_path is not None:
        data_file = Path(data_path)
        if not data_file.is_file():
            raise FileNotFoundError(f"Data file not found: {data_path}")
        column_names = _read_column_names_from_csv(data_path)

    context: str | None = None
    if context_path is not None:
        context_file = Path(context_path)
        if not context_file.is_file():
            raise FileNotFoundError(f"Context file not found: {context_path}")
        context = context_file.read_text(encoding="utf-8")

    return audit_code(code=code, column_names=column_names, context=context)
