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
    # 3. GROUPING
    # How many raw files belong to each sample/group?
    # Example:
    # If each biological sample has 5 replicate files, use 5.
    # -------------------------------------------------------------------------
    "replicates_per_group": 3,

    # Optional group names.
    # These names will be assigned to groups according to the detected file order.
    # For example, if you are running the Lumi on tissue samples, use the names of each tissue.
    #
    # If you do not want to provide names, write:
    # "sample_tags": None,
    # Then the groups will be named automatically:
    # Group_1, Group_2, Group_3, ...
    "sample_tags": [
        "control",
    ],

    # What to do with leftover files that do not complete a full group.
    # False = ignore leftover files and print a warning.
    # True  = analyse leftover files as an additional group named "Extra".
    "include_extra_group": False,

    # -------------------------------------------------------------------------
    # 4. ANALYSIS SETTINGS
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
    # 5. FILE SETTINGS
    # Usually these should not be changed.
    # Change only if the Lumi output files use different names.
    # -------------------------------------------------------------------------
    "extension": ".csv",
    "suffix_to_remove": "_Raw",
    "file_suffix": "_Raw.csv",

    # -------------------------------------------------------------------------
    # 6. SAVING
    # True  = save processed files to output_folder.
    # False = run analysis without saving files.
    # -------------------------------------------------------------------------
    "save_file": True,

    # -------------------------------------------------------------------------
    # 7. DATA LENGTH / TAIL CUTTING
    # Optional: limit analysis to the first N rows/hours/days after alignment.
    # Use only one of max_rows, max_hours, max_days.
    # Leave all as None to keep the full data.
    # -------------------------------------------------------------------------
    "interval_minutes": 10,
    "max_rows": None,
    "max_hours": None,
    "max_days": 7,

    # -------------------------------------------------------------------------
    # 8. PLOTTING SETTINGS
    # These settings control raw-data plots.
    # Global settings apply to all groups unless overridden in plot_group_settings.
    # -------------------------------------------------------------------------

    # True  = create and save raw-data plots.
    # False = do not create raw-data plots.
    "plot_raw_data": True,

    # Plot display style.
    # Options:
    # "points"      = plot data as points only
    # "line"        = plot data as continuous lines
    # "points+line" = plot points connected by lines
    "plot_style": "points",

    # Y-axis limit.
    # None       = automatic y-axis scaling.
    # 500        = y-axis from 0 to 500.
    # (-100,500) = y-axis from -100 to 500.
    "y_limit": None,

    # Figure size in inches: (width, height).
    "figsize": (9, 5),

    # Optional text shown in the top-right corner of the plot.
    # Use None for no description.
    "description": None,

    # Replicate control.
    # None = use all replicate columns automatically.
    #
    # mean_replicate_cols controls which replicates are included in the average.
    # visible_replicate_cols controls which replicates are shown on the plot.
    #
    # Example:
    # "mean_replicate_cols": ["c i", "c iii"],
    # "visible_replicate_cols": [],
    #
    # This would calculate the average from c i and c iii,
    # but show only the average curve/points.
    "mean_replicate_cols": None,
    "visible_replicate_cols": None,

    # True  = recalculate the average from mean_replicate_cols.
    # False = use the existing counts/sec (avg) column.
    "recompute_mean": True,

    # Plot display behavior.
    # show_plots=False avoids plt.show(), which is safer in PyCharm.
    # close_plots=True closes figures after saving to avoid memory buildup.
    "show_plots": False,
    "close_plots": True,

    # Optional group-specific overrides.
    # Use this when different groups need different y-limits, sizes, styles, etc.
    # Any value written here overrides the global value above only for that group.
    "plot_group_settings": {
        # Example:
        # "control": {
        #     "y_limit": 500,
        #     "figsize": (10, 5),
        #     "average_markersize": 4,
        # },
    },

}


# =============================================================================
# RUN PIPELINE
# Do not edit below this line unless you are changing the code itself.
# =============================================================================

if __name__ == "__main__":
    result = run_lumi_pipeline(config)

    print("\nPipeline finished successfully.")

    print("\nGroups analysed:")
    for group_name in result.group_results.keys():
        print(f"    {group_name}")

    if result.condensed_df is not None:
        print("\nCondensed dataframe preview:")
        print(result.condensed_df.head())
