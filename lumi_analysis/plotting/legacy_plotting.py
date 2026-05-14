import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path
from scipy.signal import find_peaks
from statsmodels.nonparametric.smoothers_lowess import lowess
from matplotlib.patches import Patch


# =============================================================================
# Signal preparation
# =============================================================================

def prepare_signal(counts, interval=10):
    # Convert counts into a numeric array and create a time axis in hours.
    step = interval / 60
    ignore_window = interval / 60

    counts = np.array(counts, dtype=float)
    time = np.cumsum(step * np.ones_like(counts)) + ignore_window

    return counts, time


# =============================================================================
# Baseline computation methods
# =============================================================================

def moving_average(counts, window_hours=24, samples_per_hour=6):
    counts = np.asarray(counts, dtype=float)

    window_size = int(window_hours * samples_per_hour)

    if window_size < 1:
        raise ValueError("window_hours is too small and results in window_size < 1")

    if window_size % 2 == 0:
        window_size += 1

    half_window = window_size // 2
    baseline = np.empty_like(counts, dtype=float)

    for i in range(len(counts)):
        start = max(0, i - half_window)
        end = min(len(counts), i + half_window + 1)
        baseline[i] = np.mean(counts[start:end])

    return baseline


def smooth_lowess(counts, window_hours=50, step=1 / 6):
    counts = np.asarray(counts, dtype=float)
    n = len(counts)

    if n == 0:
        return counts.copy()

    window_points = int(np.floor(window_hours / step))

    frac = window_points / n
    frac = max(min(frac, 1.0), 1.0 / n)

    x = np.arange(n)
    baseline = lowess(counts, x, frac=frac, it=0, return_sorted=False)

    return baseline


def linear_regression(counts, time, window_hours=48):
    time = np.asarray(time, dtype=float)
    counts = np.asarray(counts, dtype=float)

    n = len(counts)
    baseline = np.full(n, np.nan, dtype=float)

    half_window = window_hours / 2

    for i in range(n):
        t_center = time[i]

        mask = (
            (time >= t_center - half_window) &
            (time <= t_center + half_window)
        )

        x_win = time[mask]
        y_win = counts[mask]

        if len(x_win) < 2:
            continue

        m, b = np.polyfit(x_win, y_win, 1)
        baseline[i] = m * t_center + b

    return baseline


def compute_baselines(counts, time):
    ma_24 = moving_average(counts)
    smooth_50 = smooth_lowess(counts)
    lr_48 = linear_regression(counts, time)

    baselines = [ma_24, smooth_50, lr_48]
    labels = [
        "Moving Average [w=24]",
        "Smoothing (LOWESS) [w=50]",
        "Linear Regression [w=48]",
    ]
    colors = ["b", "r", "orange"]

    return baselines, labels, colors


# =============================================================================
# Peaks and periods
# =============================================================================

def compute_cycle_periods(
    time,
    signal,
    min_peak_distance_hours=20,
    prominence=None,
    ignore=None,
):
    # Compute peak locations and peak-to-peak periods.
    time = np.asarray(time, dtype=float)
    signal = np.asarray(signal, dtype=float)

    dt = np.median(np.diff(time))
    min_distance_points = max(1, int(round(min_peak_distance_hours / dt)))

    peak_indices, _ = find_peaks(
        signal,
        distance=min_distance_points,
        prominence=prominence,
    )

    if ignore is not None and len(peak_indices) > 0:
        peak_indices = peak_indices[peak_indices < ignore]

    peak_times = time[peak_indices]
    peak_values = signal[peak_indices]
    peak_to_peak_periods = np.diff(peak_times)
    cycle_mid_times = (peak_times[:-1] + peak_times[1:]) / 2

    return {
        "peak_indices": peak_indices,
        "peak_times": peak_times,
        "peak_values": peak_values,
        "peak_to_peak_periods": peak_to_peak_periods,
        "cycle_mid_times": cycle_mid_times,
    }


# =============================================================================
# General helpers
# =============================================================================

def save_plot(label, output_folder="plots"):
    Path(output_folder).mkdir(exist_ok=True)

    safe_label = label.lower().replace("/", "-")
    figure_name = Path(output_folder) / f"{safe_label}.png"

    plt.savefig(figure_name, dpi=300, bbox_inches="tight")


