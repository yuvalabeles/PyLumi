"""
Create the default Lumi settings Excel template.

This script creates:
    settings.xlsx

The user should edit only the "value" column.
All other columns are locked and styled as read-only reference information.
"""

from pathlib import Path
import xlsxwriter


OUTPUT_FILE = "../settings.xlsx"


DISPLAY_NAMES = {
    "input_folder": "Input folder",
    "output_folder": "Output folder",
    "replicates_per_group": "Replicates per group",
    "sample_tags": "Sample names",
    "include_extra_group": "Include all files",
    "noise_max": "Maximum background noise",
    "remove_noise": "Remove background noise",
    "extension": "File extension",
    "suffix_to_remove": "Suffix to remove",
    "file_suffix": "Raw file suffix",
    "save_file": "Save processed files",
    "interval_minutes": "Length of Lumi's interval",
    "max_days": "Maximum days",
    "plot_raw_data": "Create plots of the data",
    "plot_style": "Choose plot style",
    "y_limit": "Y-axis upper limit",
    "description": "Plot description",
    "ct_start_hour": "CT start hour",
    "x_axis_start": "X-axis start (only changes the plot)",
    "plot_peaks": "Show peaks",
    "show_average_peaks": "Show average peaks",
    "show_average_peaks_txt": "Show average peak labels",
    "save_peak_tables": "Save peak/period tables",
    "peak_table_decimals": "Peak table decimals",
    "plot_group_settings": "Group-specific plot settings",
    "override_group_names": "Group names",
    "override_y_limit": "Y-axis limit",
    "override_description": "Plot description",
    "override_peak_txt_dy": "Peak label vertical offset",
    "override_mean_replicate_cols": "Replicates to disable",
    "override_visible_replicate_cols": "Replicates to hide",
}


