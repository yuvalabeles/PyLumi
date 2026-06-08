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
    "disabled_replicates": "Disabled replicates",
    "include_extra_group": "Include extra files",
    "noise_max": "Maximum background noise",
    "remove_noise": "Remove background noise",
    "extension": "File extension",
    "suffix_to_remove": "Suffix to remove",
    "file_suffix": "Raw file suffix",
    "save_file": "Save processed files",
    "interval_minutes": "Length of Lumi's interval",
    "max_days": "Maximum days to analyze",
    "plot_raw_data": "Create plots of the data",
    "replicate_display_mode": "Replicate display mode",
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
    "override_visible_replicate_cols": "Replicates to hide",
}


SECTIONS = [
    {
        "title": "INPUT DATA",
        "settings": [
            {
                "name": "input_folder",
                "required": True,
                "default": None,
                "allowed": "Folder path as text. \n\nExample: C:/Users/.../Analysis/",
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
                "required": True,
                "default": "analysis_output",
                "allowed": "Folder name \nor \nFull folder path",
                "description": (
                    "Choose the name/path of the folder where processed results will be saved. "
                    "If the folder does not exist, it will create a new folder with that name."
                ),
            },
        ],
    },
    {
        "title": "GROUPING",
        "settings": [
            {
                "name": "replicates_per_group",
                "required": True,
                "default": 3,
                "allowed": "Positive integer. \n\nExample: 3",
                "description": (
                    "How many raw files belong to each sample/group."
                    "\nThey are grouped by their order in your folder."
                    "\n\nFor example, if each sample has 4 replicate files, use 4."
                ),
            },
            {
                "name": "sample_tags",
                "default": None,
                "allowed": 'List of group names, or None. \n\nExample: ["Liver", "Kidney", "Lung"]',
                "description": (
                    "Optional labels for each group of replicates. "
                    "These names will be assigned to groups according to the detected file order."
                    # "\n\nIf no labels are provided, the groups will be named automatically: "
                    # "\"Unlabeled_1\", \"Unlabeled_2\", \"Unlabeled_3\", ..."
                ),
            },
            {
                "name": "disabled_replicates",
                "default": "[]",
                "allowed": 'List of replicate names. \n\nExample: ["1a", "2b", "3c"]',
                "description": (
                    "Choose specific replicates to disable from the analysis."
                    "\n\nNOTE: each replicate name must be written inside quotes (\" \")."
                    "\n\nCorrect example: [\"1a\", \"2b\"]"
                    "\nIncorrect example: [\"1a_Raw.csv\", \"2b_Raw.csv\"]"
                ),
            },
            {
                "name": "include_extra_group",
                "default": False,
                "allowed": "True / False",
                "description": (
                    "Handle the extra files that don't complete a full group: "
                    "\n\n•  False = ignore leftover files and print a message to the user."
                    "\n•  True = analyse leftover files as an additional group named Extra."
                ),
                "validation": ["True", "False"],
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
                    "•  True = create and save raw-data plots. "
                    "\n•  False = do not create raw-data plots."
                ),
                "validation": ["True", "False"],
            },
            {
                "name": "replicate_display_mode",
                "default": "replicates_and_mean",
                "allowed": "replicates_and_mean /\nmean_only /\nreplicates_only",
                "description": (
                    "Choose what to display on the raw-data plots from these options:"
                    "\n\n•  replicates_and_mean = show replicates and their average."
                    "\n•  mean_only = show only the average signal."
                    "\n•  replicates_only = show only the replicates, without the average."
                    "\n\nNOTE: you can also hide specific replicates in the override section."
                ),
                "validation": [
                    "replicates_and_mean",
                    "mean_only",
                    "replicates_only",
                ],
            },
            {
                "name": "plot_style",
                "default": "line",
                "allowed": "points /\nline /\npoints+line",
                "description": (
                    "Plot display style - choose from the options below:"
                    "\n\n•  points = plot data as points only."
                    "\n•  line = plot data as continuous lines."
                    "\n•  points+line = plot points connected by lines."
                ),
                "validation": ["points", "line", "points+line"],
            },
            {
                "name": "y_limit",
                "default": None,
                "allowed": "None, an upper limit, or a range. \n\nExamples: None, 500, (-100, 500)",
                "description": (
                    "You can choose a unified Y-axis limit for all the groups:"
                    "\n\n•  None = automatic y-axis scaling."
                    "\n•  500 = y-axis from 0 to 500."
                    "\n•  (-100, 500) = y-axis from -100 to 500."
                ),
            },
            {
                "name": "description",
                "default": None,
                "allowed": "Text, or None. \n\nExample: \"Experiment 2.6.26\".",
                "description": (
                    "Optional text shown in the top-right corner of the plot."
                    "\nUse None for no description or write the desired text in quotes \" \"."
                ),
            },
            {
                "name": "ct_start_hour",
                "default": 0,
                "allowed": "Number. \n\nExample: 6",
                "description": (
                    "CT shift - this changes the CT values to start from the given shift."
                    "\n\nExample: CT start hour = 6 means the first row is CT = 6."
                ),
            },
            {
                "name": "x_axis_start",
                "default": 0,
                "allowed": "Number. \n(Usually 0)",
                "description": (
                    "Left x-axis limit for the plots. "
                    "\nUsually keep 0 so the plot axis starts visually at 0, "
                    "even if the first data point starts at some shifted CT such as 6."
                ),
            },
        ],
    },
    {
        "title": "PEAK SETTINGS",
        "settings": [
            {
                "name": "plot_peaks",
                "default": False,
                "allowed": "True / False",
                "description": (
                    "•  True = show peaks for each replicate on raw-data plots. "
                    "\n•  False = do not show peaks for the replicates."
                ),
                "validation": ["True", "False"],
            },
            {
                "name": "show_average_peaks",
                "default": False,
                "allowed": "True / False",
                "description": (
                    "•  True = show the peaks of the average signal on raw-data plots."
                    "\n•  False = do not show peaks for the average signal."
                ),
                "validation": ["True", "False"],
            },
            {
                "name": "show_average_peaks_txt",
                "default": False,
                "allowed": "True / False",
                "description": "•  True = show text labels with CT next to average-signal peaks."
                               "\n•  False = do not show CT labels.",
                "validation": ["True", "False"],
            },
        ],
    },
    {
        "title": "GROUP-SPECIFIC OVERRIDES",
        "settings": [
            {
                "name": "override_group_names",
                "default": "[]",
                "allowed": 'List of group names. \nExample: ["Liver", "Lung"]',
                "description": (
                    "Use this section only when you want to limit Y-axis differently for specific groups."
                    "For example, if group names are [\"Liver\", \"Lung\"], then [500, 700] means:"
                    "Liver gets 500, and Lung gets 700."
                    "\n\nNOTE: each group name MUST be in quotes (example: \"Liver\")."
                    "Each position matches the group name in the same position."
                ),
            },
            {
                "name": "override_y_limit",
                "default": "[]",
                "allowed": "List with limits (number/range)."
                           "\n\nExample: [500, (-100, 500)]",
                "description":
                    "\nWhen choosing a limit, maintain the same order in which you listed the groups."
            },
            # {
            #     "name": "override_description",
            #     "default": "[]",
            #     "allowed": 'List with one value per group, or None for no override. \n\nExample: ["Exp. 1", None, None, None]',
            #     "description": "See section: PLOTTING SETTINGS, setting: Plot description, for a detailed description.",
            # },
            # {
            #     "name": "override_peak_txt_dy",
            #     "default": "[]",
            #     "allowed": "List with one value per group, or None for no override. \n\nExample: [20, None, None, 35]",
            #     "description": "This value is used to adjust the position of the peak text labels.",
            # },
            # {
            #     "name": "override_visible_replicate_cols",
            #     "default": "[]",
            #     "allowed": "See examples above.",
            #     "description": "For each group choose specific replicates to hide from the plot."
            #                    "\n\nNOTE: this does NOT exclude them from the calculation of the average signal.",
            # },
        ],
    },
    {
        "title": "PEAK/PERIOD TABLE SETTINGS",
        "settings": [
            {
                "name": "save_peak_tables",
                "default": True,
                "allowed": "True / False",
                "description": "•  True = create an Excel file with peaks + periods table per group."
                               "\n•  False = do not create an Excel file for peaks + periods.",
                "validation": ["True", "False"],
            },
            # {
            #     "name": "peak_table_decimals",
            #     "default": 2,
            #     "allowed": "Non-negative integer. \n\nExample: 2",
            #     "description": "Number of decimals in peak and period values.",
            # },
        ],
    },
    {
        "title": "DATA LENGTH / TAIL CUTTING",
        "settings": [
            {
                "name": "interval_minutes",
                "default": 10,
                "allowed": "Positive number. \n\nExample: 10",
                "description": "The length of the sampling interval in minutes. "
                               "\n\nNOTE: Lumi's interval by default is 10 minutes.",
            },
            {
                "name": "max_days",
                "default": None,
                "allowed": "Positive number, or None.",
                "description": (
                    "Limit analysis to the first N days. "
                    "Leave None for no limit, or choose a positive number N for number of days to analyze."
                    "\n\nThis feature is useful to cut the tail of the data if it isn't significant to the analysis."
                ),
            },
        ],
    },
    {
        "title": "ANALYSIS SETTINGS",
        "settings": [
            {
                "name": "noise_max",
                "default": 25,
                "allowed": "Number. \n\nExample: 25",
                "description": (
                    "The minimum counts/sec value that marks the beginning of the real signal."
                    "All consecutive rows from the start, with counts below this threshold, are treated as pre-sample noise."
                ),
            },
            {
                "name": "remove_noise",
                "default": True,
                "allowed": "True / False",
                "description": (
                    "•  True = subtract the average pre-sample noise from the signal."
                    "\n•  False = keep the signal without subtracting that background."
                ),
                "validation": ["True", "False"],
            },
        ],
    },
    # {
    #     "title": "FILE SETTINGS",
    #     "settings": [
    #         {
    #             "name": "extension",
    #             "default": ".csv",
    #             "allowed": "File extension. \n\nExample .csv",
    #             "description": (
    #                 "Usually this should not be changed. Change only if the Lumi output files use a different file extension."
    #             ),
    #         },
    #         {
    #             "name": "suffix_to_remove",
    #             "default": "_Raw",
    #             "allowed": "Text suffix. \n\nExample: _Raw",
    #             "description": (
    #                 "Usually this should not be changed. This suffix is removed from raw file names when creating cleaner names."
    #             ),
    #         },
    #         {
    #             "name": "file_suffix",
    #             "default": "_Raw.csv",
    #             "allowed": "Text suffix. \n\nExample: _Raw.csv",
    #             "description": (
    #                 "Usually this should not be changed. Change only if the Lumi output files use different names."
    #             ),
    #         },
    #     ],
    # },
    {
        "title": "SAVING",
        "settings": [
            {
                "name": "save_file",
                "default": True,
                "allowed": "True / False",
                "description": (
                    "•  True = save processed files to the given output folder."
                    "\n•  False = run analysis without saving files."
                ),
                "validation": ["True", "False"],
            },
        ],
    },
]


