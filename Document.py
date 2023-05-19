import os

from docx import Document
from docx.enum.section import WD_ORIENTATION
from docx.enum.text import WD_BREAK
from docx.shared import Cm


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


def prepare_documents_for_manual_categorisation():
    directory_path = 'C:\\Files\\b\\'
    write_directory_path = 'C:\\Files\\c\\'
    for file_name in os.listdir(directory_path):
        document = Document()
        set_page_style(document)
        table = document.add_table(rows=1, cols=2)
        table.allow_autofit = False
        for cell in table.columns[0].cells:
            cell.width = Cm(6)
        text = ''
        for line in open(f'{directory_path}{file_name}', encoding='utf-8').readlines():
            text = text + line
        table.rows[0].cells[1].text = text
        document.save(f'{write_directory_path}{file_name}.docx')


if __name__ == '__main__':
    prepare_documents_for_manual_categorisation()