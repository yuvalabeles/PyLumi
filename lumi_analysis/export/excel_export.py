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
    output_folder=None,
):
    folder_path = ensure_output_folder(output_folder)

    # Save dataframe as Excel.
    if excel:
        file_path = folder_path / f"{filename}.xlsx"

        col_num = len(list(df.columns))

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

            # Set column widths.
            worksheet.set_column(0, 0, col_width, red_text)
            worksheet.set_column(1, 1, col_width - 2, index_format)
            worksheet.set_column(2, col_num, col_width)

            col_cnt = 0
            label_id = 0

            for col in range(2, col_num):
                if col_cnt == 5:
                    value = str(df.columns[col])

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

                    # Merge every 5 columns in first row.
                    worksheet.merge_range(
                        0,
                        col - 5,
                        0,
                        col,
                        group_labels[label_id],
                        group_header_format,
                    )

                    label_id += 1

                elif col_cnt == 6:
                    col_cnt = 0
                    continue

                else:
                    value = str(df.columns[col])

                    worksheet.write(
                        1,
                        col,
                        value,
                        green_format,
                    )

                col_cnt += 1

    # Save dataframe as CSV.
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
    # Save all group peak tables into one Excel sheet, one below the other.
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
            })

            peak_header_format = workbook.add_format({
                "bold": True,
                "align": "center",
                "valign": "vcenter",
                "border": 1
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

            average_peak_format = workbook.add_format({
                "bold": True,
                "bg_color": "#F2DCDB",
                "align": "center",
                "valign": "vcenter",
                "border": 1
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

            # Column width = 10 for all used columns
            last_col = len(table.columns)
            worksheet.set_column(0, last_col, 10)

            # Group name merged across the table width
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

            # Color "replicate" header in white
            blank_header_format = workbook.add_format({
                "font_color": "white",
            })

            worksheet.write(
                header_row,
                0,
                "replicate",
                blank_header_format,
            )

            # Format headers
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

                else:
                    worksheet.write(header_row, col_idx, col_name, centered_format)

            # Format table body
            for row_offset, (_, row) in enumerate(table.iterrows()):
                excel_row = first_data_row + row_offset
                is_average_row = str(row["replicate"]).lower() == "average"

                for col_idx, col_name in enumerate(table.columns):
                    value = row[col_name]

                    if pd.isna(value):
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
                            if str(col_name).startswith("peak"):
                                worksheet.write(excel_row, col_idx, value, average_peak_format)
                            else:
                                worksheet.write(excel_row, col_idx, value, average_fill_format)
                        else:
                            worksheet.write(excel_row, col_idx, value, centered_format)

            # Move to next table:
            # group title row + header row + data rows + empty rows
            start_row = last_data_row + 1 + empty_rows_between_tables
