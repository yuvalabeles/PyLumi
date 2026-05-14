from pathlib import Path

from lumi_analysis.core.tissue_analysis import analyse_tissue
from lumi_analysis.core.cell_population_analysis import analyse_cell_population

from lumi_analysis.core.dataframes import (
    create_complete_df,
    create_condensed_df,
)


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
    tissue_labels=None,
    save_file=True,
    suffix="_Raw.csv",
    folder_name=None,
):
    full_dfs = []

    if experiment_type not in ["tissue", "cell_population"]:
        raise ValueError("experiment_type must be either 'tissue' or 'cell_population'")

    if not isinstance(groups, dict):
        raise TypeError("groups must be a dictionary: dict[str, list[str]]")

    if experiment_type == "tissue":
        if tissue_labels is None:
            tissue_labels = list(groups.keys())

        for sample_name, file_names in groups.items():
            print(f"[*] Analysing tissue: {sample_name}, from: {file_names}")

            paths = build_file_paths(
                input_folder=input_folder,
                file_names=file_names,
                suffix=suffix,
            )

            full_df = analyse_tissue(
                paths,
                file_names,
                save_file=save_file,
                sample=sample_name,
                folder_name=folder_name,
            )

            full_dfs.append(full_df)

        complete_df = create_complete_df(
            full_dfs,
            save_file=False,
            folder_name=folder_name,
        )

        condensed_df = create_condensed_df(
            complete_df,
            tissue_labels,
            save_file=save_file,
            folder_name=folder_name,
        )

        return {
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

            full_df = analyse_cell_population(
                paths,
                sample_name=sample_name,
                save_file=save_file,
            )

            full_dfs.append(full_df)

        return {
            "full_dfs": full_dfs,
        }
