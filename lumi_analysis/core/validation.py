import pandas as pd


def assert_interval_overlaps(dfs_no_noise):
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

    return dfs_aligned


def assert_interval_jumps(df_no_noise, filenames, file_num):
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

            print(f"completed missing interval on row {insert_index}, in file {filenames[file_num]}_Raw.")
        else:
            print("More than one consecutive interval missing.")
            # return

    return df_no_noise
