from pathlib import Path

from lumi_analysis.core.tissue_analysis import analyse_tissue
from lumi_analysis.core.cell_population_analysis import analyse_cell_population

from lumi_analysis.core.dataframes import (
    create_complete_df,
    create_condensed_df,
)

from lumi_analysis.export.excel_export import save_group_data


def build_file_paths(input_folder, file_names, suffix="_Raw.csv"):
    input_folder = Path(input_folder)

    return [
        input_folder / f"{file_name}{suffix}"
        for file_name in file_names
    ]


def run_analysis(
    input_folder,
    groups,
    experiment_type="tissue",
    group_labels=None,
    save_file=True,
    suffix="_Raw.csv",
    output_folder=None,
    noise_max=25,
    remove_noise=True,
):
    full_dfs = []
    sample_results = {}

    if experiment_type not in ["tissue", "cell_population"]:
        raise ValueError("experiment_type must be either 'tissue' or 'cell_population'")

    if not isinstance(groups, dict):
        raise TypeError("groups must be a dictionary: dict[str, list[str]]")

    if experiment_type == "tissue":
        if group_labels is None:
            group_labels = list(groups.keys())

        for sample_name, file_names in groups.items():
            print(f"[*] Analysing tissue: {sample_name}, from: {file_names}")

            paths = build_file_paths(
                input_folder=input_folder,
                file_names=file_names,
                suffix=suffix,
            )

            sample_result = analyse_tissue(
                paths,
                file_names,
                noise_max=noise_max,
                remove_noise=remove_noise,
                save_file=save_file,
                sample=sample_name,
                output_folder=output_folder,
                return_intermediate=True,
            )

            full_dfs.append(sample_result["full_df"])
            sample_results[sample_name] = sample_result

        complete_df = create_complete_df(full_dfs)
        condensed_df = create_condensed_df(complete_df)

        if save_file:
            save_group_data(
                condensed_df,
                "Data - complete",
                group_labels=group_labels,
                output_folder=output_folder,
            )

        return {
            "sample_results": sample_results,
            "full_dfs": full_dfs,
            "complete_df": complete_df,
            "condensed_df": condensed_df,
        }

    if experiment_type == "cell_population":
        for sample_name, file_names in groups.items():
            print(f"[*] Analysing cell population: {sample_name}, from: {file_names}")

            paths = build_file_paths(
                input_folder=input_folder,
                file_names=file_names,
                suffix=suffix,
            )

            sample_result = analyse_cell_population(
                paths,
                filenames=file_names,
                noise_max=noise_max,
                sample_name=sample_name,
                save_file=save_file,
                output_folder=output_folder,
                return_intermediate=True,
            )

            full_dfs.append(sample_result["full_df"])
            sample_results[sample_name] = sample_result

        return {
            "sample_results": sample_results,
            "full_dfs": full_dfs,
        }
