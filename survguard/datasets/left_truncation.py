"""Synthetic delayed-entry / left-truncation survival data."""

from __future__ import annotations

import pandas as pd
import numpy as np


def make_left_truncation_data(n: int = 2000, seed: int = 42) -> pd.DataFrame:
    """
    Generate synthetic survival data with delayed entry (left truncation).

    Patients enter observation at entry_time. Only patients whose true event
    occurs after entry are retained, mimicking left-truncated observation.
    """
    rng = np.random.default_rng(seed)

    age = rng.normal(60, 10, n)
    treatment = rng.binomial(1, 0.5, n)

    baseline_hazard = 0.03
    hazard = baseline_hazard * np.exp(0.02 * (age - 60)) * np.exp(-0.3 * treatment)
    true_event_time = rng.exponential(1.0 / hazard)

    entry_time = rng.uniform(0, 20, n)

    mask = true_event_time > entry_time
    age = age[mask]
    treatment = treatment[mask]
    true_event_time = true_event_time[mask]
    entry_time = entry_time[mask]

    n_kept = len(age)
    patient_id = np.arange(1, n_kept + 1)

    censor_time = entry_time + rng.uniform(10, 60, n_kept)
    observed_time = np.minimum(true_event_time, censor_time)
    event = (true_event_time <= censor_time).astype(int)

    return pd.DataFrame(
        {
            "patient_id": patient_id,
            "age": age,
            "treatment": treatment,
            "entry_time": entry_time,
            "observed_time": observed_time,
            "event": event,
        }
    )


def save_left_truncation_data(path: str, n: int = 2000, seed: int = 42) -> None:
    """Generate and save synthetic left-truncation data to CSV."""
    df = make_left_truncation_data(n=n, seed=seed)
    df.to_csv(path, index=False)