def format_df(df_to_format, decimals=2):
    df_display = df_to_format.copy()

    for col in df_display.columns:
        df_display[col] = df_display[col].apply(
            lambda x: f"{x:.{decimals}f}" if isinstance(x, (int, float, np.number)) else x
        )

    return df_display


def expand_list_columns_for_table(df):
    expanded_parts = []
    group_sizes = {}

    for col in df.columns:
        max_len = df[col].apply(
            lambda x: len(x) if isinstance(x, (list, tuple, np.ndarray)) else 1
        ).max()

        expanded_col = pd.DataFrame(index=df.index)

        for i in range(max_len):
            expanded_col[(col, i)] = df[col].apply(
                lambda x: x[i] if isinstance(x, (list, tuple, np.ndarray)) and i < len(x) else ""
            )

        group_sizes[col] = max_len
        expanded_parts.append(expanded_col)

    return pd.concat(expanded_parts, axis=1), group_sizes


def lighten_color(color, amount=0.5):
    rgb = plt.matplotlib.colors.to_rgb(color)
    return tuple(1 - amount * (1 - c) for c in rgb)


# =============================================================================
# Basic signal plots
# =============================================================================

def plot_raw_data(counts, time, label, save=True, peaks=None, close=True):
    plot_id = 1
    plt.figure(plot_id)

    plt.plot(time, counts, ".k", markersize=1, label=label.lower(), alpha=0.5)

    if peaks is not None and len(peaks) > 0:
        label = label + " with Peaks"
        plt.plot(time[peaks], counts[peaks], "xg", markersize=5, zorder=3)

        for idx in peaks:
            plt.text(
                float(time[idx]) + 2,
                float(counts[idx]),
                f"{time[idx]:.1f}",
                fontsize=8,
                alpha=0.7,
                fontweight="bold",
            )

    plt.title(label, pad=15, fontsize=15)

    plt.xlabel("CT [hr]", labelpad=10)
    plt.xlim(left=0)

    ticks = range(0, int(max(time)) + 25, 24)
    plt.xticks(ticks, fontsize=7)
    plt.xticks(np.arange(0, int(max(time)) + 25, 12), minor=True)

    plt.grid(axis="x", which="major", linestyle="-", linewidth=0.8, alpha=0.95)
    plt.grid(axis="x", which="minor", linestyle="-", linewidth=0.8, alpha=0.5)

    plt.ylabel("Bioluminescence (counts/second)", labelpad=15)
    plt.ylim(0, max(counts) + 500)
    plt.yticks(fontsize=7)

    plt.legend(loc="best")

    if save:
        save_plot(label)

    if close:
        plt.close(plot_id)

    return plot_id


def plot_baseline(plot_id, time, baseline, label, color, close=True):
    plt.figure(plot_id)

    plt.plot(time, baseline, color, linewidth=1, label=label.lower())
    plt.title("Baseline Using " + label, pad=15, fontsize=15)
    plt.legend(loc="best")

    save_plot("Baseline = " + label)

    if close:
        plt.close(plot_id)

    return plot_id


def plot_data_post_baseline_subtraction(
    plot_id,
    counts,
    time,
    baseline,
    label,
    color,
    same_plot=False,
):
    plt.figure(plot_id)

    if not same_plot:
        label = "Signal (-) " + label.lower()

    data = counts - baseline

    cycle_periods = compute_cycle_periods(
        time,
        data,
        min_peak_distance_hours=20,
        prominence=0.05,
    )
    peaks_data = cycle_periods["peak_indices"]

    if same_plot:
        line_style = "-"
        peak_color = color
    else:
        line_style = "--"
        peak_color = "g"

    plt.plot(time, data, line_style, color=color, linewidth=1, label=label.lower())
    plt.plot(time[peaks_data], data[peaks_data], "x", color=peak_color, markersize=5, zorder=3)

    if not same_plot:
        for idx in peaks_data:
            plt.text(
                float(time[idx]) + 2,
                float(data[idx]),
                f"{time[idx]:.1f}",
                fontsize=8,
                alpha=0.7,
                fontweight="bold",
            )
    else:
        for idx in peaks_data:
            plt.axvline(x=time[idx], linestyle="--", linewidth=0.8, alpha=0.5, color=color)

    if same_plot:
        label = "3 Methods of Baseline Computation (Subtraction)"

    plt.title(label, pad=15, fontsize=15)
    plt.ylim(bottom=min(data) - 500)

    plt.legend(fontsize=8, markerscale=0.7, labelspacing=0.3, handletextpad=0.3, borderpad=0.3)

    save_plot(label)

    if not same_plot:
        plt.close(plot_id)


