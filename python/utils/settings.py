"""Settings for the signals. Starting values; change them here and nowhere else."""

WINDOW = 14  # days in the moving baseline

# z-score thresholds per series, from the original analysis
THRESHOLDS = {
    ("burn", "case_sum"): 3.46,
    ("burn", "ratio_to_other"): 3.40,
    ("burn", "wt_rto"): 3.34,
    ("head_injury", "case_sum"): 2.75,
    ("head_injury", "ratio_to_other"): 2.78,
    ("head_injury", "wt_rto"): 2.70,
}

SEED = 20003

# Chicago crime: starting values from the original crime analysis
CRIME_THRESHOLDS = {
    ("domestic", "case_sum"): 3.00,
    ("domestic", "ratio_to_other"): 3.50,
}
