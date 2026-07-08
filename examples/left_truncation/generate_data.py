from survguard.datasets.left_truncation import save_left_truncation_data

save_left_truncation_data(
    "examples/left_truncation/synthetic_left_truncation.csv",
    n=2000,
    seed=42,
)

print("Saved synthetic left-truncation data to examples/left_truncation/synthetic_left_truncation.csv")
