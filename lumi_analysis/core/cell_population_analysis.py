from lumi_analysis.core.loading import load_files
from lumi_analysis.core.validation import assert_interval_overlaps
from lumi_analysis.core.preprocessing import preprocess_replicates

from lumi_analysis.core.dataframes import (
    create_cell_population_avg_df,
)

from lumi_analysis.export.excel_export import (
    ensure_output_folder,
)


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

    avg_df = create_cell_population_avg_df(aligned_dfs)

    if save_file:
        folder_path = ensure_output_folder(output_folder)

        filename = "avg_df.csv"

        if sample_name is not None:
            filename = sample_name + filename

        file_path = folder_path / filename

        avg_df.to_csv(file_path, index=False)

    if return_intermediate:
        return {
            "sample": sample_name,
            "filenames": filenames,
            "raw_dfs": raw_dfs,
            "processed_dfs": processed_dfs,
            "aligned_dfs": aligned_dfs,
            "avg_df": avg_df,
        }

    return avg_df
