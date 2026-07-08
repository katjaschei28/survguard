import pandas as pd
from lifelines import CoxPHFitter

df = pd.read_csv("examples/left_truncation/synthetic_left_truncation.csv")

cph = CoxPHFitter()

cph.fit(
    df,
    duration_col="observed_time",
    event_col="event",
    formula="age + treatment",
)

cph.print_summary()
