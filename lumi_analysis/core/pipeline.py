from lumi_analysis.core.grouping import create_groups_from_folder
from lumi_analysis.core.analysis import run_analysis


def run_lumi_pipeline(config):
    groups = create_groups_from_folder(
        folder_path=config["input_folder"],
        replicates_per_group=config["replicates_per_group"],
        extension=config.get("extension", ".csv"),
        suffix_to_remove=config.get("suffix_to_remove", "_Raw"),
        sample_tags=config.get("sample_tags"),
        include_extra_group=config.get("include_extra_group", False),
    )

    result = run_analysis(
        input_folder=config["input_folder"],
        groups=groups,
        experiment_type=config.get("experiment_type", "tissue"),
        tissue_labels=config.get("tissue_labels"),
        save_file=config.get("save_file", True),
        suffix=config.get("file_suffix", "_Raw.csv"),
        folder_name=config.get("folder_name"),
    )

    return result
