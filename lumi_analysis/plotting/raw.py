from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt

from lumi_analysis.plotting.style import format_lumi_raw_axis, add_figure_border
from lumi_analysis.plotting.peaks import plot_peaks_for_signal


LUMI_METADATA_COLUMNS = [
    "Date",
    "Time (hr:min)",
    "Time (days)",
]

LUMI_AVERAGE_COLUMN = "counts/sec (avg)"


def create_ct_axis(n_points, start_ct=0, interval_minutes=10):
    # Create CT axis in hours.
    return start_ct + np.arange(n_points) * (interval_minutes / 60)


def get_lumi_replicate_columns(df, mean_col=LUMI_AVERAGE_COLUMN):
    # Replicate columns are all columns that are not metadata and not the average column.
    return [
        col for col in df.columns
        if col not in LUMI_METADATA_COLUMNS
        and col != mean_col
    ]


def get_lumi_time_axis(
    df,
    time_col=None,
    start_ct=0,
    interval_minutes=10,
):
    # Prefer explicit time_col if given, otherwise create CT axis from row number.
    if time_col is not None:
        if time_col not in df.columns:
            raise ValueError(f"time_col not found in dataframe: {time_col}")

        return df[time_col].to_numpy(dtype=float)

    return create_ct_axis(
        n_points=len(df),
        start_ct=start_ct,
        interval_minutes=interval_minutes,
    )


def validate_plot_style(plot_style):
    valid_styles = ["points", "line", "points+line"]

    if plot_style not in valid_styles:
        raise ValueError(
            f"plot_style must be one of: {valid_styles}"
        )


def plot_signal(
    ax,
    time,
    y,
    label,
    plot_style,
    color=None,
    markersize=2,
    linewidth=1.2,
    alpha=0.75,
    zorder=None,
):
    validate_plot_style(plot_style)

    if plot_style == "points":
        line, = ax.plot(
            time,
            y,
            ".",
            color=color,
            markersize=markersize,
            alpha=alpha,
            label=label,
            zorder=zorder,
        )

    elif plot_style == "line":
        line, = ax.plot(
            time,
            y,
            color=color,
            linewidth=linewidth,
            alpha=alpha,
            label=label,
            zorder=zorder,
        )

    elif plot_style == "points+line":
        line, = ax.plot(
            time,
            y,
            color=color,
            marker=".",
            markersize=markersize,
            linewidth=linewidth,
            alpha=alpha,
            label=label,
            zorder=zorder,
        )
    else:
        line = None

    return line


