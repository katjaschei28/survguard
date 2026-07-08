# Left truncation / delayed entry

This document explains the first SurvGuard rule: **`left_truncation_missing`**.

## The problem

In many cohort studies, patients **enter observation after time zero**. For example:

- A registry starts enrolling in 2010, but some patients had their first visit in 2012
- Age is used as the time scale, and patients enter at different ages
- Screening detects disease only after a certain calendar date

If the underlying event process started at time 0 but you only observe individuals **after** their entry time, the data are **left truncated**. People who experienced the event before entry are not in the dataset.

A standard Cox model fit on `(observed_time, event)` **without** accounting for entry can still run—and can still produce coefficients—but it may **ignore delayed entry** and introduce bias.

## What lifelines supports

`lifelines.CoxPHFitter` accepts an `entry_col` argument for delayed entry:

```python
cph.fit(
    df,
    duration_col="observed_time",
    event_col="event",
    entry_col="entry_time",  # when observation begins
    formula="age + treatment",
)
```

If your data have an entry-time column and your study design involves delayed entry, omitting `entry_col` is a common mistake.

## What SurvGuard checks

SurvGuard flags a **possible** issue when **all** of the following hold:

1. The code fits a `lifelines` Cox PH model with `duration_col` and `event_col`
2. The fit does **not** include `entry_col`
3. There is evidence of delayed entry from:
   - **Data**: column names like `entry_time`, `start`, `enrollment`, etc., or
   - **Context**: study description mentioning left truncation / delayed entry

Confidence is **high** when both data and context suggest delayed entry; **medium** when only one does.

SurvGuard does **not** claim the analysis is definitely invalid—it reports evidence and a suggested fix.

## Example in this repo

| File | Purpose |
|------|---------|
| `examples/left_truncation/generate_data.py` | Create synthetic CSV |
| `examples/left_truncation/bad_analysis.py` | Cox fit **without** `entry_col` |
| `examples/left_truncation/corrected_analysis.py` | Cox fit **with** `entry_col` |
| `examples/left_truncation/context.txt` | Study description for the auditor |

### Run the demo

```bash
python examples/left_truncation/generate_data.py

survguard audit examples/left_truncation/bad_analysis.py \
  --data examples/left_truncation/synthetic_left_truncation.csv \
  --context examples/left_truncation/context.txt
```

The bad example should report **1 finding** with rule `left_truncation_missing`. The corrected example should report **0 findings**.

## Synthetic data logic

The generator in `survguard/datasets/left_truncation.py`:

1. Simulates event times from an exponential model with age and treatment effects
2. Assigns random `entry_time` values
3. **Keeps only** patients with `true_event_time > entry_time` (left truncation)
4. Applies censoring after entry so `observed_time > entry_time`

This mimics a delayed-entry setting where pre-entry events are unobserved.

## Further reading

- Kalbfleisch & Prentice, *The Statistical Analysis of Failure Time Data*
- `lifelines` documentation on [left truncation](https://lifelines.readthedocs.io/)

## Related roadmap items

Future SurvGuard versions may cover post-baseline exposure, time-dependent covariates, and competing risks—see the main [README](../README.md#roadmap).
