from pathlib import Path

from lumi_analysis.core.grouping import create_groups_from_folder
from lumi_analysis.core.analysis import run_analysis


def validate_pipeline_config(config):
    required_keys = [
        "input_folder",
        "replicates_per_group",
        "folder_name",
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
    print(f"Output folder: {config['folder_name']}")
    print(f"Experiment type: {config.get('experiment_type', 'tissue')}")
    print(f"Replicates per group: {config['replicates_per_group']}")

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

    result = run_analysis(
        input_folder=config["input_folder"],
        groups=groups,
        experiment_type=config.get("experiment_type", "tissue"),
        tissue_labels=config.get("tissue_labels"),
        save_file=config.get("save_file", True),
        suffix=config.get("file_suffix", "_Raw.csv"),
        folder_name=config["folder_name"],
    )

    result["groups"] = groups
    result["config"] = config

    return result
