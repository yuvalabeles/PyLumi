from pathlib import Path

import pandas as pd

from lumi_analysis.core.group_analysis import analyse_group

from lumi_analysis.core.dataframes import (
    create_complete_df,
    create_condensed_df,
)

from lumi_analysis.export.excel_export import save_group_data


LUMI_METADATA_COLUMNS = [
    "Date",
    "Time (hr:min)",
    "Time (days)",
]

LUMI_AVERAGE_COLUMN = "counts/sec (avg)"


def build_file_paths(input_folder, file_names, suffix="_Raw.csv"):
    input_folder = Path(input_folder)

    return [
        input_folder / f"{file_name}{suffix}"
        for file_name in file_names
    ]


def get_replicate_columns(df):
    return [
        col for col in df.columns
        if col not in LUMI_METADATA_COLUMNS
        and col != LUMI_AVERAGE_COLUMN
    ]


def create_group_df_without_disabled_replicates(group_df, disabled_replicates):
    if not disabled_replicates:
        return group_df.copy()

    filtered_df = group_df.copy()

    replicate_cols = get_replicate_columns(filtered_df)

    disabled_cols = [
        col for col in replicate_cols
        if col in disabled_replicates
    ]

    active_cols = [
        col for col in replicate_cols
        if col not in disabled_cols
    ]

    if len(active_cols) == 0:
        raise ValueError(
            "All replicates were disabled in one group. "
            "At least one active replicate must remain."
        )

    for col in disabled_cols:
        filtered_df[col] = pd.NA

    filtered_df[LUMI_AVERAGE_COLUMN] = filtered_df[active_cols].mean(axis=1)

    return filtered_df


def create_analysis_result_without_disabled_replicates(
    analysis_result,
    disabled_replicates,
    interval_minutes=10,
    ct_start_hour=0,
):
    filtered_full_dfs = []
    filtered_group_results = {}

    for group_name, group_result in analysis_result["group_results"].items():
        filtered_group_result = group_result.copy()

        filtered_full_df = create_group_df_without_disabled_replicates(
            group_df=group_result["full_df"],
            disabled_replicates=disabled_replicates,
        )

        filtered_group_result["full_df"] = filtered_full_df

        filtered_full_dfs.append(filtered_full_df)
        filtered_group_results[group_name] = filtered_group_result

    filtered_complete_df = create_complete_df(filtered_full_dfs)

    filtered_condensed_df = create_condensed_df(
        filtered_complete_df,
        interval_minutes=interval_minutes,
        ct_start_hour=ct_start_hour,
    )

    return {
        "group_results": filtered_group_results,
        "full_dfs": filtered_full_dfs,
        "complete_df": filtered_complete_df,
        "condensed_df": filtered_condensed_df,
    }


def run_analysis(
    input_folder,
    groups,
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
    replicates_per_group=None,
    disabled_replicates=None,
):
    full_dfs = []
    group_results = {}

    if disabled_replicates is None:
        disabled_replicates = []

    if not isinstance(groups, dict):
        raise TypeError("groups must be a dictionary: dict[str, list[str]]")

    group_labels = list(groups.keys())

    for group_name, file_names in groups.items():
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

    analysis_result = {
        "group_results": group_results,
        "full_dfs": full_dfs,
        "complete_df": complete_df,
        "condensed_df": condensed_df,
    }

    if save_file:
        save_group_data(
            condensed_df,
            "Data - complete",
            group_labels=group_labels,
            replicates_per_group=replicates_per_group,
            output_folder=output_folder,
        )

    filtered_analysis_result = None

    if disabled_replicates:
        filtered_analysis_result = create_analysis_result_without_disabled_replicates(
            analysis_result=analysis_result,
            disabled_replicates=disabled_replicates,
            interval_minutes=interval_minutes,
            ct_start_hour=ct_start_hour,
        )

        if save_file:
            save_group_data(
                filtered_analysis_result["condensed_df"],
                "Data - without disabled replicates",
                group_labels=group_labels,
                replicates_per_group=replicates_per_group,
                output_folder=output_folder,
            )

    analysis_result["without_disabled_replicates"] = filtered_analysis_result

    return analysis_result
