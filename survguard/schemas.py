from typing import Literal, Optional

from pydantic import BaseModel, Field

ENTRY_PATTERNS = [
    "entry",
    "start",
    "enrollment",
    "enrolment",
    "inclusion",
    "first_visit",
    "first_observation",
    "age_entry",
    "entry_age",
]

DELAYED_ENTRY_TERMS = [
    "left truncation",
    "left-truncation",
    "delayed entry",
    "delayed-entry",
    "entry time",
    "entry age",
    "age as time scale",
    "age timescale",
    "enrollment after",
    "enrolment after",
    "patients enter observation",
    "enter observation",
    "risk set after",
]


class Evidence(BaseModel):
    source: str
    message: str


class ModelSpec(BaseModel):
    model_id: str
    model_type: str
    package: Optional[str] = None
    duration_col: Optional[str] = None
    event_col: Optional[str] = None
    entry_col: Optional[str] = None
    formula: Optional[str] = None
    covariates: list[str] = Field(default_factory=list)
    line_start: Optional[int] = None
    line_end: Optional[int] = None
    raw_call: Optional[str] = None


class DatasetSchema(BaseModel):
    columns: list[str]

    def entry_like_columns(self) -> list[str]:
        """Return columns whose names suggest delayed entry / left truncation."""
        matches: list[str] = []
        for col in self.columns:
            col_lower = col.lower()
            for pattern in ENTRY_PATTERNS:
                if pattern in col_lower:
                    matches.append(col)
                    break
        return matches


class StudyContext(BaseModel):
    text: Optional[str] = None

    def mentions_delayed_entry(self) -> bool:
        """Return True if context text mentions delayed entry or left truncation."""
        if not self.text:
            return False
        text_lower = self.text.lower()
        return any(term in text_lower for term in DELAYED_ENTRY_TERMS)


class RuleFinding(BaseModel):
    rule_id: str
    severity: Literal["low", "medium", "high"]
    confidence: Literal["low", "medium", "high"]
    title: str
    evidence: list[Evidence]
    suggested_fix: str
    model_id: Optional[str] = None


class AuditReport(BaseModel):
    models_checked: list[ModelSpec]
    findings: list[RuleFinding]

    def to_markdown(self) -> str:
        from survguard.reports.markdown import render_markdown_report

        return render_markdown_report(self)
