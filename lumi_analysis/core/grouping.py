from pathlib import Path

import numpy as np


def discover_raw_files(folder_path, extension=".csv", suffix_to_remove="_Raw"):
    folder = Path(folder_path)

    if not folder.exists():
        raise FileNotFoundError(f"Folder does not exist: {folder}")

    if not folder.is_dir():
        raise NotADirectoryError(f"Path is not a folder: {folder}")

    files = [
        file for file in folder.iterdir()
        if file.is_file() and file.suffix == extension
    ]

    files = sorted(files, key=lambda file: file.name.lower())

    file_names = []
    for file in files:
        name = file.stem

        if suffix_to_remove and name.endswith(suffix_to_remove):
            name = name[:-len(suffix_to_remove)]

        file_names.append(name)

    return file_names


def print_groups(groups):
    print("\nGenerated groups:")
    max_len = 0
    for group_name in list(groups.keys()):
        max_len = max(len(group_name), max_len)

    for group_name, files in groups.items():
        spaces = (max_len - len(group_name)) + 4
        spaces = " " * spaces
        print(f"{group_name}:", spaces, np.array(files))


def create_fixed_size_groups(
    file_names,
    replicates_per_group,
    sample_tags=None,
    include_extra_group=False,
    extra_group_name="Extra",
):
    if replicates_per_group <= 0:
        raise ValueError("replicates_per_group must be greater than 0")

    groups = {}

    full_group_count = len(file_names) // replicates_per_group
    # leftover_count = len(file_names) % replicates_per_group

    if sample_tags is None:
        sample_tags = []

    for i in range(full_group_count):
        start = i * replicates_per_group
        end = start + replicates_per_group

        if i < len(sample_tags):
            group_name = sample_tags[i]
        else:
            unlabeled_index = i - len(sample_tags) + 1
            group_name = f"Unlabeled {unlabeled_index}"

        groups[group_name] = file_names[start:end]

    used_files_count = full_group_count * replicates_per_group
    extra_files = file_names[used_files_count:]

    if extra_files and include_extra_group:
        groups[extra_group_name] = extra_files

    if extra_files and not include_extra_group:
        print("\nWarning: Some files were not assigned to any group:")
        for file_name in extra_files:
            print(f"    {file_name}")

    if len(sample_tags) > full_group_count:
        missing_tags = sample_tags[full_group_count:]

        print("\nWarning: Some sample tags did not receive any files:")
        for tag in missing_tags:
            print(f"    {tag}")

    print_groups(groups)

    return groups


def create_groups_from_folder(
    folder_path,
    replicates_per_group,
    extension=".csv",
    suffix_to_remove="_Raw",
    sample_tags=None,
    include_extra_group=False,
):
    file_names = discover_raw_files(
        folder_path=folder_path,
        extension=extension,
        suffix_to_remove=suffix_to_remove,
    )

    groups = create_fixed_size_groups(
        file_names=file_names,
        replicates_per_group=replicates_per_group,
        sample_tags=sample_tags,
        include_extra_group=include_extra_group,
    )

    return groups
