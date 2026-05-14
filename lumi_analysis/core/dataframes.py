import numpy as np
import pandas as pd

from lumi_analysis.export.excel_export import save_tissue_data


def create_sub_df(dfs_aligned, filenames, save_file=True, sample=None, folder_name=None):
    # Create and save (optional) a sub-dataframe for replicates only
    full_df = pd.DataFrame({"Date": dfs_aligned[0]["Date"], "Time (hr:min)": dfs_aligned[0]["Time (hr:min)"],
                            "Time (days)": dfs_aligned[0]["Time (days)"]})

    counts = pd.DataFrame({filenames[i]: dfs_aligned[i]["counts/sec"] for i in range(len(dfs_aligned))})

    for i in range(len(dfs_aligned)):
        full_df[filenames[i]] = dfs_aligned[i]["counts/sec"].round(4)

    if sample != "Extra":
        full_df["counts/sec (avg)"] = counts.mean(axis=1).round(4)
    else:
        full_df = full_df.rename(columns={'Time (hr:min)': 'Time'})

    if save_file:
        if sample is not None:
            filename = sample + "_"
        else:
            filename = ""
            for f in filenames:
                filename += f + "_"

        save_tissue_data(full_df, filename[0:-1], excel=False, folder_name=folder_name)

    return full_df


def create_condensed_df(complete_df, tissue_labels, save_file=True, folder_name=None):
    # Create and save (optional) a dataframe for all data, without date/time columns
    n = len(complete_df)

    # Create a column of CT (in hours):
    time_col = np.arange(n) / 6  # 10-minute steps in hours

    # Create a blank column (same number of rows):
    indices = np.array(i for i in range(len(complete_df)))

    # Add CT column to the complete dataframe:
    complete_df.insert(0, ' ', indices)
    complete_df.insert(0, 'CT [in hours]', time_col)
    complete_df['CT [in hours]'] = complete_df['CT [in hours]'].round(2)

    # Drop all additional date/time columns:
    cols_to_drop = ['Date', 'Time (hr:min)', 'Time (days)']
    condensed_df = complete_df.drop(columns=cols_to_drop)

    # Save result (optional):
    if save_file:
        save_tissue_data(condensed_df, "Data - complete", tissue_labels=tissue_labels, folder_name=folder_name)

    return condensed_df


def create_complete_df(full_dfs, save_file=True, folder_name=None):
    # Create and save (optional) the full dateframe of the analysis
    result_parts = []

    # Create a blank column (same number of rows):
    blank = pd.DataFrame(np.nan, index=full_dfs[0].index, columns=[""])

    for i, df_ in enumerate(full_dfs):
        result_parts.append(df_)
        if i < len(full_dfs) - 1:  # don't add blank after last df
            result_parts.append(blank.copy())

    complete_df = pd.concat(result_parts, axis=1)

    # Save result (optional):
    if save_file:
        save_tissue_data(complete_df, "complete_df", folder_name=folder_name)

    return complete_df