def plot_data_post_baseline_division(
    plot_id,
    counts,
    time,
    baseline,
    label,
    color,
    peaks=None,
    same_plot=False,
):
    plt.figure(plot_id)

    data = counts / baseline

    cycle_periods = compute_cycle_periods(
        time,
        data,
        min_peak_distance_hours=20,
        prominence=0.05,
    )
    peaks_ratio = cycle_periods["peak_indices"]

    if same_plot:
        line_width, line_style, peak_color = 1, "-", color
    else:
        line_width, line_style, peak_color = 1.5, "--", "g"

    plt.plot(time, data, line_style, color=color, linewidth=line_width, label=label.lower())
    plt.plot(time[peaks_ratio], data[peaks_ratio], "x", color=peak_color, markersize=5, zorder=3)
    plt.plot(time[peaks_ratio], data[peaks_ratio], "ko", ms=1, zorder=4)

    if not same_plot:
        for idx in peaks_ratio:
            plt.text(
                float(time[idx]) + 2,
                float(data[idx]),
                f"{time[idx]:.1f}",
                fontsize=8,
                alpha=0.7,
                fontweight="bold",
            )
    elif peaks is not None:
        for idx in peaks:
            plt.axvline(x=time[idx], linestyle="--", linewidth=0.8, alpha=0.9, color="g")

    if same_plot:
        label = "3 Methods of Baseline Computation (Ratio)"
    else:
        label = "Signal (Ratio) " + label

    plt.title(label, pad=15, fontsize=15)

    plt.xlabel("CT [hr]", labelpad=10)
    plt.xlim(left=0)

    ticks = range(0, int(max(time)) + 25, 24)
    plt.xticks(ticks, fontsize=7)
    plt.xticks(np.arange(0, int(max(time)) + 25, 12), minor=True)

    plt.grid(axis="x", which="major", linestyle="-", linewidth=0.8, alpha=0.95)
    plt.grid(axis="x", which="minor", linestyle="-", linewidth=0.8, alpha=0.5)

    plt.ylabel("normalized signal (fold change)", labelpad=15)
    plt.yticks(fontsize=7)

    plt.legend(fontsize=8, markerscale=0.7, labelspacing=0.3, handletextpad=0.3, borderpad=0.3)

    save_plot(label)

    if not same_plot:
        plt.close(plot_id)


def plot_all_baselines(counts, time, baselines, labels, colors, peaks_raw_data=None, ratio=False):
    if ratio:
        plot_id = 10

        for i in range(len(baselines)):
            plot_data_post_baseline_division(
                plot_id,
                counts,
                time,
                baselines[i],
                labels[i],
                colors[i],
                peaks=peaks_raw_data,
                same_plot=True,
            )
    else:
        plot_id = plot_raw_data(
            counts,
            time,
            "Raw Data",
            save=False,
            close=False,
            peaks=peaks_raw_data,
        )

        for i in range(len(baselines)):
            plot_data_post_baseline_subtraction(
                plot_id,
                counts,
                time,
                baselines[i],
                labels[i],
                colors[i],
                same_plot=True,
            )

    if peaks_raw_data is not None:
        for idx in peaks_raw_data:
            plt.axvline(x=time[idx], linestyle="--", linewidth=0.8, alpha=0.9, color="g")

    plt.close(plot_id)


