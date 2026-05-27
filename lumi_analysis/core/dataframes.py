import numpy as np
import pandas as pd


def create_sub_df(dfs_aligned, filenames, sample=None):
    # Create a sub-dataframe for one sample/group and its replicates.
    full_df = pd.DataFrame({
        "Date": dfs_aligned[0]["Date"],
        "Time (hr:min)": dfs_aligned[0]["Time (hr:min)"],
        "Time (days)": dfs_aligned[0]["Time (days)"],
    })

    counts = pd.DataFrame()

    for i in range(len(dfs_aligned)):
        counts_sec = pd.to_numeric(
            dfs_aligned[i]["counts/sec"],
            errors="coerce"  # Ensure numeric dtype across pandas versions and malformed values
        )

        counts[filenames[i]] = counts_sec
        full_df[filenames[i]] = counts_sec.round(4)

    if sample != "Extra":
        full_df["counts/sec (avg)"] = counts.mean(axis=1).round(4)
    else:
        full_df = full_df.rename(columns={"Time (hr:min)": "Time"})

    return full_df


def create_condensed_df(
    complete_df,
    interval_minutes=10,
    ct_start_hour=0,
):
    # Create a dataframe for all data without date/time columns.
    # CT is shifted according to ct_start_hour.
    complete_df = complete_df.copy()

    n = len(complete_df)

    time_col = (
        np.arange(n) * (interval_minutes / 60)
        + ct_start_hour
    )

    indices = np.array(range(len(complete_df)))

    complete_df.insert(0, " ", indices)
    complete_df.insert(0, "CT [in hours]", time_col)
    complete_df["CT [in hours]"] = complete_df["CT [in hours]"].round(2)

    cols_to_drop = ["Date", "Time (hr:min)", "Time (days)"]
    condensed_df = complete_df.drop(columns=cols_to_drop)

    return condensed_df


def create_complete_df(full_dfs):
    # Create the full dataframe of the analysis.
    result_parts = []
    blank = pd.DataFrame(np.nan, index=full_dfs[0].index, columns=[""])

    for i, df_ in enumerate(full_dfs):
        result_parts.append(df_)

        if i < len(full_dfs) - 1:
            result_parts.append(blank.copy())

    complete_df = pd.concat(result_parts, axis=1)

    return complete_df
