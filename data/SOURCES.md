# Data sources

Full datasets are not stored in this repository. Each notebook states which data it used and the date the data ends.

## National Electronic Injury Surveillance System (NEISS)

- **Publisher:** U.S. Consumer Product Safety Commission
- **What it is:** a national probability sample of emergency department visits for consumer product injuries, with a statistical weight per record and a short narrative.
- **Years used:** 2014–2023
- **Where to get it:** the NEISS On-Line Query System, https://www.cpsc.gov/cgibin/neissquery/, section "Archived Annual NEISS Data". Choose a year and a file format. (Overview: https://www.cpsc.gov/Research--Statistics/NEISS-Injury-Data)
- **File format:** CPSC publishes each year natively as a SAS data set (`neissYYYY.sas7bdat`), with a SAS formats file for the code labels. This repository reads those files as published, so analysts working in SAS and in Python start from the same files with no conversion. The code labels used here are in `data/demo/neiss/neiss_formats.csv`.
- **To run at full scale:** download 2014–2023 in the SAS format and put the files in `data/raw/neiss/`. The notebooks then switch from demo mode to full mode automatically.
- **Terms:** U.S. government public data.

## Chicago Reported Crimes

- **Publisher:** City of Chicago Data Portal, dataset "Crimes - 2001 to Present" (ID ijzp-q8t2)
- **What it is:** reported incidents of crime in Chicago, one row per incident.
- **Period used:** 2016-10-16 to 2026-10-08 (exported 2026-10-16; the portal's newest records lag by about a week).
- **Where to get it:** https://data.cityofchicago.org/Public-Safety/Crimes-2001-to-Present/ijzp-q8t2
- **Terms:** City of Chicago Data Portal terms of use, shown on the portal.
