# Public Health Surveillance

Python notebooks for public health surveillance: define a case, detect a signal, and decide whether a signal is compelling enough to pull the case files.

One method, two data sources:
- **National injuries:** ten years of emergency department injury records from the National Electronic Injury Surveillance System (NEISS), U.S. Consumer Product Safety Commission.
- **Chicago crime reports:** ten years of reported crimes from the City of Chicago Data Portal.

**Status:** in development, October 2026. Notebooks are added here as each one runs end to end.

## Notebooks

| Notebook | What it does | Run |
|---|---|---|
| [01_case_definitions](python/notebooks/01_case_definitions.ipynb) | Burn and head-injury case definitions applied to ten years of NEISS (3.5 million visits) | [Open in Colab](https://colab.research.google.com/github/nsoulakis/public_health_surveillance/blob/main/python/notebooks/01_case_definitions.ipynb) |
| [hello_world](python/notebooks/hello_world.ipynb) | Checks that the notebooks open and run in Google Colab | [Open in Colab](https://colab.research.google.com/github/nsoulakis/public_health_surveillance/blob/main/python/notebooks/hello_world.ipynb) |

## What's here

| Folder | Contents |
|---|---|
| `python/` | Notebooks, shared functions (`utils/`) and scripts |
| `data/` | Data sources and small demo samples, one subfolder per source (`neiss/`, `crime/`), shared by every language |

Other languages will sit beside `python/` and share the same `data/`.

## How to run

- **In a browser:** click "Open in Colab" next to a notebook, then Runtime → Run all. Nothing to install.
- **On your own computer:** Python 3.10 or later with pandas, NumPy, matplotlib and scikit-learn.

## Data

Sources, versions and terms of use are in [data/SOURCES.md](data/SOURCES.md). Full datasets are not stored in this repository.

- **Demo mode (default):** notebooks run on a 2% random sample in `data/demo/neiss/`, built by `python/scripts/make_demo_data.py` (seed 20003). Weights are scaled so national estimates stay on the full scale.
- **Full mode:** the results shown on this page come from the full 2014–2023 files.

## Origin

The methods are adapted from Methods in Health and Biomedical Informatics (HSIP 441), taught by Nicholas Soulakis at Northwestern University Feinberg School of Medicine.

## Citation

See [CITATION.cff](CITATION.cff), or use "Cite this repository" on the right of this page.

## License

Code: MIT ([LICENSE](LICENSE)). Text and notebook prose: CC BY 4.0 ([LICENSE-TEXT](LICENSE-TEXT)).
