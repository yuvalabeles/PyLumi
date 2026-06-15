import numpy as np
import pandas as pd
from scipy.signal import find_peaks


def compute_linked_tissue_peaks(
    data,
    min_peak_distance_hours=20,
    prominence=None,
    first_peak_after_by_treatment=None,
):
    # Compute peak time for each experiment/tissue/mouse mean signal.
    # Select the first detected peak after the treatment-specific threshold, if given.

    peak_records = []

    grouped = data.groupby(
        ["experiment", "tissue", "mouse"],
        sort=False,
    )

    for (experiment, tissue, mouse), group_df in grouped:
        group_df = group_df.sort_values("time")

        time_series = group_df["time"].astype(float).reset_index(drop=True)
        signal_series = group_df["mean"].astype(float).reset_index(drop=True)

        if len(time_series) < 2:
            continue

        dt = time_series.diff().median()

        if dt <= 0:
            continue

        min_distance_points = max(
            1,
            int(round(min_peak_distance_hours / dt)),
        )

        signal_values = signal_series.tolist()

        peak_indices_array, _ = find_peaks(
            signal_values,
            distance=min_distance_points,
            prominence=prominence,
        )

        peak_indices = np.asarray(peak_indices_array)

        if first_peak_after_by_treatment is None:
            first_peak_after = None
        else:
            first_peak_after = first_peak_after_by_treatment.get(experiment)

        if first_peak_after is not None:
            peak_indices = np.asarray([
                int(index)
                for index in peak_indices
                if time_series.iloc[int(index)] >= first_peak_after
            ])

        if len(peak_indices) == 0:
            peak_time = np.nan
            peak_value = np.nan
        else:
            selected_peak_index = int(peak_indices[0])
            peak_time = time_series.iloc[selected_peak_index]
            peak_value = signal_series.iloc[selected_peak_index]

        peak_records.append({
            "experiment": experiment,
            "tissue": tissue,
            "mouse": mouse,
            "peak_time": peak_time,
            "peak_value": peak_value,
        })

    return pd.DataFrame(peak_records)