SECTIONS = [
    {
        "title": "INPUT DATA",
        "settings": [
            {
                "name": "input_folder",
                "default": r"C:/Users/yuval/OneDrive/Desktop/Lumi/ORG slices contr females 13.4.26/Analysis/",
                "allowed": "Folder path as text. \nExample: C:/Users/.../Analysis/",
                "description": (
                    "Paste the path to the folder that contains the Lumi raw CSV files. "
                    "The folder should contain files such as 1a_Raw.csv, 1b_Raw.csv, 2a_Raw.csv, etc."
                ),
            },
        ],
    },
    {
        "title": "OUTPUT FOLDER",
        "settings": [
            {
                "name": "output_folder",
                "default": "test_output",
                "allowed": "Folder name or full folder path as text.",
                "description": (
                    "Choose the name/path of the folder where processed results will be saved. "
                    "If the folder does not exist, it will be created automatically."
                ),
            },
        ],
    },
    {
        "title": "GROUPING",
        "settings": [
            {
                "name": "replicates_per_group",
                "default": 5,
                "allowed": "Positive integer. \nExample: 5",
                "description": (
                    "How many raw files belong to each sample/group. "
                    "\nFor example, if each biological sample has 5 replicate files, use 5."
                ),
            },
            {
                "name": "sample_tags",
                "default": '["Liver1", "Liver2", "Kid1", "Kid2", "Lung1", "Lung2"]',
                "allowed": 'List of group names, or None. \nExample: ["Liver1", "Liver2"]',
                "description": (
                    "Optional group names. These names will be assigned to groups according to the detected file order. "
                    "If you do not want to provide names, write None. Then groups will be named automatically: "
                    "Group_1, Group_2, Group_3, ..."
                ),
            },
            {
                "name": "include_extra_group",
                "default": False,
                "allowed": "True / False",
                "description": (
                    "What to do with leftover files that do not complete a full group. "
                    "False = ignore leftover files and print a warning. "
                    "True = analyse leftover files as an additional group named Extra."
                ),
                "validation": ["True", "False"],
            },
        ],
    },
    {
        "title": "ANALYSIS SETTINGS",
        "settings": [
            {
                "name": "noise_max",
                "default": 25,
                "allowed": "Number. \nExample: 25",
                "description": (
                    "The minimum counts/sec value that marks the beginning of the real signal. "
                    "All consecutive rows from the start, with counts below this threshold, are treated as pre-sample noise."
                ),
            },
            {
                "name": "remove_noise",
                "default": True,
                "allowed": "True / False",
                "description": (
                    "True = subtract the average pre-sample noise from the signal. "
                    "False = keep the signal without subtracting that background."
                ),
                "validation": ["True", "False"],
            },
        ],
    },
    {
        "title": "FILE SETTINGS",
        "settings": [
            {
                "name": "extension",
                "default": ".csv",
                "allowed": "File extension as text. Usually .csv",
                "description": (
                    "Usually this should not be changed. Change only if the Lumi output files use a different file extension."
                ),
            },
            {
                "name": "suffix_to_remove",
                "default": "_Raw",
                "allowed": "Text suffix. \nExample: _Raw",
                "description": (
                    "Usually this should not be changed. This suffix is removed from raw file names when creating cleaner names."
                ),
            },
            {
                "name": "file_suffix",
                "default": "_Raw.csv",
                "allowed": "Text suffix. \nExample: _Raw.csv",
                "description": (
                    "Usually this should not be changed. Change only if the Lumi output files use different names."
                ),
            },
        ],
    },
    {
        "title": "SAVING",
        "settings": [
            {
                "name": "save_file",
                "default": True,
                "allowed": "True / False",
                "description": (
                    "True = save processed files to output_folder. "
                    "False = run analysis without saving files."
                ),
                "validation": ["True", "False"],
            },
        ],
    },
    {
        "title": "DATA LENGTH / TAIL CUTTING",
        "settings": [
            {
                "name": "interval_minutes",
                "default": 10,
                "allowed": "Positive number. \nExample: 10",
                "description": "Sampling interval in minutes.",
            },
            {
                "name": "max_days",
                "default": 7,
                "allowed": "Positive number, or None.",
                "description": (
                    "Optional: limit analysis to the first N days after alignment. "
                    "Use only one of max_rows, max_hours, max_days. Leave all as None to keep the full data."
                ),
            },
        ],
    },
    {
        "title": "PLOTTING SETTINGS",
        "settings": [
            {
                "name": "plot_raw_data",
                "default": True,
                "allowed": "True / False",
                "description": (
                    "True = create and save raw-data plots. "
                    "False = do not create raw-data plots."
                ),
                "validation": ["True", "False"],
            },
            {
                "name": "plot_style",
                "default": "line",
                "allowed": "points / line / points+line",
                "description": (
                    "Plot display style. points = plot data as points only. "
                    "line = plot data as continuous lines. "
                    "points+line = plot points connected by lines."
                ),
                "validation": ["points", "line", "points+line"],
            },
            {
                "name": "y_limit",
                "default": "None",
                "allowed": "None, a number, or a tuple. \nExamples: None, 500, (-100, 500)",
                "description": (
                    "Y-axis limit. None = automatic y-axis scaling. "
                    "500 = y-axis from 0 to 500. (-100, 500) = y-axis from -100 to 500."
                ),
            },
            {
                "name": "description",
                "default": "Control (females 13.4.26)",
                "allowed": "Text, or None.",
                "description": (
                    "Optional text shown in the top-right corner of the plot. "
                    "Use None for no description or write the desired text."
                ),
            },
            {
                "name": "ct_start_hour",
                "default": 6,
                "allowed": "Number. \nExample: 6",
                "description": (
                    "CT shift. This changes the CT values used in saved condensed data and plots. "
                    "\nExample: ct_start_hour = 6 means the first row is CT = 6."
                ),
            },
            {
                "name": "x_axis_start",
                "default": 0,
                "allowed": "Number. Usually 0.",
                "description": (
                    "Left x-axis limit for plots. Usually keep 0 so the plot axis starts visually at 0, "
                    "even if the first data point starts at shifted CT such as 6."
                ),
            },
        ],
    },
    {
        "title": "PEAK SETTINGS",
        "settings": [
            {
                "name": "plot_peaks",
                "default": True,
                "allowed": "True / False",
                "description": (
                    "True = detect and mark peaks on raw-data plots. "
                    "False = do not show peaks."
                ),
                "validation": ["True", "False"],
            },
            {
                "name": "show_average_peaks",
                "default": True,
                "allowed": "True / False",
                "description": "Whether to show peak markers for the average signal.",
                "validation": ["True", "False"],
            },
            {
                "name": "show_average_peaks_txt",
                "default": True,
                "allowed": "True / False",
                "description": "Whether to show text labels next to average-signal peaks.",
                "validation": ["True", "False"],
            },
        ],
    },
    {
        "title": "PEAK/PERIOD TABLE SETTINGS",
        "settings": [
            {
                "name": "save_peak_tables",
                "default": True,
                "allowed": "True / False",
                "description": "True = create an Excel file with one peaks/periods table per group.",
                "validation": ["True", "False"],
            },
            {
                "name": "peak_table_decimals",
                "default": 2,
                "allowed": "Non-negative integer. \nExample: 2",
                "description": "Number of decimals in peak and period values.",
            },
        ],
    },
    {
        "title": "GROUP-SPECIFIC OVERRIDES",
        "settings": [
            {
                "name": "override_group_names",
                "default": "[]",
                "allowed": 'List of group names. Example: ["Liver1", "Liver2", "Kid1"]',
                "description": (
                    "Use this section only when you want to override specific settings for specific groups. "
                    "First, write the group names in this row as a list. "
                    "Then, for each override setting below, write a list with the same number of positions and in the same order. "
                    "Each position matches the group name in the same position. "
                    "Leave an empty position when you do not want to override that setting for that group. "
                    "For example, if group names are [\"Liver1\", \"Liver2\", \"Kid1\"], then [500, , 700] means: "
                    "Liver1 gets 500, Liver2 gets no override, and Kid1 gets 700. "
                    "Spaces in empty positions are allowed. For text values, use quotes, for example: [\"Control\", , \"Kidney\"]."
                ),
            },
            {
                "name": "override_y_limit",
                "default": "[]",
                "allowed": "List with one value per group, or an empty position for no override. Example: [500, , (-100, 500)]",
                "description": "See section: PLOTTING SETTINGS, setting: Y-axis limit, for a detailed description.",
            },
            {
                "name": "override_description",
                "default": "[]",
                "allowed": 'List with one value per group, or an empty position for no override. Example: ["Control", , "Kidney"]',
                "description": "See section: PLOTTING SETTINGS, setting: Plot description, for a detailed description.",
            },
            {
                "name": "override_peak_txt_dy",
                "default": "[]",
                "allowed": "List with one value per group, or an empty position for no override. Example: [20, , 35]",
                "description": "See section: PEAK SETTINGS, setting: Peak label vertical offset, for a detailed description.",
            },
            {
                "name": "override_mean_replicate_cols",
                "default": "[]",
                "allowed": 'List with one value per group, or an empty position for no override. Example: [None, ["c i", "c iii"], ]',
                "description": "See section: PLOTTING SETTINGS, setting: Replicates used for mean, for a detailed description.",
            },
            {
                "name": "override_visible_replicate_cols",
                "default": "[]",
                "allowed": 'List with one value per group, or an empty position for no override. Example: [None, [], ["c i"]]',
                "description": "See section: PLOTTING SETTINGS, setting: Replicates shown on plot, for a detailed description.",
            },
        ],
    },
]


