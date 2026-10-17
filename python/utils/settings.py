"""Analysis settings. Change them here and nowhere else."""

WINDOW = 14  # days in the baseline (PHI_040)
TARGET_RATE = 0.01  # one flag per 100 days (Nicholas's working heuristic)
CALIBRATION = ("2014-01-01", "2018-12-31")  # k is chosen on these years ...
EVALUATION = ("2019-01-01", "2025-12-31")  # ... and applied unchanged to these