def plot_signal(counts):
    counts, time = prepare_signal(counts)

    plot_raw_data(counts, time, "Raw Data")

    cycle_periods = compute_cycle_periods(
        time,
        counts,
        min_peak_distance_hours=20,
        prominence=0.05,
    )
    peaks_raw_data = cycle_periods["peak_indices"]

    plot_raw_data(counts, time, "Raw Data", peaks=peaks_raw_data)

    baselines, labels, colors = compute_baselines(counts, time)

    plot_all_baselines(counts, time, baselines, labels, colors, peaks_raw_data)
    plot_all_baselines(counts, time, baselines, labels, colors, peaks_raw_data, ratio=True)

    for i in range(len(baselines)):
        plot_id = plot_raw_data(
            counts,
            time,
            "Raw Data",
            save=False,
            peaks=peaks_raw_data,
            close=False,
        )
        plot_id = plot_baseline(
            plot_id,
            time,
            baselines[i],
            labels[i],
            colors[i],
            close=False,
        )
        plot_data_post_baseline_subtraction(
            plot_id,
            counts,
            time,
            baselines[i],
            labels[i],
            colors[i],
        )
        plot_data_post_baseline_division(
            5,
            counts,
            time,
            baselines[i],
            labels[i],
            colors[i],
        )


# =============================================================================
# Lumi replicate plot
# =============================================================================

def plot_lumi_counts(
    df,
    title=None,
    limitY=None,
    path=None,
    description=None,
    plot_peaks=False,
    smooth=None,
    plot_table=False,
    start_CT=0,
    interval_minutes=10,
    min_peak_distance_hours=15,
    prominence=0.05,
):
    periods_rows = []
    row_colors = []
    maxY = 0

    ct_hours = start_CT + np.arange(len(df)) * (interval_minutes / 60)

    sample_cols = df.columns[:-1]
    mean_col = df.columns[-1]

    plt.figure(figsize=(9, 5))

    for sample_idx, col in enumerate(sample_cols, start=1):
        maxY = max(maxY, df[col].max())

        current_smooth = smooth

        if (plot_peaks or plot_table) and current_smooth is None:
            current_smooth = 3

        if current_smooth is not None:
            col_signal = smooth_lowess(
                df[col],
                window_hours=current_smooth,
                step=interval_minutes / 60,
            )
        else:
            col_signal = df[col]

        line, = plt.plot(
            ct_hours,
            col_signal,
            linewidth=2,
            label=f"Series{sample_idx}",
        )

        cycle_periods = compute_cycle_periods(
            ct_hours - start_CT,
            col_signal,
            min_peak_distance_hours=min_peak_distance_hours,
            prominence=prominence,
        )

        peak_indices = cycle_periods["peak_indices"]
        cycle_periods["peak_times"] = cycle_periods["peak_times"] + start_CT

        periods_rows.append({
            "replicate": f"Series{sample_idx}",
            "Peaks [CT]": cycle_periods["peak_times"].tolist(),
            "Periods [hours]": cycle_periods["peak_to_peak_periods"].tolist(),
        })

        color_line = line.get_color()
        row_colors.append(color_line)

        if plot_peaks:
            for idx in peak_indices:
                plt.axvline(
                    x=float(ct_hours[idx]),
                    linestyle="--",
                    linewidth=0.8,
                    alpha=0.95,
                    color=color_line,
                )

    if smooth is not None:
        mean_col_signal = smooth_lowess(
            df[mean_col],
            window_hours=smooth,
            step=interval_minutes / 60,
        )
    else:
        mean_col_signal = df[mean_col]

    mean_line, = plt.plot(
        ct_hours,
        mean_col_signal,
        linewidth=4,
        label="average",
    )

    cycle_periods = compute_cycle_periods(
        ct_hours - start_CT,
        mean_col_signal,
        min_peak_distance_hours=min_peak_distance_hours,
        prominence=prominence,
    )

    peak_indices = cycle_periods["peak_indices"]
    cycle_periods["peak_times"] = cycle_periods["peak_times"] + start_CT

    periods_rows.append({
        "replicate": "Series Avg.",
        "Peaks [CT]": cycle_periods["peak_times"].tolist(),
        "Periods [hours]": cycle_periods["peak_to_peak_periods"].tolist(),
    })

    color_line = mean_line.get_color()
    row_colors.append(color_line)

    if limitY is None:
        limitY = maxY + 20

    if plot_peaks:
        for idx in peak_indices:
            plt.axvline(
                x=float(ct_hours[idx]),
                linestyle="--",
                linewidth=1.5,
                alpha=0.95,
                color=color_line,
            )
            plt.text(
                float(ct_hours[idx]) + 2,
                limitY * 0.95,
                f"{float(ct_hours[idx]):.1f}",
                fontsize=9,
                alpha=0.7,
                fontweight="bold",
            )

    periods_df = pd.DataFrame(periods_rows)

    periods_df["Peaks [CT]"] = periods_df["Peaks [CT]"].apply(
        lambda lst: [round(x, 2) for x in lst]
    )

    periods_df["Periods [hours]"] = periods_df["Periods [hours]"].apply(
        lambda lst: [round(x, 2) for x in lst]
    )

    periods_df = periods_df.set_index("replicate")

    plt.xlabel("CT [hours]", labelpad=10, fontsize=12)

    ticks = range(0, int(max(ct_hours)), 12)
    plt.xticks(ticks, alpha=0.8)
    plt.xlim(left=0)

    plt.ylabel("counts / second", labelpad=15, fontsize=12)
    plt.yticks(alpha=0.8)
    plt.ylim((0, limitY))

    plt.title(title, pad=20, fontsize=20)

    plt.legend(
        loc="upper center",
        bbox_to_anchor=(0.5, -0.18),
        ncol=6,
        frameon=False,
        fontsize=12,
    )

    plt.grid(True, alpha=0.6)

    fig = plt.gcf()
    fig.patch.set_edgecolor("black")
    fig.patch.set_linewidth(1)

    if description is not None:
        plt.figtext(
            0.99,
            0.99,
            description,
            ha="right",
            va="top",
            fontsize=10,
        )

    if path is not None:
        if plot_peaks:
            save_to = path + "_PEAKS_plot.png"
        else:
            save_to = path + "_plot.png"

        plt.savefig(save_to, dpi=300, bbox_inches="tight", facecolor="white")

    plt.close()

    if plot_table and path is not None:
        create_table_with_subcolumns(
            periods_df.copy(),
            row_label_colors=row_colors,
            title=title,
            save_path=path + "_periods_table.png",
            description=description,
        )

    return periods_df


