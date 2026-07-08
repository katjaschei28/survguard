"""Rule: detect Cox models that may ignore left truncation / delayed entry."""

from __future__ import annotations

from survguard.schemas import (
    DatasetSchema,
    Evidence,
    ModelSpec,
    RuleFinding,
    StudyContext,
)


def check_left_truncation_missing(
    models: list[ModelSpec],
    dataset_schema: DatasetSchema,
    study_context: StudyContext | None = None,
) -> list[RuleFinding]:
    """
    Flag Cox PH models that omit entry_col when data or context suggest delayed entry.
    """
    context = study_context or StudyContext()
    entry_columns = dataset_schema.entry_like_columns()
    context_mentions = context.mentions_delayed_entry()
    findings: list[RuleFinding] = []

    for model in models:
        if model.model_type != "cox_ph":
            continue
        if not model.duration_col or not model.event_col:
            continue
        if model.entry_col:
            continue

        has_entry_evidence = bool(entry_columns) or context_mentions
        if not has_entry_evidence:
            continue

        if entry_columns and context_mentions:
            confidence = "high"
        else:
            confidence = "medium"

        evidence = [
            Evidence(
                source="code",
                message=(
                    f"Code uses lifelines CoxPHFitter with duration_col="
                    f"'{model.duration_col}' and event_col='{model.event_col}'."
                ),
            ),
            Evidence(
                source="code",
                message="Model fit does not include entry_col.",
            ),
        ]

        if entry_columns:
            cols_str = ", ".join(entry_columns)
            evidence.append(
                Evidence(
                    source="data",
                    message=f"Dataset contains entry-like column(s): {cols_str}.",
                )
            )

        if context_mentions:
            evidence.append(
                Evidence(
                    source="context",
                    message="Study context mentions delayed entry / left truncation.",
                )
            )

        if entry_columns:
            suggested_fix = (
                f"If patients enter observation after time zero, use "
                f"entry_col='{entry_columns[0]}' in CoxPHFitter.fit(), or use an "
                f"equivalent start-stop formulation."
            )
        else:
            suggested_fix = (
                "If patients enter observation after time zero, create an entry-time "
                "variable and pass it via entry_col in CoxPHFitter.fit(), or use an "
                "equivalent start-stop formulation."
            )

        findings.append(
            RuleFinding(
                rule_id="left_truncation_missing",
                severity="high",
                confidence=confidence,
                title="Possible left truncation ignored",
                evidence=evidence,
                suggested_fix=suggested_fix,
                model_id=model.model_id,
            )
        )

    return findings
