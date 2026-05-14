from lumi_analysis.core.loading import load_files
from lumi_analysis.core.validation import assert_interval_overlaps
from lumi_analysis.core.preprocessing import preprocess_replicates
from lumi_analysis.core.dataframes import create_sub_df

from lumi_analysis.export.excel_export import save_group_data


def analyse_cell_population(
    path_lst,
    filenames=None,
    noise_max=20,
    save_file=True,
    sample_name=None,
    output_folder=None,
    return_intermediate=False,
):
    raw_dfs = load_files(path_lst)

    if filenames is None:
        filenames = [
            f"file_{i + 1}"
            for i in range(len(raw_dfs))
        ]

    processed_dfs = preprocess_replicates(
        dfs=raw_dfs,
        filenames=filenames,
        noise_max=noise_max,
        remove_noise=True,
        keep_all_rows=False,
    )

    aligned_dfs = assert_interval_overlaps(processed_dfs)

    full_df = create_sub_df(
        aligned_dfs,
        filenames,
        sample=sample_name,
    )

    if save_file:
        filename = sample_name if sample_name is not None else "_".join(filenames)

        save_group_data(
            full_df,
            filename,
            excel=False,
            output_folder=output_folder,
        )

    if return_intermediate:
        return {
            "sample": sample_name,
            "filenames": filenames,
            "raw_dfs": raw_dfs,
            "processed_dfs": processed_dfs,
            "aligned_dfs": aligned_dfs,
            "full_df": full_df,
        }

    return full_df
