# SurvGuard

<!-- Replace YOUR_GITHUB_USERNAME with your GitHub handle after creating the repo -->
![Tests](https://github.com/YOUR_GITHUB_USERNAME/survguard/actions/workflows/tests.yml/badge.svg)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

**SurvGuard is a proof-of-concept survival-analysis linter that detects when Cox model code may ignore delayed entry / left truncation.**

SurvGuard is aimed at clinician-scientists and applied statisticians who use existing survival packages (starting with `lifelines`) and want a lightweight check for common design/code mismatches—before results go into a paper or clinical report.

> **SurvGuard is not a modeling library.** It does not reimplement Cox models, random survival forests, or neural survival models. It inspects your code, data columns, and study context, then warns about possible methodological mistakes.

The MVP (v0.1) implements one rule: **`left_truncation_missing`** for `lifelines.CoxPHFitter`.

---

## Why left truncation matters

Patients often **enter observation after time zero** (delayed entry). If the event process started earlier but you only observe individuals from their entry time onward, the data are **left truncated**.

A Cox model can still fit on `(observed_time, event)` alone—it may run without error and print a summary—while **silently ignoring** delayed entry. That can bias hazard ratios and survival estimates.

`lifelines` supports delayed entry via `entry_col`. SurvGuard checks whether your fit omits it when the data or study context suggest you need it.

See [docs/left_truncation.md](docs/left_truncation.md) for the full explanation.

---

## Quickstart

**Requirements:** Python 3.10+

```bash
git clone https://github.com/YOUR_GITHUB_USERNAME/survguard.git
cd survguard

python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

pip install -e ".[dev]"
pytest
```

Generate synthetic example data (not committed to the repo):

```bash
python examples/left_truncation/generate_data.py
```

---

## Bad example (should warn)

`examples/left_truncation/bad_analysis.py` fits a Cox model on `observed_time` and `event` but **ignores** `entry_time`:

```bash
survguard audit examples/left_truncation/bad_analysis.py \
  --data examples/left_truncation/synthetic_left_truncation.csv \
  --context examples/left_truncation/context.txt
```

**Expected output:**

```text
# SurvGuard Audit Report

Models checked: 1
Findings: 1

## Findings

### [HIGH] Possible left truncation ignored

**Rule:** `left_truncation_missing`
**Confidence:** high

**Evidence:**
- Code uses lifelines CoxPHFitter with duration_col='observed_time' and event_col='event'.
- Model fit does not include entry_col.
- Dataset contains entry-like column(s): entry_time.
- Study context mentions delayed entry / left truncation.

**Suggested fix:**
If patients enter observation after time zero, use entry_col='entry_time' in CoxPHFitter.fit(), or use an equivalent start-stop formulation.
```

---

## Corrected example (should pass)

`examples/left_truncation/corrected_analysis.py` passes `entry_col="entry_time"`:

```bash
survguard audit examples/left_truncation/corrected_analysis.py \
  --data examples/left_truncation/synthetic_left_truncation.csv \
  --context examples/left_truncation/context.txt
```

**Expected output:**

```text
# SurvGuard Audit Report

Models checked: 1
Findings: 0

No high-risk left-truncation issues detected.
```

---

## Python API

```python
from survguard import audit_file

report = audit_file(
    "examples/left_truncation/bad_analysis.py",
    data_path="examples/left_truncation/synthetic_left_truncation.csv",
    context_path="examples/left_truncation/context.txt",
)

print(report.to_markdown())
```

---

## Project layout

```text
survguard/
├── survguard/          # package source
├── examples/
│   └── left_truncation/   # bad vs corrected Cox fits
├── docs/               # rule documentation
└── tests/              # pytest suite
```

Browse the examples on GitHub:

- [`examples/left_truncation/bad_analysis.py`](examples/left_truncation/bad_analysis.py)
- [`examples/left_truncation/corrected_analysis.py`](examples/left_truncation/corrected_analysis.py)

---

## Scientific motivation

SurvGuard is inspired by tutorial-style survival workflows (e.g. PySurvival-style examples) but focused on **bias detection**, not model implementation.

Design principles:

- **Evidence-linked** — every finding cites code, data, and/or context
- **Conservative language** — "possible" issues, not definitive verdicts
- **No AI required** — v0.1 is fully deterministic and rule-based
- **Small and educational** — one rule, one package, one clear demo

---

## Roadmap

- **v0.1** — left truncation / delayed entry *(current)*
- **v0.2** — post-baseline exposure / future information
- **v0.3** — time-dependent covariates
- **v0.4** — competing risks
- **v0.5** — threshold overfitting
- **v0.6** — correlated predictors

---

## Contributing

Contributions welcome. See [CONTRIBUTING.md](CONTRIBUTING.md).

```bash
pip install -e ".[dev]"
pytest
```

---

## License

MIT — see [LICENSE](LICENSE).
