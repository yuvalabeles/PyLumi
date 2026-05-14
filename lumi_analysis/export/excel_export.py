import os
from datetime import datetime

import pandas as pd

FOLDER_NAME = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")


def save_tissue_data(df, filename, excel=True, col_width=12, tissue_labels=None, folder_name=None):
    if folder_name is None:
        folder_name = FOLDER_NAME

    # Create a folder for the files:
    os.makedirs(folder_name, exist_ok=True)

    # Save the dataframes into that folder:
    if excel:
        p = folder_name + "/" + filename
        col_num = len(list(df.columns))

        with pd.ExcelWriter(p + ".xlsx", engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Sheet1', startrow=1)

            worksheet = writer.sheets['Sheet1']
            workbook = writer.book

            group_header_format = workbook.add_format(
                {"bold": True, "align": "center", "valign": "vcenter", 'bg_color': '#E2F5E6', 'font_color': 'black'})

            red_text = workbook.add_format({'font_color': '#CC0000', "align": "center", "bold": True})
            d_green_format = workbook.add_format({'font_color': '#1B5E20', "bold": True})
            green_format = workbook.add_format({'bg_color': '#C6EFCE'})
            index_format = workbook.add_format({'font_color': '#808080', "align": "center"})

            # set column width
            worksheet.set_column(0, 0, col_width, red_text)
            worksheet.set_column(1, 1, col_width - 2, index_format)
            worksheet.set_column(2, col_num, col_width)

            col_cnt = 0
            label_id = 0
            for col in range(2, col_num):
                if col_cnt == 5:
                    value = str(df.columns[col])
                    worksheet.write(1, col, value, d_green_format)
                    worksheet.set_column(col, col, col_width + 2, d_green_format)

                    # Merge every 5 columns in first row
                    worksheet.merge_range(0, col - 5, 0, col, tissue_labels[label_id], group_header_format)
                    label_id += 1
                elif col_cnt == 6:
                    col_cnt = 0
                    continue
                else:
                    value = str(df.columns[col])
                    worksheet.write(1, col, value, green_format)
                col_cnt += 1
    else:
        os.makedirs(folder_name + "/Data (per tissue)", exist_ok=True)
        p = folder_name + "/Data (per tissue)/" + filename
        df.to_csv(p + ".csv", index=False)


def write_peaks_to_excel(df, table_title, writer, worksheet, start_row, decimals=2, gap_rows=3):
    workbook = writer.book

    title_fmt = workbook.add_format({
        "bold": True,
        "align": "center",
        "valign": "vcenter",
        "border": 1,
        "bg_color": "#D9EAD3",
        "font_size": 13
    })

    peaks_fmt = workbook.add_format({
        "bold": True,
        "align": "center",
        "valign": "vcenter",
        "border": 1,
        "bg_color": "#EADCF8"
    })

    periods_fmt = workbook.add_format({
        "bold": True,
        "align": "center",
        "valign": "vcenter",
        "border": 1,
        "bg_color": "#C7A1ED"
    })

    subheader_fmt = workbook.add_format({
        "bold": True,
        "align": "center",
        "valign": "vcenter",
        "border": 1,
        "bg_color": "#F3F3F3",
        "font_size": 8
    })

    index_fmt = workbook.add_format({
        "bold": True,
        "align": "center",
        "valign": "vcenter",
        "border": 1
    })

    cell_fmt = workbook.add_format({
        "align": "center",
        "valign": "vcenter",
        "border": 1,
        "font_size": 10
    })

    # Create expanded columns
    expanded_parts = []
    group_sizes = {}

    for col in df.columns:
        max_len = df[col].apply(
            lambda x: len(x) if isinstance(x, (list, tuple)) else 1
        ).max()

        group_sizes[col] = max_len
        expanded_col = pd.DataFrame(index=df.index)

        for i in range(max_len):
            expanded_col[(col, i + 1)] = df[col].apply(
                lambda x: x[i] if isinstance(x, (list, tuple)) and i < len(x) else ""
            )

        expanded_parts.append(expanded_col)

    df_excel = pd.concat(expanded_parts, axis=1)

    # Title cell over the index-header area
    worksheet.merge_range(start_row, 0, start_row + 1, 0, table_title, title_fmt)

    # Master headers + subheaders
    col_idx = 1
    peaks = True

    for master_label, size in group_sizes.items():
        first_col = col_idx
        last_col = col_idx + size - 1

        if peaks:
            sub_h = "peak"
            master_fmt = peaks_fmt
        else:
            sub_h = "period"
            master_fmt = periods_fmt
        peaks = not peaks

        worksheet.merge_range(start_row, first_col, start_row, last_col, master_label, master_fmt)

        for sub_i in range(size):
            worksheet.write(start_row + 1, first_col + sub_i, sub_h + str(sub_i + 1), subheader_fmt)

        col_idx += size

    # Data rows
    for row_i, index_label in enumerate(df_excel.index):
        excel_row = start_row + 2 + row_i

        worksheet.write(excel_row, 0, index_label.lower(), index_fmt)

        for col_i, value in enumerate(df_excel.loc[index_label]):
            if isinstance(value, (int, float)):
                value = round(value, decimals)

            worksheet.write(excel_row, col_i + 1, value, cell_fmt)

    # Sizing
    worksheet.set_column(0, 0, 18)
    worksheet.set_column(1, len(df_excel.columns), 12)

    end_row = start_row + 2 + len(df_excel.index)

    for r in range(end_row, end_row + gap_rows):
        worksheet.set_row(r, 15)

    return end_row + gap_rows
