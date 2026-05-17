from pathlib import Path

from lumi_analysis.core.grouping import create_groups_from_folder
from lumi_analysis.core.analysis import run_analysis
from lumi_analysis.core.results import LumiAnalysisResult
from lumi_analysis.plotting import plot_raw_replicates


def validate_pipeline_config(config):
    required_keys = [
        "input_folder",
        "replicates_per_group",
        "output_folder",
    ]

    missing_keys = [
        key for key in required_keys
        if key not in config or config[key] is None
    ]

    if missing_keys:
        raise ValueError(
            f"Missing required config values: {missing_keys}"
        )

    input_folder = Path(config["input_folder"])

    if not input_folder.exists():
        raise FileNotFoundError(
            f"Input folder does not exist: {input_folder}"
        )

    if not input_folder.is_dir():
        raise NotADirectoryError(
            f"Input path is not a folder: {input_folder}"
        )


def print_pipeline_summary(config, groups):
    print("\nLumi Analysis pipeline")
    print("----------------------")
    print(f"Input folder: {config['input_folder']}")
    print(f"Output folder: {config['output_folder']}")
    print(f"Replicates per group: {config['replicates_per_group']}")
    print(f"Noise threshold: {config.get('noise_max', 25)}")
    print(f"Remove noise: {config.get('remove_noise', True)}")
    print(f"Max rows: {config.get('max_rows')}")
    print(f"Max hours: {config.get('max_hours')}")
    print(f"Max days: {config.get('max_days')}")
    print(f"Plot raw data: {config.get('plot_raw_data', False)}")

    print("\nGroups:")
    for group_name, files in groups.items():
        print(f"{group_name}: {files}")


def get_group_plot_setting(config, group_name, setting_name, default=None):
    # Return group-specific plotting setting if provided,
    # otherwise fall back to the global config setting.
    group_settings = config.get("plot_group_settings", {})
    current_group_settings = group_settings.get(group_name, {})

    return current_group_settings.get(
        setting_name,
        config.get(setting_name, default),
    )


def plot_pipeline_results(config, analysis_result):
    if not config.get("plot_raw_data", False):
        return

    for group_name, group_result in analysis_result["group_results"].items():
        group_df = group_result["full_df"]

        plot_raw_replicates(
            group_df,
            title=f"{group_name} - raw data",
            save_path=f"{config['output_folder']}/{group_name}_raw_plot.png",

            mean_replicate_cols=get_group_plot_setting(config, group_name, "mean_replicate_cols", None),
            visible_replicate_cols=get_group_plot_setting(config, group_name, "visible_replicate_cols", None),
            recompute_mean=get_group_plot_setting(config, group_name, "recompute_mean", True),

            show=get_group_plot_setting(config, group_name, "show_plots", False),
            close=get_group_plot_setting(config, group_name, "close_plots", True),
            plot_style=get_group_plot_setting(config, group_name, "plot_style", "points"),
            y_limit=get_group_plot_setting(config, group_name, "y_limit", None),
            figsize=get_group_plot_setting(config, group_name, "figsize", (9, 5)),
            description=get_group_plot_setting(config, group_name, "description", None),

            replicate_markersize=get_group_plot_setting(config, group_name, "replicate_markersize", 2),
            replicate_linewidth=get_group_plot_setting(config, group_name, "replicate_linewidth", 1.2),
            replicate_alpha=get_group_plot_setting(config, group_name, "replicate_alpha", 0.75),

            average_markersize=get_group_plot_setting(config, group_name, "average_markersize", 3),
            average_linewidth=get_group_plot_setting(config, group_name, "average_linewidth", 2.2),
            average_color=get_group_plot_setting(config, group_name, "average_color", "black"),
            average_alpha=get_group_plot_setting(config, group_name, "average_alpha", 0.85),

            start_ct=config.get("ct_start_hour", 0),
            interval_minutes=config.get("interval_minutes", 10),
        )


def run_lumi_pipeline(config):
    validate_pipeline_config(config)

    groups = create_groups_from_folder(
        folder_path=config["input_folder"],
        replicates_per_group=config["replicates_per_group"],
        extension=config.get("extension", ".csv"),
        suffix_to_remove=config.get("suffix_to_remove", "_Raw"),
        sample_tags=config.get("sample_tags"),
        include_extra_group=config.get("include_extra_group", False),
    )

    print_pipeline_summary(config, groups)

    analysis_result = run_analysis(
        input_folder=config["input_folder"],
        groups=groups,
        group_labels=config.get("group_labels"),
        save_file=config.get("save_file", True),
        suffix=config.get("file_suffix", "_Raw.csv"),
        output_folder=config["output_folder"],
        noise_max=config.get("noise_max", 25),
        remove_noise=config.get("remove_noise", True),
        max_rows=config.get("max_rows"),
        max_hours=config.get("max_hours"),
        max_days=config.get("max_days"),
        interval_minutes=config.get("interval_minutes", 10),
    )

    plot_pipeline_results(config, analysis_result)

    return LumiAnalysisResult(
        group_results=analysis_result["group_results"],
        full_dfs=analysis_result["full_dfs"],
        groups=groups,
        config=config,
        complete_df=analysis_result.get("complete_df"),
        condensed_df=analysis_result.get("condensed_df"),
    )
