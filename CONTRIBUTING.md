# Contributing to SurvGuard

Thank you for your interest in SurvGuard. This project is an educational MVP focused on detecting common survival-analysis mistakes in code—not on implementing survival models.

## Getting started

```bash
git clone https://github.com/YOUR_GITHUB_USERNAME/survguard.git
cd survguard
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
pytest
```

Generate the left-truncation example data before running audits:

```bash
python examples/left_truncation/generate_data.py
```

## What we welcome

- New **rules** with clear evidence and conservative wording (e.g. "possible", not "definitely wrong")
- Parsers for additional modeling packages (still Python-first)
- Better tests and documentation
- Example datasets and walkthroughs

## What SurvGuard is not

- A replacement for `lifelines`, `scikit-survival`, or other modeling libraries
- A tool that claims certainty without evidence
- An AI-dependent product (rules must work without external APIs)

## Adding a new rule

1. Define detection logic in `survguard/rules/`
2. Add Pydantic schemas if needed in `survguard/schemas.py`
3. Wire the rule into `survguard/audit.py`
4. Add tests in `tests/`
5. Document the rule in `docs/`

Keep findings **evidence-linked**: cite code, data columns, and/or study context.

## Pull requests

- Keep changes focused and small when possible
- Include tests for new behavior
- Run `pytest` before submitting
- Use clear commit messages

## Questions

Open a GitHub issue for bugs, rule ideas, or discussion. For the left-truncation example, see [docs/left_truncation.md](docs/left_truncation.md).