def create_settings_template(output_path=OUTPUT_FILE):
    output_path = Path(output_path)

    workbook = xlsxwriter.Workbook(output_path)
    worksheet = workbook.add_worksheet("Settings")

    title_format = workbook.add_format({
        "bold": True,
        "font_size": 16,
        "font_color": "white",
        "bg_color": "white",
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

    red_star_format = workbook.add_format({
        "bg_color": "#FAEAEA",
        "border": 1,
        "valign": "vcenter",
        "text_wrap": True,
        "locked": True,
        "font_size": 20,
        "font_color": "red",
        "bold": True,
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

    headers = ["Section", "Setting", "Value", "Possible Values", "Description", "Config Key"]
    worksheet.write(0, 0, headers[0], header_section_format)
    worksheet.write(0, 1, headers[1], header_locked_format)
    worksheet.write(0, 2, headers[2], header_editable_format)
    worksheet.write_row(0, 3, headers[3:], header_locked_format)

    worksheet.set_column(0, 0, 22)
    worksheet.set_column(1, 1, 42)
    worksheet.set_column(2, 2, 42)
    worksheet.set_column(3, 3, 42)
    worksheet.set_column(4, 4, 78)
    worksheet.set_column(5, 5, 0, None, {"hidden": True})

    worksheet.freeze_panes(1, 0)

    row = 1

    for section in SECTIONS:
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

            if item.get("required", False):
                worksheet.write_rich_string(
                    row,
                    1,
                    red_star_format,
                    "*",
                    locked_text_format,
                    display_name,
                    locked_text_format,
                )
            else:
                worksheet.write(row, 1, display_name, locked_text_format)

            default_value = item["default"]
            if isinstance(default_value, bool):
                worksheet.write(row, 2, str(default_value), editable_text_format)
            elif isinstance(default_value, (int, float)):
                worksheet.write(row, 2, default_value, editable_number_format)
            else:
                worksheet.write(row, 2, default_value, editable_text_format)

            allowed_text = f"\n{item['allowed']}\n"
            worksheet.write(
                row,
                3,
                allowed_text,
                locked_centered_format,
            )

            description_text = f"\n{item['description']}\n"
            worksheet.write(
                row,
                4,
                description_text,
                locked_description_format,
            )

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

            row += 1

    worksheet.write_comment(
        "C1",
        "Edit only this column. The other columns are locked and are meant as documentation."
    )

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