# =============================================================================
# Table plots
# =============================================================================

def create_table_with_subcolumns(
    df,
    title=None,
    row_label_colors=None,
    decimals=1,
    figsize=(12, 4),
    font_size=17,
    header_font_size=20,
    save_path=None,
    description=None,
):
    df_table, group_sizes = expand_list_columns_for_table(df)

    df_display = format_df(df_table, decimals=decimals)

    fig, ax = plt.subplots(figsize=figsize)
    ax.axis("off")

    table = ax.table(
        cellText=df_display.values,
        rowLabels=df_display.index,
        colLabels=[""] * len(df_display.columns),
        cellLoc="center",
        rowLoc="center",
        loc="center",
        bbox=[0, 0, 1, 0.75],
    )

    table.auto_set_font_size(False)
    table.set_fontsize(font_size)

    for (row, col), cell in table.get_celld().items():
        cell.set_edgecolor("black")
        cell.set_linewidth(2)
        cell.PAD = 0.25

        if row == 0:
            cell.set_height(0.0001)
            cell.set_linewidth(0)
            cell.set_edgecolor("none")
            cell.set_facecolor("none")

    n_cols = len(df_display.columns)
    sub_col_width = 0.85 / n_cols

    for (row, col), cell in table.get_celld().items():
        if col >= 0:
            cell.set_width(sub_col_width)

    if row_label_colors is not None:
        row_shade_amounts = [0.3, 0.55]

        for row_i, color in enumerate(row_label_colors, start=1):
            col_idx = 0

            for group_i, size in enumerate(group_sizes.values()):
                shade = lighten_color(
                    color,
                    amount=row_shade_amounts[group_i % len(row_shade_amounts)],
                )

                for col in range(col_idx, col_idx + size):
                    table[(row_i, col)].set_facecolor(shade)

                col_idx += size

    fig.canvas.draw()

    start_col = 0

    for master_label, size in group_sizes.items():
        first_cell = table[(1, start_col)]
        last_cell = table[(1, start_col + size - 1)]

        x_left = first_cell.get_x()
        x_right = last_cell.get_x() + last_cell.get_width()
        x_center = (x_left + x_right) / 2

        y_top = first_cell.get_y() + first_cell.get_height()

        ax.text(
            x_center,
            y_top + 0.03,
            str(master_label),
            ha="center",
            va="bottom",
            fontsize=header_font_size,
            fontweight="bold",
            transform=ax.transAxes,
        )

        start_col += size

    if row_label_colors is not None:
        for i, label in enumerate(df_display.index, start=1):
            if i - 1 < len(row_label_colors):
                table[(i, -1)].get_text().set_color(row_label_colors[i - 1])
                table[(i, -1)].set_text_props(weight="bold")

    if title is not None:
        plt.figtext(0.05, 0.95, title + ":", ha="left", va="top", fontsize=30)

    if description is not None:
        plt.figtext(
            0.99,
            0.99,
            description,
            ha="right",
            va="top",
            fontsize=int(header_font_size * 0.85),
        )

    plt.tight_layout()

    if save_path is not None:
        plt.savefig(save_path, dpi=300, bbox_inches="tight")

    plt.close(fig)

    return table


