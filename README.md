
# Lumi Analysis

Lumi Analysis is a Python pipeline for analysing Lumi luminescence experiments.

The pipeline receives raw CSV files exported from the Lumi software and produces:
- processed data tables
- grouped replicate analysis
- condensed summary tables
- plots and visualizations (future stages)
- inspectable intermediate processing stages

The project is designed for biological experiments involving:
- tissue/slice samples
- cell population samples


---

# Project Structure

```text
Lumi Analysis/
│
├── lumi_analysis/
│   ├── core/
│   ├── export/
│   └── ...
│
├── scripts/
│   └── run_pipeline.py
│
└── README.md
```

---

# Requirements

Python 3.10+ recommended.

Required packages:

* pandas
* numpy
* openpyxl

Install dependencies:

```bash
pip install pandas numpy openpyxl
```

---

# Input Data

The input folder should contain raw CSV files exported from the Lumi software.

Typical file names:

```text
1a_Raw.csv
1b_Raw.csv
1c_Raw.csv
...
```

The files are automatically grouped into replicate groups according to the user settings.

---

# Running the Pipeline

Open:

```text
scripts/run_pipeline.py
```

Edit only the `USER SETTINGS` section.

Then run:

```bash
python scripts/run_pipeline.py
```

---

# Main User Settings

## Input folder

```python
"input_folder"
```

Path to the folder containing the Lumi raw CSV files.

---

## Output folder

```python
"output_folder"
```

Folder where processed results will be saved.

---

## Experiment type

```python
"experiment_type"
```

Options:

```python
"tissue"
"cell_population"
```

---

## Replicates per group

```python
"replicates_per_group"
```

Number of replicate files belonging to each sample.

Example:

```text
5 replicate files per tissue sample
```

---

## Sample tags

```python
"sample_tags"
```

Optional sample names assigned to detected groups.

Example:

```python
[
    "Liver1",
    "Liver2",
    "Kid1",
]
```

If set to:

```python
None
```

groups will be named automatically:

```text
Group_1
Group_2
Group_3
```

---

## Noise threshold

```python
"noise_max"
```

Minimum counts/sec value used to detect the beginning of the biological signal.

All consecutive rows from the start, with counts below this threshold, are treated as pre-sample noise.

---

## Remove noise

```python
"remove_noise"
```

Options:

```python
True
False
```

If enabled, the average pre-sample signal is subtracted from the data.

---

# Output

The pipeline generates:

* processed replicate tables
* complete combined tables
* condensed analysis tables
* intermediate analysis objects

All outputs are saved automatically into the selected output folder.

---

# Intermediate Analysis Objects

The pipeline stores intermediate processing stages internally.

These include:

* raw loaded dataframes
* processed dataframes
* aligned replicate dataframes
* final result tables

This allows future interactive inspection and visualization.

---

# Common Errors

## Folder does not exist

Check that:

```python
"input_folder"
```

points to a valid folder.

---

## Missing CSV files

Make sure the folder contains Lumi-exported CSV files.

---

## Wrong replicate count

If files are grouped incorrectly, verify:

```python
"replicates_per_group"
```

and:

```python
"sample_tags"
```

---

# Future Development

Planned features:

* interactive plotting
* Streamlit graphical interface
* manual replicate grouping
* parameter tuning UI
* intermediate-stage visualization
* automated report generation

```
```
