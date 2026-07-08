<p align="center">
  <img src="docs/assets/logo.png" alt="SurvGuard — bias-aware survival analysis" width="360">
</p>

# SurvGuard

![Tests](https://github.com/katjaschei28/survguard/actions/workflows/tests.yml/badge.svg)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

**SurvGuard is a proof-of-concept survival-analysis linter that detects when Cox model code may ignore delayed entry / left truncation.**

It is designed for clinician-scientists, biomedical researchers, and applied statisticians who already use existing survival-analysis packages — starting with [`lifelines`](https://lifelines.readthedocs.io/) — and want a lightweight check for common design/code mismatches before results go into a paper, poster, or clinical report.

> **SurvGuard is not a survival-modeling library.** It does not reimplement Cox models, random survival forests, neural survival models, or competing-risk models. Instead, it inspects your code, data columns, and study context, then warns about possible methodological mistakes.

The MVP (**v0.1**) implements one rule — `left_truncation_missing` — for `lifelines.CoxPHFitter`.

**Documentation:** [Left truncation rule](docs/left_truncation.md) · [Contributing](CONTRIBUTING.md)

---

## Why left truncation matters

Patients often enter observation **after** the clinical time origin.

| Concept | Examples |
|---------|----------|
| **Time zero** | Disease onset, birth, diagnosis, transplant |
| **Entry time** | Enrollment, first visit, registry inclusion, first observation |

If the event process started before a patient entered observation, individuals who had the event before entry are never seen in the dataset. That is **delayed entry / left truncation**.

A Cox model can still fit on `observed_time` + `event`, print a normal summary, and **silently ignore** delayed entry — potentially biasing hazard ratios and survival estimates.

In `lifelines`, delayed entry can often be handled with:

```python
cph.fit(df, duration_col="observed_time", event_col="event", entry_col="entry_time")
```

SurvGuard checks whether your Cox model omits `entry_col` when the dataset or study context suggests delayed entry may be present.

---

## What SurvGuard does in v0.1

SurvGuard flags this pattern:

1. `CoxPHFitter.fit(...)` uses `duration_col` and `event_col`
2. The dataset and/or study context suggests delayed entry
3. The fit does **not** include `entry_col`

When all three hold, SurvGuard emits an evidence-linked warning:

```text
[HIGH] Possible left truncation ignored

Evidence:
- Code uses lifelines CoxPHFitter with duration_col='observed_time' and event_col='event'.
- Model fit does not include entry_col.
- Dataset contains entry-like column(s): entry_time.
- Study context mentions delayed entry / left truncation.

Suggested fix:
If patients enter observation after time zero, use entry_col='entry_time' in CoxPHFitter.fit(),
or use an equivalent start-stop formulation.
```

SurvGuard uses conservative language on purpose. It does **not** claim your analysis is definitely invalid — it flags a possible mismatch between the clinical time structure and the model specification.

---

## Quickstart

**Requirements:** Python 3.10+

```bash
git clone https://github.com/katjaschei28/survguard.git
cd survguard

python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

pip install -e ".[dev]"
pytest
```

Generate the demo dataset locally (the CSV is not committed):

```bash
python examples/left_truncation/generate_data.py
```

This creates `examples/left_truncation/synthetic_left_truncation.csv` with columns:
`patient_id`, `age`, `treatment`, `entry_time`, `observed_time`, `event`.

---

## Demo: bad vs corrected analysis

### Bad example — should warn

[`examples/left_truncation/bad_analysis.py`](examples/left_truncation/bad_analysis.py) fits a Cox model on `observed_time` and `event` but ignores `entry_time`.

```bash
survguard audit examples/left_truncation/bad_analysis.py \
  --data examples/left_truncation/synthetic_left_truncation.csv \
  --context examples/left_truncation/context.txt
```

Expected: **1 finding** (`left_truncation_missing`, confidence: high).

### Corrected example — should pass

[`examples/left_truncation/corrected_analysis.py`](examples/left_truncation/corrected_analysis.py) passes `entry_col="entry_time"`.

```bash
survguard audit examples/left_truncation/corrected_analysis.py \
  --data examples/left_truncation/synthetic_left_truncation.csv \
  --context examples/left_truncation/context.txt
```

Expected: **0 findings** — *No high-risk left-truncation issues detected.*

---

## Python API

Audit a file:

```python
from survguard import audit_file

report = audit_file(
    "examples/left_truncation/bad_analysis.py",
    data_path="examples/left_truncation/synthetic_left_truncation.csv",
    context_path="examples/left_truncation/context.txt",
)

print(report.to_markdown())
```

Audit code from a string:

```python
from survguard import audit_code

code = """
from lifelines import CoxPHFitter

cph = CoxPHFitter()
cph.fit(
    df,
    duration_col="observed_time",
    event_col="event",
    formula="age + treatment",
)
"""

report = audit_code(
    code=code,
    column_names=["patient_id", "entry_time", "observed_time", "event", "age", "treatment"],
    context="Patients have delayed entry and entry_time marks when they enter observation.",
)

print(report.to_markdown())
```

---

## Project layout

```text
survguard/
├── survguard/              # package source
│   ├── audit.py            # public API
│   ├── cli.py              # typer CLI
│   ├── parsers/            # lifelines code parsing
│   ├── rules/              # bias-detection rules
│   ├── reports/            # markdown report rendering
│   └── datasets/           # synthetic data generators
├── examples/
│   └── left_truncation/    # bad vs corrected Cox demo
├── docs/                   # rule documentation
├── tests/
├── README.md
├── pyproject.toml
└── LICENSE
```

---

## Scientific motivation

Typical survival packages help users **fit models**. SurvGuard asks a different question:

> Does the code's statistical model match the clinical time structure of the study?

Left truncation is a strong first target because:

```text
The code runs.
The model prints results.
But the risk set may be wrong.
```

That makes it a useful entry point for a bias-aware survival-analysis linter.

---

## Design principles

| Principle | What it means |
|-----------|---------------|
| **Evidence-linked** | Every finding cites code, data columns, and/or study context |
| **Conservative language** | "Possible left truncation ignored" — not "your analysis is wrong" |
| **No AI required** | v0.1 is fully deterministic and rule-based |
| **Small and educational** | One rule, one dataset, one bad example, one corrected example |

An AI explanation layer may be added later, but the package should remain useful without external APIs.

---

## Current limitations

SurvGuard v0.1 is deliberately small:

- Python only
- `lifelines.CoxPHFitter` only
- CSV column names only (reads headers, not full patient-level validation)
- One rule: `left_truncation_missing`
- Heuristic detection of entry-like column names

The tool does not decide whether left truncation truly applies in a real clinical study. It flags a **possible** issue when available evidence suggests delayed entry but the Cox model omits `entry_col`.

---

## Roadmap

| Version | Focus |
|---------|-------|
| **v0.1** | Left truncation / delayed entry *(current)* |
| v0.2 | Post-baseline exposure / future information |
| v0.3 | Time-dependent covariates |
| v0.4 | Competing risks |
| v0.5 | Threshold overfitting |
| v0.6 | Correlated predictors |
| v0.7 | AI-assisted explanation layer |

Possible future integrations: Jupyter reports, R survival code support, VS Code extension, GitHub Actions audit, API wrapper.

---

## Contributing

Contributions welcome — see [CONTRIBUTING.md](CONTRIBUTING.md).

```bash
pip install -e ".[dev]"
pytest
```

Good first contributions: more synthetic examples, parser improvements, documentation, edge-case tests, a second rule.

---

## License

MIT — see [LICENSE](LICENSE).