def draw_single_table(
    ax,
    df_display,
    table_title,
    row_label_colors=None,
    font_size=22,
    header_font_size=30,
    avg=False,
    description=None,
):
    ax.axis("off")

    table = ax.table(
        cellText=df_display.values,
        rowLabels=df_display.index,
        cellLoc="center",
        rowLoc="center",
        loc="center",
        bbox=[0, 0, 1, 0.82],
    )

    table.auto_set_font_size(False)
    table.set_fontsize(font_size)

    n_cols = len(df_display.columns)
    sub_col_width = 0.85 / n_cols

    for (row, col), cell in table.get_celld().items():
        cell.set_edgecolor("black")
        cell.set_linewidth(2)

        if col >= 0:
            cell.set_width(sub_col_width)

    if row_label_colors is not None:
        for row_i, color in enumerate(row_label_colors, start=0):
            if row_i < len(df_display.index):
                if row_i == 0:
                    color = "black"

                for col in range(n_cols):
                    reference_value = df_display.iloc[0, col]
                    current_value = df_display.iloc[row_i, col]

                    if row_i > 0 and current_value != reference_value:
                        color_b = "#EAF3FF" if current_value > reference_value else "#E6E6E6"
                        table[(row_i, col)].set_facecolor(color_b)
                        table[(row_i, col)].set_text_props(weight="bold")

                    table[(row_i, col)].get_text().set_color(color)

                table[(row_i, -1)].get_text().set_color(color)

    if not avg:
        ax.text(
            0.5,
            1.03,
            table_title,
            ha="center",
            va="bottom",
            fontsize=header_font_size,
            fontweight="bold",
            transform=ax.transAxes,
        )
    else:
        target_col = len(df_display.columns) - 1

        for (row, col), cell in table.get_celld().items():
            if col == target_col:
                cell.set_linewidth(4)
                cell.set_edgecolor("black")

        ax.text(
            0.99,
            1.12,
            table_title,
            ha="right",
            va="top",
            fontweight="bold",
            fontsize=header_font_size,
        )

        if description is not None:
            plt.figtext(
                -0.32,
                0.99,
                description[1:-1] + ":",
                ha="left",
                va="top",
                fontsize=0.95 * font_size,
                fontstyle="italic",
            )

    return table


