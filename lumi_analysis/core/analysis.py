from pathlib import Path

from lumi_analysis.core.group_analysis import analyse_group

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
    group_labels=None,
    save_file=True,
    suffix="_Raw.csv",
    output_folder=None,
    noise_max=25,
    remove_noise=True,
    max_rows=None,
    max_hours=None,
    max_days=None,
    interval_minutes=10,
    ct_start_hour=0,
):
    full_dfs = []
    group_results = {}

    if not isinstance(groups, dict):
        raise TypeError("groups must be a dictionary: dict[str, list[str]]")

    if group_labels is None:
        group_labels = list(groups.keys())

    for group_name, file_names in groups.items():
        print(f"[*] Analysing group: {group_name}, from: {file_names}")

        paths = build_file_paths(
            input_folder=input_folder,
            file_names=file_names,
            suffix=suffix,
        )

        group_result = analyse_group(
            paths,
            filenames=file_names,
            noise_max=noise_max,
            remove_noise=remove_noise,
            save_file=save_file,
            group_name=group_name,
            output_folder=output_folder,
            return_intermediate=True,
            max_rows=max_rows,
            max_hours=max_hours,
            max_days=max_days,
            interval_minutes=interval_minutes,
        )

        full_dfs.append(group_result["full_df"])
        group_results[group_name] = group_result

    complete_df = create_complete_df(full_dfs)

    condensed_df = create_condensed_df(
        complete_df,
        interval_minutes=interval_minutes,
        ct_start_hour=ct_start_hour,
    )

    if save_file:
        save_group_data(
            condensed_df,
            "Data - complete",
            group_labels=group_labels,
            output_folder=output_folder,
        )

    return {
        "group_results": group_results,
        "full_dfs": full_dfs,
        "complete_df": complete_df,
        "condensed_df": condensed_df,
    }
