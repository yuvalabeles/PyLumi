from pathlib import Path

import pandas as pd


def ensure_output_folder(output_folder):
    if output_folder is None:
        raise ValueError(
            "output_folder must be provided explicitly."
        )

    folder_path = Path(output_folder)
    folder_path.mkdir(parents=True, exist_ok=True)

    return folder_path


def save_group_data(
    df,
    filename,
    excel=True,
    col_width=12,
    group_labels=None,
    replicates_per_group=None,
    output_folder=None,
):
    folder_path = ensure_output_folder(output_folder)

    if excel:
        file_path = folder_path / f"{filename}.xlsx"

        col_num = len(df.columns)

        with pd.ExcelWriter(file_path, engine="xlsxwriter") as writer:
            df.to_excel(
                writer,
                index=False,
                sheet_name="Sheet1",
                startrow=1,
            )

            worksheet = writer.sheets["Sheet1"]
            workbook = writer.book

            group_header_format = workbook.add_format({
                "bold": True,
                "align": "center",
                "valign": "vcenter",
                "bg_color": "#E2F5E6",
                "font_color": "black",
            })

            red_text = workbook.add_format({
                "font_color": "#CC0000",
                "align": "center",
                "bold": True,
            })

            d_green_format = workbook.add_format({
                "font_color": "#1B5E20",
                "bold": True,
            })

            green_format = workbook.add_format({
                "bg_color": "#C6EFCE",
            })

            index_format = workbook.add_format({
                "font_color": "#808080",
                "align": "center",
            })

            if group_labels is None:
                raise ValueError(
                    "group_labels must be provided when saving formatted Excel group data."
                )

            if replicates_per_group is None:
                raise ValueError(
                    "replicates_per_group must be provided when saving formatted Excel group data."
                )

            if replicates_per_group <= 0:
                raise ValueError(
                    "replicates_per_group must be greater than 0."
                )

            data_start_col = 2

            visible_cols_per_group = replicates_per_group + 1
            number_of_groups = len(group_labels)
            spaces_between_groups = number_of_groups - 1

            expected_data_cols_with_spaces = (
                number_of_groups * visible_cols_per_group
                + spaces_between_groups
            )

            expected_total_cols = data_start_col + expected_data_cols_with_spaces

            if expected_total_cols > col_num:
                raise ValueError(
                    f"Expected at least {expected_total_cols} columns, "
                    f"but dataframe has only {col_num}. "
                    f"replicates_per_group={replicates_per_group}, "
                    f"group_labels={number_of_groups}."
                )

            worksheet.set_column(0, 0, col_width, red_text)
            worksheet.set_column(1, 1, col_width - 2, index_format)
            worksheet.set_column(2, col_num - 1, col_width)

            for label_id, group_label in enumerate(group_labels):
                group_start_col = (
                    data_start_col
                    + label_id * (visible_cols_per_group + 1)
                )

                group_end_col = group_start_col + visible_cols_per_group - 1
                mean_col = group_end_col

                worksheet.merge_range(
                    0,
                    group_start_col,
                    0,
                    group_end_col,
                    group_label,
                    group_header_format,
                )

                for col in range(group_start_col, group_end_col + 1):
                    value = str(df.columns[col])

                    if col == mean_col:
                        worksheet.write(
                            1,
                            col,
                            value,
                            d_green_format,
                        )

                        worksheet.set_column(
                            col,
                            col,
                            col_width + 2,
                            d_green_format,
                        )

                    else:
                        worksheet.write(
                            1,
                            col,
                            value,
                            green_format,
                        )

    else:
        group_folder = folder_path / "Data (per group)"
        group_folder.mkdir(exist_ok=True)

        file_path = group_folder / f"{filename}.csv"

        df.to_csv(file_path, index=False)


