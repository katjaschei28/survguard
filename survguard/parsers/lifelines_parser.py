"""Parse lifelines CoxPHFitter.fit() calls from Python source code."""

from __future__ import annotations

import ast
from typing import Optional

from survguard.schemas import ModelSpec


def _literal_string(node: ast.AST) -> Optional[str]:
    """Return string value for string constants; otherwise unparse or None."""
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    try:
        return ast.unparse(node)
    except Exception:
        return None


def _parse_covariates(formula: Optional[str]) -> list[str]:
    if not formula:
        return []
    return [part.strip() for part in formula.split("+") if part.strip()]


def parse_lifelines_cox_models(code: str) -> list[ModelSpec]:
    """
    Extract lifelines CoxPHFitter.fit() calls from Python source code.

    Returns an empty list if the code has syntax errors or no matching calls.
    """
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return []

    models: list[ModelSpec] = []
    index = 0

    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        if not isinstance(node.func, ast.Attribute):
            continue
        if node.func.attr != "fit":
            continue

        kwargs: dict[str, Optional[str]] = {}
        for keyword in node.keywords:
            if keyword.arg is not None:
                kwargs[keyword.arg] = _literal_string(keyword.value)

        duration_col = kwargs.get("duration_col")
        event_col = kwargs.get("event_col")
        if not duration_col or not event_col:
            continue

        index += 1
        formula = kwargs.get("formula")
        try:
            raw_call = ast.unparse(node)
        except Exception:
            raw_call = None

        models.append(
            ModelSpec(
                model_id=f"cox_model_{index}",
                model_type="cox_ph",
                package="lifelines",
                duration_col=duration_col,
                event_col=event_col,
                entry_col=kwargs.get("entry_col"),
                formula=formula,
                covariates=_parse_covariates(formula),
                line_start=getattr(node, "lineno", None),
                line_end=getattr(node, "end_lineno", None),
                raw_call=raw_call,
            )
        )

    return models
