import numpy as np
from scipy.signal import find_peaks


def compute_peak_indices(
    time,
    signal,
    min_peak_distance_hours=20,
    prominence=None,
):
    # Compute peak indices for a signal sampled along a time axis.
    time = np.asarray(time, dtype=float)
    signal = np.asarray(signal, dtype=float)

    if len(time) != len(signal):
        raise ValueError("time and signal must have the same length.")

    if len(time) < 2:
        return np.array([], dtype=int)

    dt = np.median(np.diff(time))

    if dt <= 0:
        raise ValueError("time must be strictly increasing.")

    min_distance_points = max(
        1,
        int(round(min_peak_distance_hours / dt)),
    )

    peak_indices, _ = find_peaks(
        signal,
        distance=min_distance_points,
        prominence=prominence,
    )

    return peak_indices


def plot_peaks_for_signal(
    ax,
    time,
    signal,
    color,
    show_text=False,
    min_peak_distance_hours=20,
    prominence=None,
    text_dx=2,
    text_dy=0,
    text_fontsize=8,
    zorder=6,
):
    # Plot peak vertical grid lines and optional peak-time labels for one signal.
    time = np.asarray(time, dtype=float)
    signal = np.asarray(signal, dtype=float)

    peak_indices = compute_peak_indices(
        time=time,
        signal=signal,
        min_peak_distance_hours=min_peak_distance_hours,
        prominence=prominence,
    )

    if len(peak_indices) == 0:
        return peak_indices

    for idx in peak_indices:
        peak_time = float(time[idx])

        ax.axvline(
            x=peak_time,
            color=color,
            linewidth=0.8,
            alpha=0.75,
            linestyle="--",
            zorder=zorder,
        )

    if show_text:
        y_min, y_max = ax.get_ylim()
        text_y = y_max - 0.04 * (y_max - y_min)

        for idx in peak_indices:
            peak_time = float(time[idx])

            ax.text(
                peak_time + text_dx,
                text_y + text_dy,
                f"{peak_time:.1f}",
                fontsize=text_fontsize,
                alpha=0.85,
                fontweight="bold",
                color=color,
                zorder=zorder + 1,
                ha="left",
                va="top",
            )

    return peak_indices
