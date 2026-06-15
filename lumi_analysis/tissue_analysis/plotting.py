from pathlib import Path

import matplotlib.pyplot as plt


def plot_linked_tissue_traces(
    data,
    output_path,
    title="Mean signal by tissue",
    tissue_order=None,
    y_upper_limits=None,
    figsize=None,
):
    # Plot mean traces as stacked tissue panels.
    # Color represents experiment.
    # Each mouse is drawn as a separate line, but legend shows only treatments.

    output_path = Path(output_path)

    if tissue_order is None:
        tissue_order = list(data["tissue"].drop_duplicates())

    experiments = list(data["experiment"].drop_duplicates())

    if y_upper_limits is not None and len(y_upper_limits) != len(tissue_order):
        raise ValueError(
            "y_upper_limits must have the same length as tissue_order."
        )

    if figsize is None:
        figsize = (8, 3.2 * len(tissue_order))

    fig, axes = plt.subplots(
        len(tissue_order),
        1,
        figsize=figsize,
        sharex=False,
        sharey=False,
    )

    if len(tissue_order) == 1:
        axes = [axes]

    color_map = {
        experiment: f"C{i}"
        for i, experiment in enumerate(experiments)
    }

    used_labels = set()

    for tissue_index, (ax, tissue) in enumerate(zip(axes, tissue_order)):
        tissue_df = data[data["tissue"] == tissue]

        for (experiment, mouse), group_df in tissue_df.groupby(
            ["experiment", "mouse"],
            sort=False,
        ):
            group_df = group_df.sort_values("time")

            label = experiment if experiment not in used_labels else None
            used_labels.add(experiment)

            ax.plot(
                group_df["time"],
                group_df["mean"],
                color=color_map[experiment],
                linewidth=1.8,
                label=label,
            )

        ax.text(
            -0.17,
            0.5,
            f"{tissue}:",
            transform=ax.transAxes,
            fontsize=12,
            fontweight="bold",
            ha="right",
            va="center",
        )

        ax.set_xlabel("Time")
        ax.set_ylabel("Mean signal")

        if y_upper_limits is not None:
            ax.set_ylim(0, y_upper_limits[tissue_index])

        ax.grid(True, alpha=0.3)

    handles, labels = axes[0].get_legend_handles_labels()

    fig.suptitle(
        title.title(),
        y=0.98,
        x=0.585,
        fontsize=15,
    )

    fig.legend(
        handles,
        labels,
        loc="upper center",
        bbox_to_anchor=(0.585, 0.94),
        ncol=min(4, len(experiments)),
        frameon=True,
        edgecolor="lightgray",
    )

    fig.tight_layout(rect=(0.12, 0, 1, 0.90))

    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)

    return output_path


def plot_linked_tissue_peak_times(
    peaks_df,
    output_path,
    tissue_order=None,
    title="Peak time by tissue",
    figsize=None,
):
    # Plot peak times across tissues.
    # X axis = peak time.
    # Y axis = tissue.
    # Color represents experiment.
    # Each mouse is drawn as a separate line, but legend shows only treatments.

    output_path = Path(output_path)

    peaks_df = peaks_df.copy()

    if tissue_order is None:
        tissue_order = list(peaks_df["tissue"].drop_duplicates())

    experiments = list(peaks_df["experiment"].drop_duplicates())

    if figsize is None:
        figsize = (6, 5)

    tissue_to_y = {
        tissue: index
        for index, tissue in enumerate(tissue_order)
    }

    peaks_df["y"] = peaks_df["tissue"].map(tissue_to_y)

    color_map = {
        experiment: f"C{i}"
        for i, experiment in enumerate(experiments)
    }

    fig, ax = plt.subplots(figsize=figsize)

    used_labels = set()

    for (experiment, mouse), group_df in peaks_df.groupby(
        ["experiment", "mouse"],
        sort=False,
    ):
        group_df = group_df.dropna(subset=["peak_time", "y"])
        group_df = group_df.sort_values("y")

        label = experiment if experiment not in used_labels else None
        used_labels.add(experiment)

        ax.plot(
            group_df["peak_time"],
            group_df["y"],
            color=color_map[experiment],
            marker="o",
            linewidth=1.8,
            markersize=6,
            label=label,
        )

    ax.set_yticks(range(len(tissue_order)))
    ax.set_yticklabels(tissue_order)

    ax.set_xlabel("Peak time")
    ax.set_ylabel("Tissue")
    ax.set_title(title.title())
    ax.grid(True, axis="x", alpha=0.3)

    ax.legend(frameon=False)

    fig.tight_layout()

    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)

    return output_path
