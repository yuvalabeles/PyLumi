from lumi_analysis.core.pipeline import run_lumi_pipeline


# ==================================================================================================================== #
# USER SETTINGS
# Edit only this section before running the pipeline.
# Do not change anything below the USER SETTINGS section.
# ==================================================================================================================== #

config = {
    # ---------------------------------------------------------------------------------------------------------------- #
    # 1. INPUT DATA
    # Paste the path to the folder that contains the Lumi raw CSV files.
    # The folder should contain files such as:
    # 1a_Raw.csv, 1b_Raw.csv, 2a_Raw.csv, etc.
    # ---------------------------------------------------------------------------------------------------------------- #

    "input_folder": (
        r"C:/Users/yuval/OneDrive/Desktop/Lumi/"
        r"12.4.26/DM3_Lumi1 Allicin-Dex/Allicin 3 25uM-Dex/Analysis/Analysis/"
    ),

    # ---------------------------------------------------------------------------------------------------------------- #
    # 2. OUTPUT FOLDER
    # Choose the name/path of the folder where processed results will be saved.
    # If the folder does not exist, it will be created automatically.
    # ---------------------------------------------------------------------------------------------------------------- #

    "output_folder": "test_output",

    # ---------------------------------------------------------------------------------------------------------------- #
    # 3. GROUPING
    # How many raw files belong to each sample/group?
    # Example:
    # If each biological sample has 5 replicate files, use 5.
    # ---------------------------------------------------------------------------------------------------------------- #

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

    # ---------------------------------------------------------------------------------------------------------------- #
    # 4. ANALYSIS SETTINGS
    # noise_max:
    #   The minimum counts/sec value that marks the beginning of the real signal.
    #   All consecutive rows from the start, with counts below this threshold,
    #   are treated as pre-sample noise.
    #
    # remove_noise:
    #   True  = subtract the average pre-sample noise from the signal.
    #   False = keep the signal without subtracting that background.
    # ---------------------------------------------------------------------------------------------------------------- #

    "noise_max": 25,
    "remove_noise": True,

    # ---------------------------------------------------------------------------------------------------------------- #
    # 5. FILE SETTINGS
    # Usually these should NOT be changed. Change only if the Lumi output files use different names.
    # ---------------------------------------------------------------------------------------------------------------- #

    "extension": ".csv",
    "suffix_to_remove": "_Raw",
    "file_suffix": "_Raw.csv",

    # ---------------------------------------------------------------------------------------------------------------- #
    # 6. SAVING
    # True  = save processed files to output_folder.
    # False = run analysis without saving files.
    # ---------------------------------------------------------------------------------------------------------------- #

    "save_file": True,

    # ---------------------------------------------------------------------------------------------------------------- #
    # 7. DATA LENGTH / TAIL CUTTING
    # Optional: limit analysis to the first N rows/hours/days after alignment.
    # Use only one of max_rows, max_hours, max_days. Leave all as None to keep the full data.
    # ---------------------------------------------------------------------------------------------------------------- #

    "interval_minutes": 10,
    "max_rows": None,
    "max_hours": None,
    "max_days": 7,

    # ---------------------------------------------------------------------------------------------------------------- #
    # 8. PLOTTING SETTINGS
    # These settings control raw-data plots.
    # Global settings apply to all groups unless overridden in plot_group_settings.
    # ---------------------------------------------------------------------------------------------------------------- #

    # True  = create and save raw-data plots.
    # False = do not create raw-data plots.
    "plot_raw_data": True,

    # Plot display style - options:
    # "points"      = plot data as points only
    # "line"        = plot data as continuous lines
    # "points+line" = plot points connected by lines
    "plot_style": "points",

    # Y-axis limit:
    # None       = automatic y-axis scaling.
    # 500        = y-axis from 0 to 500.
    # (-100,500) = y-axis from -100 to 500.
    "y_limit": None,

    # Figure size in inches: (width, height)
    "figsize": (9, 5),

    # Optional text shown in the top-right corner of the plot:
    # Use None for no description or write your text in "...".
    "description": None,

    # Replicate control:
    # None = show in the figure and use for the mean all replicate columns automatically.
    # mean_replicate_cols controls which replicates are included in the average.
    # visible_replicate_cols controls which replicates are shown on the plot.
    #
    # Example:
    # "mean_replicate_cols": ["c i", "c iii"],
    # "visible_replicate_cols": [],
    #
    # This would calculate the average from c i and c iii, but show only the average curve/points.
    "mean_replicate_cols": None,
    "visible_replicate_cols": None,

    # CT shift.
    # This changes the CT values used in saved condensed data and plots.
    # Example: ct_start_hour=6 means the first row is CT=6.
    "ct_start_hour": 0,

    # Left x-axis limit for plots.
    # Usually keep 0 so the plot axis starts visually at 0,
    # even if the first data point starts at shifted CT such as 6.
    "x_axis_start": 0,

    # ---------------------------------------------------------------------------------------------------------------- #
    # 9. PEAK SETTINGS
    # These settings control peak markers on raw-data plots.
    # Global settings apply to all groups unless overridden in plot_group_settings.
    # ---------------------------------------------------------------------------------------------------------------- #

    # True  = detect and mark peaks on raw-data plots.
    # False = do not show peaks.
    "plot_peaks": True,

    # Which replicate peaks to show.
    # None = show peaks for all visible replicates.
    # []   = show no replicate peaks.
    # Example: ["c i", "c iii"]
    "peaks_to_show": None,

    # Which replicate should also get text labels next to their peaks:
    # None or [] = no replicate has peak text labels.
    # Example: ["c iii"]
    "peaks_to_show_txt": None,

    # Average peak visibility.
    "show_average_peaks": True,
    "show_average_peaks_txt": True,

    # ---------------------------------------------------------------------------------------------------------------- #
    # 10. PEAK/PERIOD TABLE SETTINGS
    # ---------------------------------------------------------------------------------------------------------------- #

    # True = create an Excel file with one peaks/periods table per group:
    "save_peak_tables": True,

    # Number of decimals in peak and period values:
    "peak_table_decimals": 2,

    # True  = period values are written as text like "(24.17 h)".
    # False = period values are saved as numeric values.
    "peak_table_period_as_text": True,

    # Whether to include the average signal as an additional row:
    "include_average_in_peak_table": True,

    # ---------------------------------------------------------------------------------------------------------------- #
    # Optional group-specific overrides:
    # Use this when different groups need different plot settings.
    # Any value written here overrides the global value above only for that group.
    # You can override regular plot settings AND peak settings here.
    # ---------------------------------------------------------------------------------------------------------------- #

    # Example:
    # "plot_group_settings": {
    #     "control": {
    #         "y_limit": 500,
    #         "figsize": (10, 5),
    #
    #         # Peak overrides for this group only:
    #         "plot_peaks": True,
    #         "peaks_to_show": ["c i", "c iii"],
    #         "peaks_to_show_txt": ["c iii"],
    #         "show_average_peaks": True,
    #         "show_average_peaks_txt": True,
    #         "min_peak_distance_hours": 20,
    #         "peak_prominence": None,
    #     },
    # },

    "plot_group_settings": {
    },

}


# ==================================================================================================================== #
# RUN PIPELINE
# Do not edit below this line unless you are changing the code itself.
# ==================================================================================================================== #

if __name__ == "__main__":
    result = run_lumi_pipeline(config)

    print("\nPipeline finished successfully.")

    print("\nGroups analysed:")
    for group_name in result.group_results.keys():
        print(f"    {group_name}")

    if result.condensed_df is not None:
        print("\nCondensed dataframe preview:")
        print(result.condensed_df.head())
