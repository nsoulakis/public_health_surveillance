# Public Health Surveillance

Python notebooks for injury surveillance with the National Electronic Injury Surveillance System (NEISS), CPSC's national sample of consumer product–related injuries treated in hospital emergency departments: define a case, check the data it depends on, estimate with the survey design, detect unusual days, and investigate a flag.

The aim is a small, inspectable example of a surveillance analysis done the way a practitioner would do it: sample counts kept apart from national estimates, uncertainty from the survey design, a detector with a stated basis, thresholds set from a stated workload, and interpretations that stay within the evidence.

## Notebooks

| Notebook | What it does | Run |
|---|---|---|
| [01_case_definitions](python/notebooks/01_case_definitions.ipynb) | Checks the data, applies burn and head-injury definitions to adults in every published NEISS year from 2014, and reports sampled cases and national estimates with design-based uncertainty and CPSC stability checks | [Open in Colab](https://colab.research.google.com/github/nsoulakis/public_health_surveillance/blob/main/python/notebooks/01_case_definitions.ipynb) |
| [02_signals](python/notebooks/02_signals.ipynb) | Daily counts and weighted ratios, an EARS C1-style detector with thresholds set to one flag per 100 days on 2014–2018 and applied unchanged to later years, the combined alert workload, and a worked investigation of one flag | [Open in Colab](https://colab.research.google.com/github/nsoulakis/public_health_surveillance/blob/main/python/notebooks/02_signals.ipynb) |
| [hello_world](python/notebooks/hello_world.ipynb) | Checks that the notebooks open and run in Google Colab | [Open in Colab](https://colab.research.google.com/github/nsoulakis/public_health_surveillance/blob/main/python/notebooks/hello_world.ipynb) |

## Contribution and origin

The analyses are Nicholas Soulakis's, adapted from Methods in Health and Biomedical Informatics, which he taught as HSIP 441 at Northwestern University Feinberg School of Medicine and as MSBI 33100 at the University of Chicago. This Python implementation (2026) was checked rule by rule against his original course programs and the published methods cited in each notebook; the intentional differences are listed in the notebooks and tested.

## How to run

- **In a browser:** click "Open in Colab", then Runtime → Run all. The repository, data included, is copied into the Colab session; nothing to install.
- **On your own computer:** Python 3.10 or later, then `pip install -r requirements.txt` and open the notebooks in Jupyter. Run the checks with `pytest tests`.

## Data

`data/neiss/` holds CPSC's published NEISS files for 2014–2025, one compressed file per year with every published field and record, and CPSC's code labels. They were copied from CPSC's files with `python/scripts/extract_neiss.py`, which changes nothing but field-name case and the name of the sex field. Sources and terms: [data/SOURCES.md](data/SOURCES.md).

## What is checked, and what is not

**Checked:**
- Case definitions, the age rules and the adult population against hand-built records (`tests/test_neiss.py`).
- The variance against hand-computed values, including hospitals with no cases (`tests/test_survey.py`).
- The detector by hand, its behavior when the baseline does not vary, and that later days cannot change earlier flags (`tests/test_signals.py`).
- `.github/workflows/check.yml` runs the lint, the tests and every notebook from a clean copy on each push.

**Not claimed:**
- Detection performance. The alert rates are workload, not sensitivity, specificity or false-alarm rates; a simulation study is planned.
- An external benchmark for the variance code. The method follows Schroeder & Ault (2001); each public-file PSU is treated as one hospital, and hospitals reporting in any month count, which makes the standard errors slightly conservative.
- Estimates for all emergency visits. NEISS covers consumer product–related injuries only.
- Real-time detection. The analysis is retrospective, on published data.

## Planned

- Chicago crime reports: the same detector on refreshing open data, with reporting delays handled.
- A simulation study of detection performance.
- A client-style student assignment with a rubric and peer code review.
- Text-based case definitions from the narratives, with measured accuracy.

## Citation

See [CITATION.cff](CITATION.cff), or use "Cite this repository" on this page.

## License

Code: MIT ([LICENSE](LICENSE)). Text and notebook prose: CC BY 4.0 ([LICENSE-TEXT](LICENSE-TEXT)). NEISS data: U.S. government public data (CPSC).
