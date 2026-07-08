"""Render audit reports as human-readable Markdown."""

from survguard.schemas import AuditReport, RuleFinding


def _render_finding(finding: RuleFinding) -> str:
    lines = [
        f"### [{finding.severity.upper()}] {finding.title}",
        "",
        f"**Rule:** `{finding.rule_id}`  ",
        f"**Confidence:** {finding.confidence}",
        "",
        "**Evidence:**",
    ]
    for item in finding.evidence:
        lines.append(f"- {item.message}")
    lines.extend(
        [
            "",
            "**Suggested fix:**",
            finding.suggested_fix,
        ]
    )
    return "\n".join(lines)


def render_markdown_report(report: AuditReport) -> str:
    """Format an AuditReport as Markdown text."""
    n_models = len(report.models_checked)
    n_findings = len(report.findings)

    lines = [
        "# SurvGuard Audit Report",
        "",
        f"Models checked: {n_models}  ",
        f"Findings: {n_findings}",
    ]

    if not report.findings:
        lines.extend(
            [
                "",
                "No high-risk left-truncation issues detected.",
            ]
        )
    else:
        lines.extend(["", "## Findings", ""])
        for finding in report.findings:
            lines.append(_render_finding(finding))
            lines.append("")

    return "\n".join(lines).rstrip() + "\n"