def create_two_stacked_tables(
    df,
    title=None,
    row_label_colors=None,
    decimals=2,
    figsize=(12, 13),
    font_size=22,
    header_font_size=30,
    save_path=None,
    description=None,
    peaks_col="Peaks [CT]",
    periods_col="Periods [hours]",
):
    peaks_df = df[[peaks_col]].copy()
    periods_df = df[[periods_col]].copy()

    peaks_table, _ = expand_list_columns_for_table(peaks_df)
    periods_table, _ = expand_list_columns_for_table(periods_df)

    peaks_display = format_df(peaks_table, decimals=decimals)
    periods_display = format_df(periods_table, decimals=decimals)

    fig, axes = plt.subplots(
        2,
        1,
        figsize=figsize,
        gridspec_kw={"height_ratios": [1, 1], "hspace": 0.25},
    )

    if description is not None:
        plt.figtext(
            -0.32,
            0.95,
            description[1:-1] + ":",
            ha="left",
            va="top",
            fontsize=0.95 * font_size,
            fontstyle="italic",
        )

    draw_single_table(
        axes[0],
        peaks_display,
        peaks_col,
        row_label_colors=row_label_colors,
        font_size=font_size,
        header_font_size=header_font_size,
    )

    draw_single_table(
        axes[1],
        periods_display,
        periods_col,
        row_label_colors=row_label_colors,
        font_size=font_size,
        header_font_size=header_font_size,
    )

    legend_elements = [
        Patch(facecolor="#EAF3FF", edgecolor="black", label="higher"),
        Patch(facecolor="#E6E6E6", edgecolor="black", label="lower"),
    ]

    plt.legend(
        handles=legend_elements,
        loc="lower center",
        bbox_to_anchor=(-0.21, -0.24),
        ncol=3,
        frameon=True,
        fontsize=font_size * 0.9,
    )

    plt.figtext(
        -0.32,
        0.05,
        "(value is:",
        ha="left",
        fontsize=font_size * 0.9,
    )

    plt.figtext(
        0.14,
        0.05,
        "than raw data)",
        ha="left",
        fontsize=font_size * 0.9,
    )

    if title is not None:
        plt.figtext(0.05, 0.98, title + ":", ha="left", va="top", fontsize=30)

    if save_path is not None:
        plt.savefig(save_path, dpi=300, bbox_inches="tight", pad_inches=0.5)

    plt.close(fig)


def create_peaks_periods_table(counts, description=None, divide=True):
    counts, time = prepare_signal(counts)

    periods_rows = []
    row_colors = []

    cycle_periods = compute_cycle_periods(
        time,
        counts,
        min_peak_distance_hours=20,
        prominence=0.05,
    )

    periods_rows.append({
        "method": "Raw Data",
        "Peaks [CT]": cycle_periods["peak_times"].tolist(),
        "Periods [hours]": cycle_periods["peak_to_peak_periods"].tolist(),
    })

    row_colors.append("gray")

    baselines, labels, colors = compute_baselines(counts, time)

    for i in range(len(baselines)):
        baseline, label, color = baselines[i], labels[i], colors[i]

        if divide:
            transformed_signal = counts / baseline
        else:
            transformed_signal = counts - baseline

        cycle_periods = compute_cycle_periods(
            time,
            transformed_signal,
            min_peak_distance_hours=20,
            prominence=0.05,
        )

        periods_rows.append({
            "method": label,
            "Peaks [CT]": cycle_periods["peak_times"].tolist(),
            "Periods [hours]": cycle_periods["peak_to_peak_periods"].tolist(),
        })

        row_colors.append(color)

    periods_df = pd.DataFrame(periods_rows)

    periods_df["Peaks [CT]"] = periods_df["Peaks [CT]"].apply(
        lambda lst: [round(x, 2) for x in lst]
    )

    periods_df["Periods [hours]"] = periods_df["Periods [hours]"].apply(
        lambda lst: [round(x, 2) for x in lst]
    )

    periods_df = periods_df.set_index("method")

    if description is not None:
        save_path = f"{description[1:-1]}.png"
    else:
        save_path = "peaks_periods_table.png"

    create_two_stacked_tables(
        periods_df.copy(),
        row_label_colors=row_colors,
        description=description,
        save_path=save_path,
    )

    periods_expanded = pd.DataFrame(
        periods_df["Periods [hours]"].tolist(),
        index=periods_df.index,
    )
    periods_expanded["Average Period"] = periods_df["Periods [hours]"].apply(np.mean)

    ex_display = format_df(periods_expanded)

    fig, ax = plt.subplots(figsize=(12, 3))
    ax.axis("off")

    if description is not None:
        title = " Periods of the " + description.lower()[1:]
        avg_save_path = title[1:-1] + ".png"
    else:
        title = "Average Periods"
        avg_save_path = "average_periods.png"

    draw_single_table(
        ax,
        ex_display,
        "Average\nPeriod ",
        row_label_colors=row_colors,
        avg=True,
        header_font_size=20,
        description=title,
    )

    plt.savefig(avg_save_path, dpi=300, bbox_inches="tight", pad_inches=0.5)
    plt.close(fig)

    return periods_df
