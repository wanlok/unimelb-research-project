import os

from docx import Document


def get_lines(table, column_index):
    lines = None
    cells = table.columns[column_index].cells
    if len(cells) == 1:
        lines = cells[0].text
    return lines


if __name__ == '__main__':
    file_names = []
    directory_path = 'C:\\Files\\c\\Completed\\'
    text = 'Vulnerability type'
    for file_name in os.listdir(directory_path):
        f = open(f'{directory_path}{file_name}', 'rb')
        document = Document(f)
        tables = document.tables
        if len(tables) == 1:
            if text in get_lines(tables[0], 0):
                print(file_name)
