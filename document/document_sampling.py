import os
import random

from docx import Document
from docx.enum.section import WD_ORIENTATION
from docx.shared import Cm

from utils import csv_reader


def set_page_style(document):
    if len(document.sections) == 1:
        section = document.sections[0]
        width = section.page_width
        height = section.page_height
        section.orientation = WD_ORIENTATION.LANDSCAPE
        section.page_width = height
        section.page_height = width
        section.top_margin = Cm(1)
        section.bottom_margin = Cm(1)
        section.left_margin = Cm(1)
        section.right_margin = Cm(1)


if __name__ == '__main__':
    size = 2
    from_path = 'C:\\Files\\a1\\'
    check_path = 'C:\\Files\\c\\Completed\\'
    to_path = 'C:\\Files\\e\\'
    from_file_names = set(os.listdir(from_path))
    check_file_names = set(map(lambda x: x[:-5], os.listdir(check_path)))
    content_dict = dict()
    for file_name in from_file_names - check_file_names:
        row = None
        i = 0
        for r in csv_reader(f'{from_path}{file_name}'):
            if i > 0:
                row = r
            i = i + 1
        if row is not None and len(row[5]) > 0:
            content_dict[file_name] = row[5]
    if len(content_dict) < size:
        size = len(content_dict)
    while size > 0:
        for file_name in random.sample(list(content_dict.keys()), size):
            content = content_dict[file_name]
            if len(content) > 1000:
                document = Document()
                set_page_style(document)
                table = document.add_table(rows=1, cols=2)
                table.allow_autofit = False
                for cell in table.columns[0].cells:
                    cell.width = Cm(6)
                table.rows[0].cells[1].text = content_dict[file_name]
                document.save(f'{to_path}{file_name}.docx')
                size = size - 1
