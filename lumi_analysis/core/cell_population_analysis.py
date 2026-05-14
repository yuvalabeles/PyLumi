import numpy as np
import pandas as pd

from lumi_analysis.core.loading import load_files
from lumi_analysis.core.validation import (
    assert_interval_jumps,
    assert_interval_overlaps,
)


def analyse_cell_population(
    path_lst,
    filenames=None,
    noise_max=20,
    save_file=True,
    sample_name=None,
):
    # Load files.
    dfs = load_files(path_lst)
    dfs_no_noise = []

    if filenames is None:
        filenames = [f"file_{i + 1}" for i in range(len(dfs))]

    for file_num, df in enumerate(dfs):
        # Remove rows prior to inserting the samples.
        first_valid_index = df[df["counts/sec"] >= noise_max].index[0]
        df_no_noise = df.loc[first_valid_index:].reset_index(drop=True)

        # Subtract the mean of the removed counts from the data.
        subtract = np.mean(
            df[0:(len(df) - len(df_no_noise))]["counts/sec"]
        )

        df_no_noise["counts/sec"] = (
            df_no_noise["counts/sec"] - subtract
        )

        # Validate interval jumps.
        df_no_noise = assert_interval_jumps(
            df_no_noise,
            filenames,
            file_num,
        )

        dfs_no_noise.append(df_no_noise)

    # Align overlapping time intervals across all files.
    dfs_aligned = assert_interval_overlaps(dfs_no_noise)

    # Create average dataframe.
    avg_df = pd.DataFrame({
        "Date": dfs_aligned[0]["Date"],
        "Time (hr:min)": dfs_aligned[0]["Time (hr:min)"],
        "Time (days)": dfs_aligned[0]["Time (days)"],
    })

    counts = pd.DataFrame({
        f"counts/sec {i}": dfs_aligned[i]["counts/sec"]
        for i in range(len(dfs_aligned))
    })

    avg_df["counts/sec"] = counts.mean(axis=1)

    # Save result temporarily for backward compatibility.
    if save_file:
        filename = "avg_df.csv"

        if sample_name is not None:
            filename = sample_name + filename

        avg_df.to_csv(filename, index=False)

    return avg_df
