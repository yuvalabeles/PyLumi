import numpy as np

from lumi_analysis.core.validation import assert_interval_jumps


def remove_initial_noise(
    df,
    noise_max,
    remove_noise=True,
    keep_all_rows=False,
):
    if keep_all_rows:
        first_valid_index = 0
        remove_noise = False
    else:
        first_valid_index = df[df["counts/sec"] >= noise_max].index[0]

    df_no_noise = df.loc[first_valid_index:].reset_index(drop=True)

    if remove_noise:
        subtract = np.mean(
            df[0:(len(df) - len(df_no_noise))]["counts/sec"]
        )

        df_no_noise["counts/sec"] = (
            df_no_noise["counts/sec"] - subtract
        )

    return df_no_noise


def preprocess_replicates(
    dfs,
    filenames,
    noise_max,
    remove_noise=True,
    keep_all_rows=False,
):
    processed_dfs = []

    for file_num, df in enumerate(dfs):
        df_processed = remove_initial_noise(
            df=df,
            noise_max=noise_max,
            remove_noise=remove_noise,
            keep_all_rows=keep_all_rows,
        )

        df_processed = assert_interval_jumps(
            df_processed,
            filenames,
            file_num,
        )

        processed_dfs.append(df_processed)

    return processed_dfs


def crop_replicates_tail(
    dfs,
    max_rows=None,
    max_hours=None,
    max_days=None,
    interval_minutes=10,
):
    # Crop all replicate dataframes to the same requested length.
    active_limits = [
        value is not None
        for value in [max_rows, max_hours, max_days]
    ]

    if sum(active_limits) > 1:
        raise ValueError(
            "Use only one of: max_rows, max_hours, max_days."
        )

    if max_days is not None:
        max_hours = max_days * 24

    if max_hours is not None:
        rows_to_keep = int(max_hours * 60 / interval_minutes)
    elif max_rows is not None:
        rows_to_keep = int(max_rows)
    else:
        return dfs

    if rows_to_keep <= 0:
        raise ValueError("Tail crop length must be greater than 0.")

    return [
        df.iloc[:rows_to_keep].reset_index(drop=True)
        for df in dfs
    ]
