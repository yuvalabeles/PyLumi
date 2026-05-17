import numpy as np


def format_lumi_raw_axis(
    ax,
    time,
    xlabel="CT [hours]",
    ylabel="counts / second",
    x_major_tick_hours=24,
    x_minor_tick_hours=12,
    x_axis_start=0,
):
    ax.set_xlabel(xlabel, labelpad=10, fontsize=12)
    ax.set_ylabel(ylabel, labelpad=15, fontsize=12)

    ax.set_xlim(left=x_axis_start)

    max_time = float(np.nanmax(time))
    major_ticks = np.arange(x_axis_start, max_time + x_major_tick_hours, x_major_tick_hours)
    minor_ticks = np.arange(x_axis_start, max_time + x_minor_tick_hours, x_minor_tick_hours)

    ax.set_xticks(major_ticks)
    ax.set_xticks(minor_ticks, minor=True)

    ax.grid(axis="x", which="major", linestyle="-", linewidth=0.8, alpha=0.8)
    ax.grid(axis="x", which="minor", linestyle="-", linewidth=0.8, alpha=0.4)
    ax.grid(axis="y", linewidth=0.6, alpha=0.3)

    ax.tick_params(axis="both", labelsize=9)


def add_figure_border(fig, linewidth=1):
    fig.patch.set_edgecolor("black")
    fig.patch.set_linewidth(linewidth)
