import numpy as np

from lumi_analysis.core.loading import load_files
from lumi_analysis.core.validation import (
    assert_interval_jumps,
    assert_interval_overlaps,
)
from lumi_analysis.core.dataframes import create_sub_df


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
