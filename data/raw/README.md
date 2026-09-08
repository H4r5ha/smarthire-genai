# Optional raw Kaggle CSVs

These are the original/raw Kaggle job CSV files used only if you want to reproduce or transform the project dataset yourself. They are **optional** and are **not required to run the SmartHire application**.

The raw CSV files may be present in this local `data/raw/` folder, but they should **not be committed to the Git repository** because they are large source files. The application uses the prepared dataset at:

`data/jobs/smarthire_jobs_80.csv`

Expected optional source files:

- `naukri_software_engineer.csv`
- `naukri_data_scientist.csv`

If you need to regenerate or transform the prepared dataset from these raw files, use the project's dataset-processing script from the project root. This is a data-preparation workflow only; normal app execution does not depend on the raw files.

## Recommended `.gitignore` entry

Add this line to `.gitignore` so raw CSVs under this folder are excluded from Git:

```gitignore
data/raw/*.csv
```
