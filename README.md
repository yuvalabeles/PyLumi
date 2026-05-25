# Lumi Analysis

Lumi Analysis is a Python pipeline for analysing Lumi luminescence experiments.

The pipeline receives raw CSV files exported from Lumi software and performs:

- grouped biological replicate analysis
- preprocessing and signal cleaning
- plotting
- peak and period analysis
- Excel export of processed outputs

The pipeline is configured through an Excel settings file (`settings.xlsx`).

---

# Quick Start

## 1. Install Python

First, check whether Python is already installed.

### Windows

Open Command Prompt:

- Press the Windows key
- Type:

```text
cmd
```

- Press Enter

Run:

```bash
py --version
```

### macOS

Open Terminal:

- Press `⌘ + Space`
- Search for:

```text
Terminal
```

Run:

```bash
python3 --version
```

If Python is not installed, download it from:

https://www.python.org/downloads/

Windows users: during installation make sure to check:

```text
Add Python to PATH
```

---

## 2. Save the Lumi folder

Save the Lumi Analysis folder somewhere easy to access.

Recommended:

- Desktop
- Documents

Do not rename internal files.

---

## 3. Prepare your data

Place Lumi raw CSV files inside a single folder.

Recommended:

Use the `Analysis` folder automatically created by Lumi.

Example:

```text
Analysis/
├── 1a_Raw.csv
├── 1b_Raw.csv
├── 2a_Raw.csv
├── 2b_Raw.csv
```

Replicates belonging to the same condition must appear consecutively.

---

## 4. Configure `settings.xlsx`

Open the Excel settings file.

Settings marked with `(*)` must be edited or verified before the first run.

Only the blue column is editable.

Every time settings are changed:

1. Save the Excel file  
2. Re-run the pipeline

### Settings syntax rules

#### Empty cell = `None`

An empty cell is equivalent to:

```text
None
```

#### Lists

Lists must use square brackets:

```text
[ ]
```

Examples:

```python
[1, 2, 3]
["control", "Dex", "Dex 25"]
[True, "sample", 2, False]
```

Notes:

- Text inside lists must be in quotation marks
- Numbers and booleans (`True/False`) should NOT be in quotation marks
- Outside lists, quotation marks are not required

#### Folder paths

Windows example:

```text
C:\Users\YourName\Desktop\Analysis
```

macOS example:

```text
/Users/YourName/Desktop/Analysis
```

Windows uses `\`  
macOS uses `/`

---

## 5. Open Terminal inside the Lumi folder

### Windows

Right-click inside the Lumi folder and choose:

```text
Open in Terminal
```

### macOS

Right-click the Lumi folder and choose:

```text
New Terminal at Folder
```

Or navigate manually:

```bash
cd /path/to/Lumi_folder
```

Example:

```bash
cd /Users/YourName/Desktop/Lumi
```

---

## 6. Run the pipeline

### Windows

```bash
python -m scripts.run_pipeline
```

### macOS

```bash
python3 -m scripts.run_pipeline
```

The first run may take longer because required packages are installed automatically.

---

## 7. Find your results

Results are saved to the output folder defined in `settings.xlsx`.

If only a folder name is provided instead of a full path, the results folder will most likely be created inside the Lumi pipeline folder.

To avoid overwriting previous analyses:

- move completed result folders elsewhere
- or define a full output path in `settings.xlsx`

---

# Common Issues

## Python is not recognized

Python may not be installed or added to PATH.

Check:

```text
Add Python to PATH
```

## Input folder does not exist

Verify the input folder path in `settings.xlsx`.

## Output folder issues

Verify the output folder path in `settings.xlsx`.

## Settings changes do not appear

Make sure the settings file was saved and the pipeline re-run.
