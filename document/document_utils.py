def get_lines(table, column_index):
    lines = None
    cells = table.columns[column_index].cells
    if len(cells) == 1:
        lines = cells[0].text
    return lines
