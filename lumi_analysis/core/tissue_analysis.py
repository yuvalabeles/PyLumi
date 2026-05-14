import numpy as np

from lumi_analysis.core.loading import load_files
from lumi_analysis.core.validation import (
    assert_interval_jumps,
    assert_interval_overlaps,
)
from lumi_analysis.core.dataframes import create_sub_df

from lumi_analysis.export.excel_export import save_tissue_data


def analyse_tissue(
    path_lst,
    filenames,
    noise_max=25,
    remove_noise=True,
    save_file=True,
    sample=None,
    output_folder=None,
):
    # Load files.
    dfs = load_files(path_lst)
    dfs_no_noise = []

    for f in range(len(dfs)):
        df = dfs[f]

        if sample == "Extra":
            first_valid_index = 0
            remove_noise = False
        else:
            # Remove rows prior to inserting the samples.
            first_valid_index = df[df["counts/sec"] >= noise_max].index[0]

        df_no_noise = df.loc[first_valid_index:].reset_index(drop=True)

        if remove_noise:
            # Subtract the mean of the removed counts from the data.
            subtract = np.mean(
                df[0:(len(df) - len(df_no_noise))]["counts/sec"]
            )

            df_no_noise["counts/sec"] = (
                df_no_noise["counts/sec"] - subtract
            )

        # Validate interval jumps (10-minute intervals).
        df_no_noise = assert_interval_jumps(
            df_no_noise,
            filenames,
            f,
        )

        dfs_no_noise.append(df_no_noise)

    # Align replicate intervals.
    dfs_aligned = assert_interval_overlaps(dfs_no_noise)

    # Drop Lumi baseline column.
    for df in dfs_aligned:
        df.drop(" Baseline", axis=1, inplace=True)

    # Create results dataframe.
    full_df = create_sub_df(
        dfs_aligned,
        filenames,
        sample=sample,
    )

    # Save result (optional).
    if save_file:
        if sample is not None:
            filename = sample + "_"
        else:
            filename = "_".join(filenames)

        save_tissue_data(
            full_df,
            filename[0:-1],
            excel=False,
            output_folder=output_folder,
        )

    return full_df
