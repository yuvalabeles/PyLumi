from lumi_analysis.core.loading import load_files
from lumi_analysis.core.validation import assert_interval_overlaps
from lumi_analysis.core.preprocessing import preprocess_replicates

from lumi_analysis.core.dataframes import (
    create_cell_population_avg_df,
)


def analyse_cell_population(
    path_lst,
    filenames=None,
    noise_max=20,
    save_file=True,
    sample_name=None,
):
    dfs = load_files(path_lst)

    if filenames is None:
        filenames = [
            f"file_{i + 1}"
            for i in range(len(dfs))
        ]

    processed_dfs = preprocess_replicates(
        dfs=dfs,
        filenames=filenames,
        noise_max=noise_max,
        remove_noise=True,
        keep_all_rows=False,
    )

    dfs_aligned = assert_interval_overlaps(processed_dfs)

    avg_df = create_cell_population_avg_df(dfs_aligned)

    # Temporary backward-compatible saving.
    if save_file:
        filename = "avg_df.csv"

        if sample_name is not None:
            filename = sample_name + filename

        avg_df.to_csv(filename, index=False)

    return avg_df
