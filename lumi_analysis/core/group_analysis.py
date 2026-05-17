from lumi_analysis.core.loading import load_files
from lumi_analysis.core.validation import assert_interval_overlaps
from lumi_analysis.core.preprocessing import preprocess_replicates, crop_replicates_tail
from lumi_analysis.core.dataframes import create_sub_df

from lumi_analysis.export.excel_export import save_group_data


def analyse_group(
    path_lst,
    filenames=None,
    noise_max=25,
    remove_noise=True,
    save_file=True,
    group_name=None,
    output_folder=None,
    return_intermediate=False,
    max_rows=None,
    max_hours=None,
    max_days=None,
    interval_minutes=10,
):
    raw_dfs = load_files(path_lst)

    if filenames is None:
        filenames = [
            f"file_{i + 1}"
            for i in range(len(raw_dfs))
        ]

    keep_all_rows = group_name == "Extra"

    processed_dfs = preprocess_replicates(
        dfs=raw_dfs,
        filenames=filenames,
        noise_max=noise_max,
        remove_noise=remove_noise,
        keep_all_rows=keep_all_rows,
    )

    aligned_dfs = assert_interval_overlaps(processed_dfs)

    aligned_dfs = crop_replicates_tail(
        dfs=aligned_dfs,
        max_rows=max_rows,
        max_hours=max_hours,
        max_days=max_days,
        interval_minutes=interval_minutes,
    )

    for df in aligned_dfs:
        if " Baseline" in df.columns:
            df.drop(" Baseline", axis=1, inplace=True)

    full_df = create_sub_df(
        aligned_dfs,
        filenames,
        sample=group_name,
    )

    if save_file:
        filename = group_name if group_name is not None else "_".join(filenames)

        save_group_data(
            full_df,
            filename,
            excel=False,
            output_folder=output_folder,
        )

    if return_intermediate:
        return {
            "group": group_name,
            "filenames": filenames,
            "raw_dfs": raw_dfs,
            "processed_dfs": processed_dfs,
            "aligned_dfs": aligned_dfs,
            "full_df": full_df,
        }

    return full_df
