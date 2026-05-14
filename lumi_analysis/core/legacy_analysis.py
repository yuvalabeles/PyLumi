"""
TEMPORARY LEGACY FILE

This file contains migrated functions copied from the old Lumi Pipeline project.

The goal is to preserve working functionality during architecture migration.

Functions here should gradually be refactored and moved into:
- tissue_analysis.py
- cell_population_analysis.py
- export.py
- plotting.py
"""

from datetime import datetime
import numpy as np
import pandas as pd
from lumi_analysis.core.loading import load_files
from lumi_analysis.core.validation import (
    assert_interval_jumps,
    assert_interval_overlaps,
)
from lumi_analysis.core.dataframes import (
    create_sub_df,
    create_complete_df,
    create_condensed_df,
)
FOLDER_NAME = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")


# ____________________________________________________________________________________________________________________ #
# Function to load the raw data as saved from Lumi:
# ____________________________________________________________________________________________________________________ #


# ____________________________________________________________________________________________________________________ #
# Functions to build DataFrames of the analyzed data:
# ____________________________________________________________________________________________________________________ #


# ____________________________________________________________________________________________________________________ #
# Functions to assert the data validity:
# ____________________________________________________________________________________________________________________ #


# ____________________________________________________________________________________________________________________ #
# Function for analysing samples of cells:
# ____________________________________________________________________________________________________________________ #
def analyse_cell_population(path_lst, noise_max=20, save_file=True, sample_name=None):
    # Load files:
    dfs, dfs_no_noise = [], []
    for p in path_lst:
        dfs.append(pd.read_csv(p, header=1, index_col=0))

    for df in dfs:
        # Removing the rows prior to inserting the samples:
        first_valid_index = df[df["counts/sec"] >= noise_max].index[0]
        df_no_noise = df.loc[first_valid_index:].reset_index(drop=True)

        # Subtracting the mean of the removed counts from the data:
        subtract = np.mean(df[0:(len(df) - len(df_no_noise))]["counts/sec"])
        df_no_noise["counts/sec"] = df_no_noise["counts/sec"] - subtract

        # Validate the intervals jumps are correct (10 minutes):
        timestamps = df_no_noise["Time (hr:min)"]
        for i in range(len(timestamps) - 1):
            curr = int(timestamps[i][-2])
            nxt = int(timestamps[i + 1][-2])
            if (curr + 1) % 6 == nxt:
                continue
            elif (curr + 1) % 6 == (nxt - 1) % 6:
                # Only one consecutive interval is missing - filling missing row manually:
                insert_index = i + 1
                numeric_cols = df_no_noise.select_dtypes(include="number").columns
                new_row = (pd.DataFrame(df_no_noise)).iloc[insert_index - 1].copy()
                new_row["Time (hr:min)"] = timestamps[i][:-2] + str((curr + 1) % 6) + timestamps[i][-1]
                new_row[numeric_cols] = (df_no_noise.iloc[insert_index - 1][numeric_cols] +
                                         df_no_noise.iloc[insert_index][numeric_cols]) / 2
                new_row = new_row.to_frame().T
                df_no_noise = pd.concat(
                    [df_no_noise.iloc[:insert_index], new_row, df_no_noise.iloc[insert_index:]]).reset_index(drop=True)
            else:
                print("More than one consecutive interval missing.")
                return

        dfs_no_noise.append(df_no_noise)

    # Assert the time intervals in all three dataframes correctly overlap:
    times = []
    for df in dfs_no_noise:
        time_col = pd.to_datetime(df["Time (hr:min)"], format="%H:%M").dt.floor("10min").dt.time
        times.append(time_col)

    latest_time = max(col.iloc[0] for col in times)
    indices = [col[col == latest_time].index[0] for col in times]
    dfs_aligned = [
        df.iloc[start_idx:].reset_index(drop=True)
        for df, start_idx in zip(dfs_no_noise, indices)
    ]
    min_len = min(len(df) for df in dfs_aligned)
    dfs_aligned = [df.iloc[:min_len] for df in dfs_aligned]

    # Create a new dataframe with average counts column:
    avg_df = pd.DataFrame({"Date": dfs_aligned[0]["Date"], "Time (hr:min)": dfs_aligned[0]["Time (hr:min)"],
                           "Time (days)": dfs_aligned[0]["Time (days)"]})

    counts = pd.DataFrame({"counts/sec " + str(i): dfs_aligned[i]["counts/sec"] for i in range(len(dfs_aligned))})

    avg_df["counts/sec"] = counts.mean(axis=1)

    # Save result (optional):
    if save_file:
        filename = "avg_df.csv"
        if sample_name is not None:
            filename = sample_name + filename
        avg_df.to_csv(filename, index=False)


# ____________________________________________________________________________________________________________________ #
# Function for analysing samples of tissues:
# ____________________________________________________________________________________________________________________ #
def analyse_tissue(path_lst, filenames, noise_max=25, remove_noise=True, save_file=True, sample=None, folder_name=None):
    # Load files:
    dfs, dfs_no_noise = load_files(path_lst), []

    for f in range(len(dfs)):
        df = dfs[f]

        if sample == "Extra":
            first_valid_index = 0
            remove_noise = False
        else:
            # Removing the rows prior to inserting the samples:
            first_valid_index = df[df["counts/sec"] >= noise_max].index[0]

        df_no_noise = df.loc[first_valid_index:].reset_index(drop=True)

        if remove_noise:
            # Subtracting the mean of the removed counts from the data:
            subtract = np.mean(df[0:(len(df) - len(df_no_noise))]["counts/sec"])
            df_no_noise["counts/sec"] = df_no_noise["counts/sec"] - subtract

        # Validate the intervals jumps are correct (10 minutes):
        df_no_noise = assert_interval_jumps(df_no_noise, filenames, f)
        dfs_no_noise.append(df_no_noise)

    # Assert the time intervals in all replicates correctly overlap:
    dfs_aligned = assert_interval_overlaps(dfs_no_noise)

    # Drop default 'Baseline' column:
    for df in dfs_aligned:
        df.drop(" Baseline", axis=1, inplace=True)

    # Create results dataframes:
    full_df = create_sub_df(dfs_aligned, filenames, save_file=save_file, sample=sample, folder_name=folder_name)

    return full_df


# ____________________________________________________________________________________________________________________ #
# Function to save the data to files (excel / csv):
# ____________________________________________________________________________________________________________________ #