def save_peaks_periods_tables_to_excel(
    tables,
    output_path,
    empty_rows_between_tables=2,
):
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with pd.ExcelWriter(output_path, engine="xlsxwriter") as writer:
        sheet_name = "peaks_periods"
        start_row = 0

        for group_name, table in tables.items():
            table.to_excel(
                writer,
                sheet_name=sheet_name,
                startrow=start_row + 1,
                startcol=0,
                index=False,
            )

            workbook = writer.book
            worksheet = writer.sheets[sheet_name]

            group_format = workbook.add_format({
                "bold": True,
                "font_size": 16,
                "align": "center",
                "valign": "vcenter",
                "border": 1
            })

            first_col_label_format = workbook.add_format({
                "italic": True,
                "border": 1
            })

            centered_format = workbook.add_format({
                "align": "center",
                "valign": "vcenter",
                "left": 1,
                "right": 1
            })

            peak_header_format = workbook.add_format({
                "align": "center",
                "valign": "vcenter",
                "border": 1
            })

            period_header_format = workbook.add_format({
                "bold": True,
                "bg_color": "#F9EEED",
                "align": "center",
                "valign": "vcenter",
                "bottom": 1
            })

            average_period_header_format = workbook.add_format({
                "bold": True,
                "align": "center",
                "valign": "vcenter",
                "bg_color": "#EADCF4",
                "border": 1
            })

            average_fill_format = workbook.add_format({
                "bg_color": "#F2DCDB",
                "align": "center",
                "valign": "vcenter",
                "border": 1
            })

            avg_row_period_format = workbook.add_format({
                "bold": True,
                "bg_color": "#F9EEED",
                "align": "center",
                "valign": "vcenter",
                "border": 1
            })

            period_format = workbook.add_format({
                "bg_color": "#F9EEED",
                "align": "center",
                "valign": "vcenter",
                "top": 1,
                "bottom": 1,
                "top_color": "#D9D9D9",
                "bottom_color": "#D9D9D9",
            })

            average_label_format = workbook.add_format({
                "italic": True,
                "bg_color": "#F2DCDB",
                "border": 1
            })

            average_period_format = workbook.add_format({
                "align": "center",
                "valign": "vcenter",
                "bg_color": "#EADCF4",
                "border": 1
            })

            last_col = len(table.columns)
            worksheet.set_column(0, last_col, 10)

            worksheet.merge_range(
                start_row,
                0,
                start_row,
                last_col,
                group_name,
                group_format,
            )

            header_row = start_row + 1
            first_data_row = start_row + 2
            last_data_row = first_data_row + len(table) - 1

            blank_header_format = workbook.add_format({
                "font_color": "white",
            })

            worksheet.write(
                header_row,
                0,
                "replicate",
                blank_header_format,
            )

            for col_idx, col_name in enumerate(table.columns):
                if col_idx == 0:
                    continue

                if col_name == "average period":
                    worksheet.merge_range(
                        header_row,
                        col_idx,
                        header_row,
                        col_idx + 1,
                        col_name,
                        average_period_header_format,
                    )

                elif str(col_name).startswith("peak"):
                    worksheet.write(header_row, col_idx, col_name, peak_header_format)

                elif str(col_name).startswith("Δ"):
                    worksheet.write(header_row, col_idx, col_name, period_header_format)

                else:
                    worksheet.write(header_row, col_idx, col_name, centered_format)

            for row_offset, (_, row) in enumerate(table.iterrows()):
                excel_row = first_data_row + row_offset
                is_average_row = str(row["replicate"]).lower() == "average"

                for col_idx, col_name in enumerate(table.columns):
                    value = row[col_name]

                    if pd.isna(value):
                        if col_name == "average period":
                            worksheet.merge_range(
                                excel_row,
                                col_idx,
                                excel_row,
                                col_idx + 1,
                                "",
                                average_period_format,
                            )

                        elif col_idx == 0:
                            worksheet.write_blank(excel_row, col_idx, None, first_col_label_format)

                        elif is_average_row:
                            if str(col_name).startswith("Δ"):
                                worksheet.write_blank(excel_row, col_idx, None, avg_row_period_format)
                            else:
                                worksheet.write_blank(excel_row, col_idx, None, average_fill_format)

                        else:
                            if str(col_name).startswith("Δ"):
                                worksheet.write_blank(excel_row, col_idx, None, period_format)
                            else:
                                worksheet.write_blank(excel_row, col_idx, None, centered_format)

                        continue

                    if col_name == "average period":
                        worksheet.merge_range(
                            excel_row,
                            col_idx,
                            excel_row,
                            col_idx + 1,
                            value,
                            average_period_format,
                        )
                        continue

                    if col_idx == 0:
                        if is_average_row:
                            worksheet.write(excel_row, col_idx, value, average_label_format)
                        else:
                            worksheet.write(excel_row, col_idx, value, first_col_label_format)

                    else:
                        if is_average_row:
                            if str(col_name).startswith("Δ"):
                                worksheet.write(excel_row, col_idx, value, avg_row_period_format)
                            else:
                                worksheet.write(excel_row, col_idx, value, average_fill_format)
                        else:
                            if str(col_name).startswith("Δ"):
                                worksheet.write(excel_row, col_idx, value, period_format)
                            else:
                                worksheet.write(excel_row, col_idx, value, centered_format)

            start_row = last_data_row + 1 + empty_rows_between_tables
