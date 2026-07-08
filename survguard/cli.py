"""Command-line interface for SurvGuard."""

import typer

from survguard.audit import audit_file

app = typer.Typer(help="Bias-aware survival-analysis linting for clinician-scientists.")


@app.callback()
def main() -> None:
    """SurvGuard — bias-aware survival-analysis linting."""


@app.command()
def audit(
    code_path: str,
    data: str | None = typer.Option(None, "--data", "-d", help="CSV dataset path"),
    context: str | None = typer.Option(
        None, "--context", "-c", help="Study context text file"
    ),
):
    """Audit a survival analysis script for methodological issues."""
    try:
        report = audit_file(
            code_path=code_path,
            data_path=data,
            context_path=context,
        )
    except FileNotFoundError as exc:
        typer.echo(f"Error: {exc}", err=True)
        raise typer.Exit(code=1) from exc

    typer.echo(report.to_markdown())


if __name__ == "__main__":
    app()
