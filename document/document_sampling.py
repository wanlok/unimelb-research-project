import os
import random
from functools import reduce

from docx import Document
from docx.enum.section import WD_ORIENTATION
from docx.shared import Cm

from document.document_utils import get_document_contents
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


def dummy():
    existing_paths = [
        'M:\\我的雲端硬碟\\UniMelb\\Research Project\\Open Coding\\20230522\\',
        'M:\\我的雲端硬碟\\UniMelb\\Research Project\\Open Coding\\20230606\\',
        'M:\\我的雲端硬碟\\UniMelb\\Research Project\\Open Coding\\20230606-1\\'
    ]
    existing_file_names = reduce(lambda a, b: a.union(b), map(lambda directory_path: set(
        map(lambda file_name: file_name, os.listdir(directory_path))), existing_paths))

    file_names = set(os.listdir('M:\\我的雲端硬碟\\UniMelb\\Research Project\\Open Coding\\Combined\\'))
    # print(file_names)
    print(file_names - existing_file_names)

if __name__ == '__main__':
    size = 1
    from_path = 'C:\\Files\\a1\\'
    existing_paths = [
        'M:\\我的雲端硬碟\\UniMelb\\Research Project\\Open Coding\\20230522\\',
        'M:\\我的雲端硬碟\\UniMelb\\Research Project\\Open Coding\\20230601\\',
        'M:\\我的雲端硬碟\\UniMelb\\Research Project\\Open Coding\\20230606\\',
        'M:\\我的雲端硬碟\\UniMelb\\Research Project\\Open Coding\\20230607\\',
        'M:\\我的雲端硬碟\\UniMelb\\Research Project\\Open Coding\\20230608\\',
        'M:\\我的雲端硬碟\\UniMelb\\Research Project\\Open Coding\\20230609\\',
        'M:\\我的雲端硬碟\\UniMelb\\Research Project\\Open Coding\\20230610\\Completed\\'
    ]
    to_path = 'M:\\我的雲端硬碟\\UniMelb\\Research Project\\Open Coding\\20230610\\'
    from_file_names = set(os.listdir(from_path))
    if len(existing_paths) > 0:
        existing_file_names = reduce(lambda a, b: a.union(b), map(lambda directory_path: set(map(lambda file_name: file_name[:-5], os.listdir(directory_path))), existing_paths))
        dummy = list(existing_file_names)
        for i in range(len(dummy)):
            print(f'{i} {dummy[i]}')
    else:
        existing_file_names = set()
    content_dict = dict()
    for file_name in from_file_names - existing_file_names:
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
            if len(content) >= 1000:
                document = Document()
                set_page_style(document)
                table = document.add_table(rows=1, cols=2)
                table.allow_autofit = False
                for cell in table.columns[0].cells:
                    cell.width = Cm(6)
                table.rows[0].cells[1].text = content_dict[file_name]
                document.save(f'{to_path}{file_name}.docx')
                size = size - 1
