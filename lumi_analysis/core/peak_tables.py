import numpy as np
import pandas as pd
from typing import Any

from lumi_analysis.plotting.raw import (
    LUMI_AVERAGE_COLUMN,
    get_lumi_replicate_columns,
    get_lumi_time_axis,
)
from lumi_analysis.plotting.peaks import compute_peak_indices


def create_signal_peaks_periods_row(
    signal_name,
    time,
    signal,
    min_peak_distance_hours=20,
    prominence=None,
    decimals=2,
    period_as_text=True,
):
    # Create one table row containing peak times and periods for a single signal.
    time = np.asarray(time, dtype=float)
    signal = np.asarray(signal, dtype=float)

    peak_indices = compute_peak_indices(
        time=time,
        signal=signal,
        min_peak_distance_hours=min_peak_distance_hours,
        prominence=prominence,
    )

    peak_times = time[peak_indices]

    row: dict[str, Any] = {
        "replicate": signal_name,
    }

    for i, peak_time in enumerate(peak_times, start=1):
        row[f"peak {i}"] = round(float(peak_time), decimals)

        if i < len(peak_times):
            period = float(peak_times[i] - peak_times[i - 1])

            if period_as_text:
                row[f"Δ {i}-{i + 1}"] = f"({period:.{decimals}f} h)"
            else:
                row[f"Δ {i}-{i + 1}"] = round(period, decimals)

    return row


def create_group_peaks_periods_table(
    df,
    mean_replicate_cols=None,
    visible_replicate_cols=None,
    mean_col=LUMI_AVERAGE_COLUMN,
    recompute_mean=True,
    time_col=None,
    start_ct=0,
    interval_minutes=10,
    include_average=True,
    min_peak_distance_hours=20,
    peak_prominence=None,
    decimals=2,
    period_as_text=True,
):
    # Create a peaks/periods table for one Lumi group.
    all_replicate_cols = get_lumi_replicate_columns(df, mean_col=mean_col)

    if mean_replicate_cols is None:
        mean_replicate_cols = all_replicate_cols

    if visible_replicate_cols is None:
        visible_replicate_cols = all_replicate_cols

    time = get_lumi_time_axis(
        df=df,
        time_col=time_col,
        start_ct=start_ct,
        interval_minutes=interval_minutes,
    )

    rows = []

    for col in visible_replicate_cols:
        row = create_signal_peaks_periods_row(
            signal_name=col,
            time=time,
            signal=df[col].to_numpy(dtype=float),
            min_peak_distance_hours=min_peak_distance_hours,
            prominence=peak_prominence,
            decimals=decimals,
            period_as_text=period_as_text,
        )
        rows.append(row)

    if include_average:
        if recompute_mean:
            average_signal = df[mean_replicate_cols].mean(axis=1)
            average_name = "average"
        else:
            average_signal = df[mean_col]
            average_name = mean_col

        average_row = create_signal_peaks_periods_row(
            signal_name=average_name,
            time=time,
            signal=average_signal.to_numpy(dtype=float),
            min_peak_distance_hours=min_peak_distance_hours,
            prominence=peak_prominence,
            decimals=decimals,
            period_as_text=period_as_text,
        )
        rows.append(average_row)

    table = pd.DataFrame(rows)

    ordered_columns = ["replicate"]
    max_peak_number = _get_max_peak_number(table.columns)

    for i in range(1, max_peak_number + 1):
        ordered_columns.append(f"peak {i}")

        if i < max_peak_number:
            ordered_columns.append(f"Δ {i}-{i + 1}")

    table = table.reindex(columns=ordered_columns)

    return table


def create_all_group_peaks_periods_tables(
    analysis_result,
    config,
    get_group_setting,
):
    # Create one peaks/periods table per group.
    tables = {}

    for group_name, group_result in analysis_result["group_results"].items():
        group_df = group_result["full_df"]

        table = create_group_peaks_periods_table(
            df=group_df,
            mean_replicate_cols=get_group_setting(config, group_name, "mean_replicate_cols", None),
            visible_replicate_cols=get_group_setting(config, group_name, "visible_replicate_cols", None),
            recompute_mean=get_group_setting(config, group_name, "recompute_mean", True),
            start_ct=config.get("ct_start_hour", 0),
            interval_minutes=config.get("interval_minutes", 10),
            include_average=get_group_setting(config, group_name, "include_average_in_peak_table", True),
            min_peak_distance_hours=get_group_setting(config, group_name, "min_peak_distance_hours", 20),
            peak_prominence=get_group_setting(config, group_name, "peak_prominence", None),
            decimals=get_group_setting(config, group_name, "peak_table_decimals", 2),
            period_as_text=get_group_setting(config, group_name, "peak_table_period_as_text", True),
        )

        tables[group_name] = table

    return tables


def _get_max_peak_number(columns):
    # Extract the largest peak number from columns like "peak 1", "peak 2", etc.
    max_peak_number = 0

    for col in columns:
        if isinstance(col, str) and col.startswith("peak "):
            peak_number = int(col.replace("peak ", ""))
            max_peak_number = max(max_peak_number, peak_number)

    return max_peak_number
