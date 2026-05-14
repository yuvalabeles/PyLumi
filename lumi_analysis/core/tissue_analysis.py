from lumi_analysis.core.loading import load_files
from lumi_analysis.core.validation import assert_interval_overlaps
from lumi_analysis.core.preprocessing import preprocess_replicates
from lumi_analysis.core.dataframes import create_sub_df

from lumi_analysis.export.excel_export import save_group_data


def analyse_tissue(
    path_lst,
    filenames,
    noise_max=25,
    remove_noise=True,
    save_file=True,
    sample=None,
    output_folder=None,
    return_intermediate=False,
):
    raw_dfs = load_files(path_lst)

    keep_all_rows = sample == "Extra"

    processed_dfs = preprocess_replicates(
        dfs=raw_dfs,
        filenames=filenames,
        noise_max=noise_max,
        remove_noise=remove_noise,
        keep_all_rows=keep_all_rows,
    )

    aligned_dfs = assert_interval_overlaps(processed_dfs)

    for df in aligned_dfs:
        df.drop(" Baseline", axis=1, inplace=True)

    full_df = create_sub_df(
        aligned_dfs,
        filenames,
        sample=sample,
    )

    if save_file:
        if sample is not None:
            filename = sample + "_"
        else:
            filename = "_".join(filenames)

        save_group_data(
            full_df,
            filename[0:-1],
            excel=False,
            output_folder=output_folder,
        )

    if return_intermediate:
        return {
            "sample": sample,
            "filenames": filenames,
            "raw_dfs": raw_dfs,
            "processed_dfs": processed_dfs,
            "aligned_dfs": aligned_dfs,
            "full_df": full_df,
        }

    return full_df