def create_settings_template(output_path=OUTPUT_FILE):
    output_path = Path(output_path)

    workbook = xlsxwriter.Workbook(output_path)
    worksheet = workbook.add_worksheet("Settings")

    # Workbook formats
    title_format = workbook.add_format({
        "bold": True,
        "font_size": 16,
        "font_color": "white",
        "bg_color": "white",
        # "align": "center",
        "valign": "vcenter",
        "border": 1,
        "locked": True,
    })

    section_side_format = workbook.add_format({
        "bold": True,
        "font_size": 15,
        "font_color": "000000",
        "bg_color": "#EDEDED",
        "align": "center",
        "valign": "vcenter",
        "border": 1,
        "text_wrap": True,
        "locked": True,
    })

    header_locked_format = workbook.add_format({
        "bold": True,
        "font_size": 18,
        "bg_color": "#FAEAEA",
        "border": 1,
        "align": "center",
        "valign": "vcenter",
        "locked": True,
    })

    header_section_format = workbook.add_format({
        "bold": True,
        "font_size": 18,
        "bg_color": "#EDEDED",
        "border": 1,
        "align": "center",
        "valign": "vcenter",
        "locked": True,
    })

    header_editable_format = workbook.add_format({
        "bold": True,
        "font_size": 18,
        "bg_color": "#DAEEF3",
        "border": 1,
        "align": "center",
        "valign": "vcenter",
        "locked": False,
    })

    locked_text_format = workbook.add_format({
        "bg_color": "#FAEAEA",
        "border": 1,
        "valign": "vcenter",
        "text_wrap": True,
        "locked": True,
        "font_size": 15,
    })

    locked_centered_format = workbook.add_format({
        "bg_color": "#FAEAEA",
        "border": 1,
        "align": "center",
        "valign": "vcenter",
        "text_wrap": True,
        "locked": True,
        "font_size": 15,
    })

    locked_description_format = workbook.add_format({
        "bg_color": "#FAEAEA",
        "border": 1,
        "valign": "vcenter",
        "text_wrap": True,
        "locked": True,
        "font_size": 15,
    })

    editable_text_format = workbook.add_format({
        "bg_color": "#DAEEF3",
        "border": 1,
        "align": "center",
        "valign": "vcenter",
        "text_wrap": True,
        "locked": False,
        "font_size": 15,
        "bold": True,
    })

    editable_number_format = workbook.add_format({
        "bg_color": "#DAEEF3",
        "border": 1,
        "align": "center",
        "valign": "vcenter",
        "locked": False,
        "font_size": 15,
        "bold": True,

    })

    # Column setup
    headers = ["Section", "Setting", "Value", "Possible Values", "Description", "Config Key"]
    worksheet.write(0, 0, headers[0], header_section_format)
    worksheet.write(0, 1, headers[1], header_locked_format)
    worksheet.write(0, 2, headers[2], header_editable_format)
    worksheet.write_row(0, 3, headers[3:], header_locked_format)

    worksheet.set_column(0, 0, 22)
    worksheet.set_column(1, 1, 42)
    worksheet.set_column(2, 2, 42)
    worksheet.set_column(3, 3, 42)
    worksheet.set_column(4, 4, 75)
    worksheet.set_column(5, 5, 0, None, {"hidden": True})

    worksheet.freeze_panes(1, 0)

    row = 1

    for section in SECTIONS:
        # Blank white row before each section.
        worksheet.merge_range(row, 0, row, 5, "", title_format)
        worksheet.set_row(row, 20)
        row += 1

        section_start_row = row
        section_end_row = row + len(section["settings"]) - 1

        if section_start_row == section_end_row:
            worksheet.write(section_start_row, 0, section["title"], section_side_format)
        else:
            worksheet.merge_range(section_start_row, 0, section_end_row, 0, section["title"], section_side_format)

        for item in section["settings"]:
            display_name = DISPLAY_NAMES.get(item["name"], item["name"].replace("_", " ").title()) + ":"
            worksheet.write(row, 1, display_name, locked_text_format)

            default_value = item["default"]
            if isinstance(default_value, bool):
                worksheet.write(row, 2, str(default_value), editable_text_format)
            elif isinstance(default_value, (int, float)):
                worksheet.write(row, 2, default_value, editable_number_format)
            else:
                worksheet.write(row, 2, default_value, editable_text_format)

            worksheet.write(row, 3, item["allowed"], locked_centered_format)
            worksheet.write(row, 4, item["description"], locked_description_format)
            worksheet.write(row, 5, item["name"], locked_text_format)

            if "validation" in item:
                worksheet.data_validation(row, 2, row, 2, {
                    "validate": "list",
                    "source": item["validation"],
                    "input_title": "Choose a value",
                    "input_message": "Choose one of the allowed values.",
                    "error_title": "Invalid value",
                    "error_message": "Please choose one of the allowed values.",
                })

            # worksheet.set_row(row, 70)
            row += 1

    # Make it clear that only the value column should be edited.
    worksheet.write_comment(
        "C1",
        "Edit only this column. The other columns are locked and are meant as documentation."
    )

    # Protect the worksheet so only unlocked cells can be edited.
    # No password is used, so the sheet can still be unprotected easily if needed.
    worksheet.protect(options={
        "select_locked_cells": True,
        "select_unlocked_cells": True,
        "format_cells": False,
        "format_columns": False,
        "format_rows": False,
        "insert_columns": False,
        "insert_rows": False,
        "delete_columns": False,
        "delete_rows": False,
    })

    workbook.close()
    print(f"Created: {output_path.resolve()}")


if __name__ == "__main__":
    create_settings_template()
