import pandas as pd
from rich import print


def assert_interval_overlaps(dfs_no_noise):
    times = []

    for df in dfs_no_noise:
        time_col = pd.to_datetime(
            df["Time (hr:min)"],
            format="%H:%M"
        ).dt.floor("10min").dt.time

        times.append(time_col)

    latest_time = max(col.iloc[0] for col in times)

    indices = [
        col[col == latest_time].index[0]
        for col in times
    ]

    dfs_aligned = [
        df.iloc[start_idx:].reset_index(drop=True)
        for df, start_idx in zip(dfs_no_noise, indices)
    ]

    min_len = min(len(df) for df in dfs_aligned)

    dfs_aligned = [
        df.iloc[:min_len].reset_index(drop=True)
        for df in dfs_aligned
    ]

    return dfs_aligned


def assert_interval_jumps(df_no_noise, filenames, file_num, max_allowed_consecutive_missing=3):
    df = df_no_noise.copy().reset_index(drop=True)

    print("\n" + 27 * "-")
    print(
        f"Validating data for file [bold spring_green3]{filenames[file_num]}[/bold spring_green3]"
    )
    print(27 * "-")

    numeric_cols = df.select_dtypes(include="number").columns

    # Use elapsed experimental minutes instead of Date + Time.
    # This avoids false gaps when the Date column is wrong after midnight,
    # and avoids floating-point precision issues in Time (days).
    df["_elapsed_minutes"] = (
        df["Time (days)"].astype(float) * 24 * 60
    ).round().astype(int)

    df = df.set_index("_elapsed_minutes").sort_index()

    interval_minutes = 10

    full_index = pd.Index(
        range(
            int(df.index.min()),
            int(df.index.max()) + interval_minutes,
            interval_minutes
        ),
        name="_elapsed_minutes"
    )

    missing_times = full_index.difference(df.index)

    if len(missing_times) == 0:
        return df.reset_index(drop=True)

    missing_series = pd.Series(missing_times)
    gap_groups = (missing_series.diff() != interval_minutes).cumsum()

    gap_sizes = missing_series.groupby(gap_groups).size()
    longest_gap_group = gap_sizes.idxmax()
    longest_missing_gap = gap_sizes.max()

    longest_gap_times = missing_series[gap_groups == longest_gap_group]

    first_missing_time = longest_gap_times.iloc[0]
    last_missing_time = longest_gap_times.iloc[-1]

    row_before_time = first_missing_time - interval_minutes
    row_after_time = last_missing_time + interval_minutes

    row_before = df.index.get_loc(row_before_time) if row_before_time in df.index else "not found"
    row_after = df.index.get_loc(row_after_time) if row_after_time in df.index else "not found"

    if longest_missing_gap > max_allowed_consecutive_missing:
        raise ValueError(
            f"Cannot analyze file {filenames[file_num]}_Raw: "
            f"too many consecutive intervals are missing "
            f"({longest_missing_gap} consecutive 10-minute intervals). "
            f"Missing gap starts after row {row_before} "
            f"and ends before row {row_after}. "
            f"Time range: "
            f"{first_missing_time / 60:.2f} - "
            f"{last_missing_time / 60:.2f} experimental hours."
        )

    if longest_missing_gap > 1:
        print(
            f"[yellow]Warning:[/yellow] "
            f"{longest_missing_gap} consecutive intervals were completed."
        )

    # Reindex creates the missing rows.
    df = df.reindex(full_index)

    # Fill numeric columns by linear interpolation between the row above and the row below.
    df[numeric_cols] = df[numeric_cols].interpolate(method="index")

    # Rebuild Date and Time columns for inserted rows.
    base_date = pd.to_datetime(
        df_no_noise["Date"].iloc[0],
        format="%m/%d/%Y"
    ).normalize()

    datetime_values = base_date + pd.to_timedelta(df.index, unit="min")

    df["Date"] = datetime_values.strftime("%m/%d/%Y")
    df["Time (hr:min)"] = datetime_values.strftime("%H:%M")

    if "Time (days)" in df.columns:
        df["Time (days)"] = df.index / (24 * 60)

    for missing_time in missing_times:
        missing_datetime = base_date + pd.to_timedelta(missing_time, unit="min")

        print(
            f"[cyan]Completed missing interval[/cyan] at "
            f"[bold]{missing_datetime.strftime('%m/%d/%Y %H:%M')}[/bold]."
        )

    return df.reset_index(drop=True)
