from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt

from lumi_analysis.plotting.style import format_lumi_raw_axis, add_figure_border


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
        ax.plot(
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
        ax.plot(
            time,
            y,
            color=color,
            linewidth=linewidth,
            alpha=alpha,
            label=label,
            zorder=zorder,
        )

    elif plot_style == "points+line":
        ax.plot(
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


def plot_raw_replicates(
    df,
    mean_replicate_cols=None,
    visible_replicate_cols=None,
    mean_col=LUMI_AVERAGE_COLUMN,
    recompute_mean=True,
    time_col=None,
    start_ct=0,
    interval_minutes=10,
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
):
    """
    Plot raw Lumi data from a pipeline full_df.

    Expected dataframe structure:
    Date | Time (hr:min) | Time (days) | replicate columns... | counts/sec (avg)

    mean_replicate_cols:
        Replicates included in average calculation.

    visible_replicate_cols:
        Replicates shown on the plot.

    This allows separating:
    1. disabling a replicate from the average
    2. only hiding a replicate visually
    """

    all_replicate_cols = get_lumi_replicate_columns(df, mean_col=mean_col)

    if mean_replicate_cols is None:
        mean_replicate_cols = all_replicate_cols

    if visible_replicate_cols is None:
        visible_replicate_cols = all_replicate_cols

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

    if missing_mean_cols:
        raise ValueError(f"Mean replicate columns not found: {missing_mean_cols}")

    if missing_visible_cols:
        raise ValueError(f"Visible replicate columns not found: {missing_visible_cols}")

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

        plot_signal(
            ax=ax,
            time=time,
            y=y,
            label=str(col),
            plot_style=plot_style,
            markersize=replicate_markersize,
            linewidth=replicate_linewidth,
            alpha=replicate_alpha,
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

    # -------------------------------------------------------------------------
    # Plot average
    # -------------------------------------------------------------------------
    plot_signal(
        ax=ax,
        time=time,
        y=average_signal.to_numpy(dtype=float),
        label=average_label,
        plot_style=plot_style,
        color=average_color,
        markersize=average_markersize,
        linewidth=average_linewidth,
        alpha=average_alpha,
        zorder=5,
    )

    # -------------------------------------------------------------------------
    # Figure styling
    # -------------------------------------------------------------------------
    if title is not None:
        ax.set_title(str(title).title(), pad=20, fontsize=18, fontweight="bold")

    format_lumi_raw_axis(ax, time)

    if y_limit is not None:
        if isinstance(y_limit, tuple):
            ax.set_ylim(y_limit)
        else:
            ax.set_ylim(0, y_limit)

    legend_items_count = len(visible_replicate_cols) + 1

    ax.legend(
        loc="upper center",
        bbox_to_anchor=(0.5, -0.18),
        ncol=min(legend_items_count, 6),
        frameon=True,
        fontsize=12,
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

    fig.tight_layout()

    # -------------------------------------------------------------------------
    # Save figure
    # -------------------------------------------------------------------------
    if save_path is not None:
        save_path = Path(save_path)
        save_path.parent.mkdir(parents=True, exist_ok=True)

        fig.savefig(
            save_path,
            dpi=300,
            bbox_inches="tight",
            facecolor="white",
        )

    # -------------------------------------------------------------------------
    # Show / close
    # -------------------------------------------------------------------------
    if show:
        plt.show()

    if close:
        plt.close(fig)

    return fig, ax
