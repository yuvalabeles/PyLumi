from pathlib import Path
import argparse

from lumi_analysis.tissue_analysis import (
    create_tissue_settings_template,
    read_tissue_settings,
    create_linked_tissue_plot_template,
    read_linked_tissue_plot_template,
    compute_linked_tissue_peaks,
    plot_linked_tissue_traces,
    plot_linked_tissue_peak_times,
)


SETTINGS_FILE = Path("tissue_settings.xlsx")
AVERAGE_TEMPLATE_FILE = Path("average_tissue_template.xlsx")


def create_settings():
    create_tissue_settings_template(
        output_path=SETTINGS_FILE,
    )

    print(f"Created settings file: {SETTINGS_FILE}")


def create_template():
    mice, tissues, treatments, _, _, _ = read_tissue_settings(
        input_path=SETTINGS_FILE,
    )

    create_linked_tissue_plot_template(
        output_path=AVERAGE_TEMPLATE_FILE,
        treatments=treatments,
        tissues=tissues,
        mice=mice,
    )

    print(f"Created average template: {AVERAGE_TEMPLATE_FILE}")


def run_analysis():
    _, tissues, _, y_upper_limits, output_path, first_peak_after_by_treatment = read_tissue_settings(
        input_path=SETTINGS_FILE,
    )

    data_tissue = read_linked_tissue_plot_template(
        input_path=AVERAGE_TEMPLATE_FILE,
    )

    output_path = Path(output_path)
    output_path.mkdir(parents=True, exist_ok=True)

    traces_path = output_path / "linked_tissue_traces.png"
    peaks_path = output_path / "linked_tissue_peak_times.png"

    plot_linked_tissue_traces(
        data=data_tissue,
        output_path=traces_path,
        tissue_order=tissues,
        y_upper_limits=y_upper_limits,
    )

    peaks_data = compute_linked_tissue_peaks(
        data=data_tissue,
        min_peak_distance_hours=20,
        prominence=None,
        first_peak_after_by_treatment=first_peak_after_by_treatment,
    )

    plot_linked_tissue_peak_times(
        peaks_df=peaks_data,
        output_path=peaks_path,
        tissue_order=tissues,
    )

    print(f"Created plot: {traces_path}")
    print(f"Created plot: {peaks_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Create and run linked tissue analysis.",
    )

    parser.add_argument(
        "action",
        choices=["settings", "create", "run"],
        help="Action to perform: settings, create, or run.",
    )

    args = parser.parse_args()

    if args.action == "settings":
        create_settings()

    elif args.action == "create":
        create_template()

    elif args.action == "run":
        run_analysis()


if __name__ == "__main__":
    main()
