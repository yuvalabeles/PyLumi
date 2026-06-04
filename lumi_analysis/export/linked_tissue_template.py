from pathlib import Path
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill, Border, Side
from openpyxl.utils import get_column_letter
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.signal import find_peaks


def create_linked_tissue_plot_template(
    output_path,
    treatments,
    tissues,
    n_mice,
    sheet_name="plot_input",
):
    # Create an Excel template for linked tissue plots.
    # Each treatment has its own time column, because experiments may have different time axes.

    output_path = Path(output_path)

    wb = Workbook()
    ws = wb.active
    ws.title = sheet_name

    experiment_row = 1
    tissue_row = 2
    mouse_row = 3
    data_start_row = 4

    header_fill = PatternFill("solid", fgColor="D9EAF7")
    time_fill = PatternFill("solid", fgColor="D9EAD3")
    spacer_fill = PatternFill("solid", fgColor="E7E6E6")

    thin_gray = Side(style="thin", color="B7B7B7")
    border = Border(left=thin_gray, right=thin_gray, top=thin_gray, bottom=thin_gray)

    col = 1

    for treatment_index, treatment in enumerate(treatments):
        treatment_start_col = col

        # Treatment-specific time column.
        ws.cell(experiment_row, col).value = treatment
        ws.cell(tissue_row, col).value = "Time"
        ws.cell(mouse_row, col).value = ""

        for row in range(1, data_start_row):
            cell = ws.cell(row, col)
            cell.fill = time_fill
            cell.font = Font(bold=True)
            cell.alignment = Alignment(horizontal="center", vertical="center")
            cell.border = border

        ws.column_dimensions[get_column_letter(col)].width = 14
        col += 1

        for mouse in range(1, n_mice + 1):
            for tissue in tissues:
                ws.cell(experiment_row, col).value = treatment
                ws.cell(tissue_row, col).value = tissue
                ws.cell(mouse_row, col).value = mouse

                for row in range(1, data_start_row):
                    cell = ws.cell(row, col)
                    cell.fill = header_fill
                    cell.font = Font(bold=True)
                    cell.alignment = Alignment(horizontal="center", vertical="center")
                    cell.border = border

                ws.column_dimensions[get_column_letter(col)].width = 14
                col += 1

        treatment_end_col = col - 1

        ws.merge_cells(
            start_row=experiment_row,
            start_column=treatment_start_col,
            end_row=experiment_row,
            end_column=treatment_end_col,
        )

        if treatment_index < len(treatments) - 1:
            for row in range(1, data_start_row):
                cell = ws.cell(row, col)
                cell.fill = spacer_fill
                cell.border = border

            ws.column_dimensions[get_column_letter(col)].width = 4
            col += 1

    ws.freeze_panes = f"A{data_start_row}"

    for row in range(1, data_start_row):
        ws.row_dimensions[row].height = 22

    output_path.parent.mkdir(parents=True, exist_ok=True)
    wb.save(output_path)

    return output_path


def read_linked_tissue_plot_template(
    input_path,
    sheet_name="plot_input",
):
    # Read a filled linked tissue plot template.
    # Each treatment block has its own Time column.

    input_path = Path(input_path)

    raw = pd.read_excel(
        input_path,
        sheet_name=sheet_name,
        header=None,
    )

    experiment_row = 0
    tissue_row = 1
    mouse_row = 2
    data_start_row = 3

    records = []

    current_experiment = None
    current_time = None

    for col in range(raw.shape[1]):
        experiment = raw.iloc[experiment_row, col]
        tissue = raw.iloc[tissue_row, col]
        mouse = raw.iloc[mouse_row, col]

        # Empty spacer column.
        if pd.isna(experiment) and pd.isna(tissue) and pd.isna(mouse):
            current_experiment = None
            current_time = None
            continue

        # Because treatment headers are merged, only the first column has the value.
        if not pd.isna(experiment):
            current_experiment = str(experiment).strip()

        if pd.isna(tissue):
            continue

        tissue = str(tissue).strip()

        # Start of a new treatment block.
        if tissue.lower() == "time":
            current_time = pd.to_numeric(
                raw.iloc[data_start_row:, col],
                errors="coerce",
            )
            continue

        if current_experiment is None or current_time is None:
            continue

        if pd.isna(mouse):
            continue

        mouse = str(mouse).strip()

        values = pd.to_numeric(
            raw.iloc[data_start_row:, col],
            errors="coerce",
        )

        sample_df = pd.DataFrame({
            "time": current_time,
            "experiment": current_experiment,
            "tissue": tissue,
            "mouse": mouse,
            "mean": values,
        })

        sample_df = sample_df.dropna(subset=["time", "mean"])
        records.append(sample_df)

    if not records:
        raise ValueError("No valid data columns were found in the template.")

    return pd.concat(records, ignore_index=True)


def compute_linked_tissue_peaks(
    data,
    min_peak_distance_hours=20,
    prominence=None,
    peak_number=1,
):
    # Compute peak time for each experiment/tissue/mouse mean signal.

    peak_records = []

    grouped = data.groupby(["experiment", "tissue", "mouse"], sort=False)

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

        if len(peak_indices) < peak_number:
            peak_time = np.nan
            peak_value = np.nan
        else:
            selected_peak_index = int(peak_indices[peak_number - 1])
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


def plot_linked_tissue_traces(
    data,
    output_path,
    title="Mean traces by tissue",
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

        # Tissue title on the left side, bold, with colon.
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
        fontsize=15
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
    ax.set_title(title)
    ax.grid(True, axis="x", alpha=0.3)

    ax.legend(frameon=False)

    fig.tight_layout()

    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)

    return output_path


if __name__ == "__main__":
    # create_linked_tissue_plot_template(
    #     output_path="linked_tissue_plot_template.xlsx",
    #     treatments=["control F", "control M", "6% O2", "10% CO2"],
    #     tissues=["Liver", "Lung", "Kidney"],
    #     n_mice=2,
    # )

    data_tissue = read_linked_tissue_plot_template(
        input_path="linked_tissue_plot_template.xlsx",
    )

    plot_linked_tissue_traces(
        data=data_tissue,
        output_path="plots/linked_tissue_traces.png",
        title="Mean traces by tissue",
        tissue_order=["Kidney", "Lung", "Liver"],
        y_upper_limits=[200, 850, 400],
    )

    peaks_data = compute_linked_tissue_peaks(
        data=data_tissue,
        min_peak_distance_hours=20,
        prominence=None,
        peak_number=1,
    )

    plot_linked_tissue_peak_times(
        peaks_df=peaks_data,
        output_path="plots/linked_tissue_peak_times.png",
        tissue_order=["Kidney", "Lung", "Liver"],
    )
