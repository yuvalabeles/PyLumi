import numpy as np
import pandas as pd

from lumi_analysis.core.validation import (
    assert_interval_jumps,
    assert_interval_overlaps,
)


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
