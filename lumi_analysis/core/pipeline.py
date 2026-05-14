from pathlib import Path

from lumi_analysis.core.grouping import create_groups_from_folder
from lumi_analysis.core.analysis import run_analysis
from lumi_analysis.core.results import LumiAnalysisResult


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

    print("\nGroups:")
    for group_name, files in groups.items():
        print(f"{group_name}: {files}")


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
    )

    return LumiAnalysisResult(
        group_results=analysis_result["group_results"],
        full_dfs=analysis_result["full_dfs"],
        groups=groups,
        config=config,
        complete_df=analysis_result.get("complete_df"),
        condensed_df=analysis_result.get("condensed_df"),
    )
