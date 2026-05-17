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
    marker="x",
    markersize=7,
    markeredgewidth=1.5,
    text_dx=2,
    text_dy=0,
    text_fontsize=8,
    zorder=6,
):
    # Plot peak markers and optional peak-time labels for one signal.
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

    ax.plot(
        time[peak_indices],
        signal[peak_indices],
        linestyle="None",
        marker=marker,
        markersize=markersize,
        markeredgewidth=markeredgewidth,
        color=color,
        zorder=zorder,
    )

    if show_text:
        for idx in peak_indices:
            ax.text(
                float(time[idx]) + text_dx,
                float(signal[idx]) + text_dy,
                f"{float(time[idx]):.1f}",
                fontsize=text_fontsize,
                alpha=0.8,
                fontweight="bold",
                color=color,
                zorder=zorder + 1,
            )

    return peak_indices
