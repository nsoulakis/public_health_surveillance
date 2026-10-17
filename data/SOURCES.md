# Data sources

## National Electronic Injury Surveillance System (NEISS)

- **Publisher:** U.S. Consumer Product Safety Commission (CPSC).
- **What it is:** a national probability sample of hospital emergency department visits for consumer product–related injuries. Each record carries a statistical weight, the hospital's stratum and PSU, coded fields, and a short narrative.
- **Years in this repository:** 2014–2025, every published year from 2014. The second diagnosis and body-part fields are absent from the 2014 file and empty until 2019; the case-definition notebook shows the effect.
- **Where CPSC publishes it:** the NEISS On-Line Query System, https://www.cpsc.gov/cgibin/neissquery/, "Archived Annual NEISS Data" (overview: https://www.cpsc.gov/Research--Statistics/NEISS-Injury-Data). CPSC publishes each year as a SAS data set (`neissYYYY.sas7bdat`) with a formats file (`neiss_fmt.sas7bdat`).
- **In this repository:** `data/neiss/neiss_YYYY.csv.gz` and `data/neiss/neiss_formats.csv`, written from CPSC's files by `python/scripts/extract_neiss.py`. All records and fields are kept; field names are lowercased, the sex field (published as `Sex`, or `gender` in 2023) is named `sex`, and whole-number codes are written without a decimal point.
- **Documentation used:** NEISS Coding Manual (CPSC Only "Non-Trauma"), January 2025, rev. 1; Schroeder T, Ault K, *The NEISS Sample (Design and Implementation) 1997 to Present*, CPSC, 2001; CPSC, NEISS web estimates, https://www.cpsc.gov/cgibin/NEISSQuery/webestimates.html.
- **Terms:** U.S. government public data.
