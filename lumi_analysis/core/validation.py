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


def _add_interval_index(df, interval_minutes):
    df = df.copy().reset_index(drop=True)

    elapsed_minutes = (
        df["Time (days)"].astype(float) * 24 * 60
    ).round().astype(int)

    first_elapsed_minute = elapsed_minutes.iloc[0]

    df["_elapsed_minutes"] = elapsed_minutes
    df["_interval_index"] = (
        (elapsed_minutes - first_elapsed_minute) / interval_minutes
    ).round().astype(int)

    return df.set_index("_interval_index").sort_index()


def _get_expected_interval_index(df):
    return pd.Index(
        range(
            int(df.index.min()),
            int(df.index.max()) + 1
        ),
        name="_interval_index"
    )


def _get_longest_consecutive_gap(times):
    if len(times) == 0:
        return 0, None, None

    missing_series = pd.Series(sorted(times))
    gap_groups = (missing_series.diff() != 1).cumsum()

    gap_sizes = missing_series.groupby(gap_groups).size()
    longest_gap_group = gap_sizes.idxmax()
    longest_gap_size = gap_sizes.max()

    longest_gap_times = missing_series[gap_groups == longest_gap_group]

    return (
        longest_gap_size,
        longest_gap_times.iloc[0],
        longest_gap_times.iloc[-1],
    )


def assert_group_interval_jumps(
    dfs_no_noise,
    filenames,
    group_name=None,
    max_allowed_consecutive_missing=3,
    interval_minutes=10,
):
    prepared_dfs = [
        _add_interval_index(df, interval_minutes)
        for df in dfs_no_noise
    ]

    expected_indices = [
        _get_expected_interval_index(df)
        for df in prepared_dfs
    ]

    missing_by_file = [
        set(expected_index.difference(df.index))
        for df, expected_index in zip(prepared_dfs, expected_indices)
    ]

    all_candidate_missing_indices = sorted(
        set().union(*missing_by_file)
    )

    shared_missing_indices = set()
    fill_missing_by_file = [
        set()
        for _ in prepared_dfs
    ]

    for missing_index in all_candidate_missing_indices:
        eligible_files = [
            file_num
            for file_num, expected_index in enumerate(expected_indices)
            if missing_index in expected_index
        ]

        files_missing_this_index = [
            file_num
            for file_num in eligible_files
            if missing_index in missing_by_file[file_num]
        ]

        if len(files_missing_this_index) == len(eligible_files):
            shared_missing_indices.add(missing_index)
        else:
            for file_num in files_missing_this_index:
                fill_missing_by_file[file_num].add(missing_index)

    if shared_missing_indices:
        longest_shared_gap, first_shared_index, last_shared_index = _get_longest_consecutive_gap(
            shared_missing_indices
        )

        print(
            f"\n[yellow]Warning:[/yellow] "
            f"shared missing interval(s) detected in group "
            f"[bold]{group_name}[/bold]. "
            f"These intervals were not completed because they are missing "
            f"from all relevant replicates."
        )

        print(
            f"Longest shared gap: {longest_shared_gap} interval(s), "
            f"from interval {first_shared_index} to interval {last_shared_index}."
        )

    completed_dfs = []

    for file_num, df in enumerate(prepared_dfs):
        # print("\n" + 27 * "-")
        # print(
        #     f"Validating data for file "
        #     f"[bold spring_green3]{filenames[file_num]}[/bold spring_green3]"
        # )
        # print(27 * "-")

        missing_indices_to_fill = sorted(fill_missing_by_file[file_num])

        longest_missing_gap, first_missing_index, last_missing_index = _get_longest_consecutive_gap(
            missing_indices_to_fill
        )

        if longest_missing_gap > max_allowed_consecutive_missing:
            row_before_index = first_missing_index - 1
            row_after_index = last_missing_index + 1

            row_before = df.index.get_loc(row_before_index) if row_before_index in df.index else "not found"
            row_after = df.index.get_loc(row_after_index) if row_after_index in df.index else "not found"

            raise ValueError(
                f"Cannot analyze file {filenames[file_num]}_Raw: "
                f"too many consecutive intervals are missing "
                f"({longest_missing_gap} consecutive 10-minute intervals). "
                f"Missing gap starts after row {row_before} "
                f"and ends before row {row_after}. "
                f"Missing interval range: "
                f"{first_missing_index} - {last_missing_index}."
            )

        if longest_missing_gap > 1:
            print(
                f"[yellow]Warning:[/yellow] "
                f"{longest_missing_gap} consecutive intervals were completed."
            )

        if missing_indices_to_fill:
            numeric_cols = df.select_dtypes(include="number").columns

            new_index = pd.Index(
                sorted(set(df.index).union(missing_indices_to_fill)),
                name="_interval_index"
            )

            df = df.reindex(new_index)

            df[numeric_cols] = df[numeric_cols].interpolate(method="index")

            first_original_elapsed_minute = int(
                (
                    dfs_no_noise[file_num]["Time (days)"].astype(float).iloc[0]
                    * 24
                    * 60
                ).round()
            )

            base_date = pd.to_datetime(
                dfs_no_noise[file_num]["Date"].iloc[0],
                format="%m/%d/%Y"
            ).normalize()

            elapsed_minutes = (
                first_original_elapsed_minute
                + df.index.astype(int) * interval_minutes
            )

            datetime_values = base_date + pd.to_timedelta(elapsed_minutes, unit="min")

            df["Date"] = datetime_values.strftime("%m/%d/%Y")
            df["Time (hr:min)"] = datetime_values.strftime("%H:%M")
            df["Time (days)"] = elapsed_minutes / (24 * 60)

            for missing_index in missing_indices_to_fill:
                missing_elapsed_minutes = (
                    first_original_elapsed_minute
                    + missing_index * interval_minutes
                )

                missing_datetime = base_date + pd.to_timedelta(
                    missing_elapsed_minutes,
                    unit="min"
                )

                print(
                    f"[cyan]Completed missing interval[/cyan] at "
                    f"[bold]{missing_datetime.strftime('%m/%d/%Y %H:%M')}[/bold], on file "
                    f"[bold spring_green3]{filenames[file_num]}[/bold spring_green3]"
                )

        completed_dfs.append(
            df.drop(columns=["_elapsed_minutes"], errors="ignore").reset_index(drop=True)
        )

    return completed_dfs
