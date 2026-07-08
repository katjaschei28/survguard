# Left truncation example

This example demonstrates a common survival-analysis problem: delayed entry / left truncation.

The synthetic dataset contains:
- `entry_time`: when the patient enters observation
- `observed_time`: event or censoring time
- `event`: 1 if event occurred, 0 if censored
- `age`
- `treatment`

The bad analysis fits a Cox model using `observed_time` and `event` but ignores `entry_time`.

The corrected analysis passes `entry_col="entry_time"` to `CoxPHFitter.fit()`.

**Note:** The synthetic CSV is not committed to the repo. Generate it first:

Run:

```bash
python examples/left_truncation/generate_data.py
survguard audit examples/left_truncation/bad_analysis.py \
  --data examples/left_truncation/synthetic_left_truncation.csv \
  --context examples/left_truncation/context.txt

survguard audit examples/left_truncation/corrected_analysis.py \
  --data examples/left_truncation/synthetic_left_truncation.csv \
  --context examples/left_truncation/context.txt
```
