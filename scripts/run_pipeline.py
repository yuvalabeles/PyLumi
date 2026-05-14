from lumi_analysis.core.pipeline import run_lumi_pipeline


# =============================================================================
# USER SETTINGS
# Edit only this section before running the pipeline.
# Do not change anything below the USER SETTINGS section.
# =============================================================================

config = {
    # -------------------------------------------------------------------------
    # 1. INPUT DATA
    # Paste the path to the folder that contains the Lumi raw CSV files.
    # The folder should contain files such as:
    # 1a_Raw.csv, 1b_Raw.csv, 2a_Raw.csv, etc.
    # -------------------------------------------------------------------------
    "input_folder": (
        r"C:/Users/yuval/OneDrive/Desktop/Lumi/"
        r"12.4.26/DM3_Lumi1 Allicin-Dex/Allicin 3 25uM-Dex/Analysis/Analysis/"
    ),

    # -------------------------------------------------------------------------
    # 2. OUTPUT FOLDER
    # Choose the name/path of the folder where processed results will be saved.
    # If the folder does not exist, it will be created automatically.
    # -------------------------------------------------------------------------
    "output_folder": "test_output",

    # -------------------------------------------------------------------------
    # 3. EXPERIMENT TYPE
    # Choose one option:
    #   "tissue"          = tissue/slice samples
    #   "cell_population" = cell population samples
    # -------------------------------------------------------------------------
    "experiment_type": "cell_population",

    # -------------------------------------------------------------------------
    # 4. GROUPING
    # How many raw files belong to each sample/group?
    # Example:
    # If each tissue has 5 replicate files, use 5.
    # -------------------------------------------------------------------------
    "replicates_per_group": 3,

    # Optional sample names.
    # These names will be assigned to groups according to the detected file order.
    #
    # If you do not want to provide names, write:
    # "sample_tags": None,
    #
    # Then the groups will be named automatically:
    # Group_1, Group_2, Group_3, ...
    "sample_tags": [
        "control"
    ],

    # What to do with leftover files that do not complete a full group.
    # False = ignore leftover files and print a warning.
    # True  = analyse leftover files as an additional group named "Extra".
    "include_extra_group": False,

    # -------------------------------------------------------------------------
    # 5. ANALYSIS SETTINGS
    # noise_max:
    #   The minimum counts/sec value that marks the beginning of the real signal.
    #   All consecutive rows from the start, with counts below this threshold,
    #   are treated as pre-sample noise.
    #
    # remove_noise:
    #   True  = subtract the average pre-sample noise from the signal.
    #   False = keep the signal without subtracting that background.
    # -------------------------------------------------------------------------
    "noise_max": 25,
    "remove_noise": True,

    # -------------------------------------------------------------------------
    # 6. FILE SETTINGS
    # Usually these should not be changed.
    # Change only if the Lumi output files use different names.
    # -------------------------------------------------------------------------
    "extension": ".csv",
    "suffix_to_remove": "_Raw",
    "file_suffix": "_Raw.csv",

    # -------------------------------------------------------------------------
    # 7. SAVING
    # True  = save processed files to output_folder.
    # False = run analysis without saving files.
    # -------------------------------------------------------------------------
    "save_file": True,
}


# =============================================================================
# RUN PIPELINE
# Do not edit below this line unless you are changing the code itself.
# =============================================================================

if __name__ == "__main__":
    result = run_lumi_pipeline(config)

    print("\nPipeline finished successfully.")

    print("\nSamples analysed:")
    for sample_name in result.sample_results.keys():
        print(f"    {sample_name}")

    if result.condensed_df is not None:
        print("\nCondensed dataframe preview:")
        print(result.condensed_df.head())