def plot_raw_replicates(
    df,
    mean_replicate_cols=None,
    visible_replicate_cols=None,
    replicate_display_mode="replicates_and_mean",
    mean_col=LUMI_AVERAGE_COLUMN,
    recompute_mean=True,
    time_col=None,
    start_ct=0,
    interval_minutes=10,
    x_axis_start=0,
    title=None,
    description=None,
    y_limit=None,
    save_path=None,
    show=False,
    close=True,
    figsize=(9, 5),
    plot_style="points",
    replicate_markersize=2,
    replicate_linewidth=1.2,
    replicate_alpha=0.75,
    average_markersize=3,
    average_linewidth=2.2,
    average_color="black",
    average_alpha=0.85,
    plot_peaks=False,
    peaks_to_show=None,
    peaks_to_show_txt=None,
    show_average_peaks=True,
    show_average_peaks_txt=True,
    min_peak_distance_hours=20,
    peak_prominence=None,
    peak_marker="x",
    peak_markersize=7,
    peak_markeredgewidth=1.5,
    peak_txt_dx=2,
    peak_txt_dy=0,
    peak_txt_fontsize=8,
):
    """
    Plot raw Lumi data from a pipeline full_df.

    replicate_display_mode:
        "replicates_and_mean" = show visible replicates and the average.
        "mean_only" = show only the average.
        "replicates_only" = show only visible replicates, without the average.
    """

    allowed_modes = [
        "replicates_and_mean",
        "mean_only",
        "replicates_only",
    ]

    if replicate_display_mode not in allowed_modes:
        raise ValueError(
            f"Invalid replicate_display_mode: {replicate_display_mode}. "
            f"Allowed values: {allowed_modes}"
        )

    all_replicate_cols = get_lumi_replicate_columns(df, mean_col=mean_col)

    disabled_replicate_cols = mean_replicate_cols or []

    if mean_replicate_cols is None:
        mean_replicate_cols = all_replicate_cols
    else:
        mean_replicate_cols = [
            col for col in all_replicate_cols
            if col not in disabled_replicate_cols
        ]

    hidden_replicate_cols = visible_replicate_cols or []

    visible_replicate_cols = [
        col for col in all_replicate_cols
        if col not in hidden_replicate_cols and col not in disabled_replicate_cols
    ]

    if replicate_display_mode == "mean_only":
        visible_replicate_cols = []

    if plot_peaks:
        if peaks_to_show is None:
            peaks_to_show = visible_replicate_cols
    else:
        peaks_to_show = []

    if peaks_to_show_txt is None:
        peaks_to_show_txt = []

    if len(mean_replicate_cols) == 0:
        raise ValueError("mean_replicate_cols must include at least one replicate.")

    missing_mean_cols = [
        col for col in mean_replicate_cols
        if col not in df.columns
    ]

    missing_visible_cols = [
        col for col in visible_replicate_cols
        if col not in df.columns
    ]

    missing_peak_cols = [
        col for col in peaks_to_show
        if col not in df.columns
    ]

    missing_peak_txt_cols = [
        col for col in peaks_to_show_txt
        if col not in df.columns
    ]

    if missing_mean_cols:
        raise ValueError(f"Mean replicate columns not found: {missing_mean_cols}")

    if missing_visible_cols:
        raise ValueError(f"Visible replicate columns not found: {missing_visible_cols}")

    if missing_peak_cols:
        raise ValueError(f"Peak columns not found: {missing_peak_cols}")

    if missing_peak_txt_cols:
        raise ValueError(f"Peak text columns not found: {missing_peak_txt_cols}")

    time = get_lumi_time_axis(
        df=df,
        time_col=time_col,
        start_ct=start_ct,
        interval_minutes=interval_minutes,
    )

    if len(time) != len(df):
        raise ValueError("Time axis length must match dataframe length.")

    fig, ax = plt.subplots(figsize=figsize)

    # -------------------------------------------------------------------------
    # Plot replicates
    # -------------------------------------------------------------------------
    for col in visible_replicate_cols:
        y = df[col].to_numpy(dtype=float)

        line = plot_signal(
            ax=ax,
            time=time,
            y=y,
            label=str(col),
            plot_style=plot_style,
            markersize=replicate_markersize,
            linewidth=replicate_linewidth,
            alpha=replicate_alpha,
        )

        if plot_peaks and col in peaks_to_show:
            color = line.get_color()

            plot_peaks_for_signal(
                ax=ax,
                time=time,
                signal=y,
                color=color,
                show_text=col in peaks_to_show_txt,
                min_peak_distance_hours=min_peak_distance_hours,
                prominence=peak_prominence,
                marker=peak_marker,
                markersize=peak_markersize,
                markeredgewidth=peak_markeredgewidth,
                text_dx=peak_txt_dx,
                text_dy=peak_txt_dy,
                text_fontsize=peak_txt_fontsize,
            )

    # -------------------------------------------------------------------------
    # Compute average
    # -------------------------------------------------------------------------
    if recompute_mean:
        average_signal = df[mean_replicate_cols].mean(axis=1)
        average_label = "average"
    else:
        if mean_col not in df.columns:
            raise ValueError(f"mean_col not found in dataframe: {mean_col}")

        average_signal = df[mean_col]
        average_label = mean_col

    average_y = average_signal.to_numpy(dtype=float)

    # -------------------------------------------------------------------------
    # Plot average
    # -------------------------------------------------------------------------
    if replicate_display_mode != "replicates_only":
        average_line = plot_signal(
            ax=ax,
            time=time,
            y=average_y,
            label=average_label,
            plot_style=plot_style,
            color=average_color,
            markersize=average_markersize,
            linewidth=average_linewidth,
            alpha=average_alpha,
            zorder=5,
        )

        if plot_peaks and show_average_peaks:
            average_peak_color = average_line.get_color()

            plot_peaks_for_signal(
                ax=ax,
                time=time,
                signal=average_y,
                color=average_peak_color,
                show_text=show_average_peaks_txt,
                min_peak_distance_hours=min_peak_distance_hours,
                prominence=peak_prominence,
                marker=peak_marker,
                markersize=peak_markersize,
                markeredgewidth=peak_markeredgewidth,
                text_dx=peak_txt_dx,
                text_dy=peak_txt_dy,
                text_fontsize=peak_txt_fontsize,
                zorder=7,
            )

    # -------------------------------------------------------------------------
    # Figure styling
    # -------------------------------------------------------------------------
    if title is not None:
        ax.set_title(str(title).title(), pad=20, fontsize=18, fontweight="bold")

    format_lumi_raw_axis(
        ax,
        time,
        x_axis_start=x_axis_start,
    )

    if y_limit is not None:
        if isinstance(y_limit, tuple):
            ax.set_ylim(y_limit)
        else:
            ax.set_ylim(0, y_limit)

    legend_items_count = len(visible_replicate_cols)

    if replicate_display_mode != "replicates_only":
        legend_items_count += 1

    if legend_items_count > 0:
        ax.legend(
            loc="upper center",
            bbox_to_anchor=(0.5, -0.18),
            ncol=min(legend_items_count, 6),
            frameon=False,
            fontsize=13,
            markerscale=5,
        )

    add_figure_border(fig)

    if description is not None:
        fig.text(
            0.99,
            0.99,
            description,
            ha="right",
            va="top",
            fontsize=10,
        )

    if len(disabled_replicate_cols) > 0:
        disabled_text = "* Replicates excluded from the data: " + ", ".join(disabled_replicate_cols)

        fig.text(
            0.01,
            0.01,
            disabled_text,
            ha="left",
            va="bottom",
            fontsize=8,
            alpha=0.8,
            fontstyle="italic",
        )

    fig.tight_layout()

    if save_path is not None:
        save_path = Path(save_path)
        save_path.parent.mkdir(parents=True, exist_ok=True)

        fig.savefig(
            save_path,
            dpi=300,
            bbox_inches="tight",
            facecolor="white",
        )

    if show:
        plt.show()

    if close:
        plt.close(fig)

    return fig, ax
