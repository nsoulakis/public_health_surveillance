# Public Health Surveillance

Python notebooks for public health surveillance: define a case, detect a signal, and decide whether a signal is compelling enough to pull the case files.

One method, two data sources:
- **National injuries:** ten years of emergency department injury records from the National Electronic Injury Surveillance System (NEISS), U.S. Consumer Product Safety Commission.
- **Chicago crime reports:** ten years of reported crimes from the City of Chicago Data Portal.

**Status:** in development, October 2026. Notebooks are added here as each one runs end to end.

## Notebooks

| Notebook | What it does | Run |
|---|---|---|
| [hello_world](notebooks/hello_world.ipynb) | Checks that the notebooks open and run in Google Colab | [Open in Colab](https://colab.research.google.com/github/nsoulakis/public_health_surveillance/blob/main/notebooks/hello_world.ipynb) |

## How to run

- **In a browser:** click "Open in Colab" next to a notebook, then Runtime → Run all. Nothing to install.
- **On your own computer:** Python 3.10 or later with pandas, NumPy, matplotlib and scikit-learn.

## Data

Sources, versions and terms of use are in [data/SOURCES.md](data/SOURCES.md). Full datasets are not stored in this repository.

## Origin

The methods are adapted from Methods in Health and Biomedical Informatics (HSIP 441), taught by Nicholas Soulakis at Northwestern University Feinberg School of Medicine.

## Citation

See [CITATION.cff](CITATION.cff), or use "Cite this repository" on the right of this page.

## License

Code: MIT ([LICENSE](LICENSE)). Text and notebook prose: CC BY 4.0 ([LICENSE-TEXT](LICENSE-TEXT)).
