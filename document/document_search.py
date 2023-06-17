import os

from docx import Document

from document_utils import get_lines, directory_paths

if __name__ == '__main__':
    # text = 'take the security of our software products and services seriously'
    # text = 'consider vulnerabilities leading to the compromise'
    # text = 'threat model'
    # text = 'process is to reduce the total time users are vulnerable to publicly known exploits'
    text = 'member'
    column = 1
    ignored_files = ['desktop.ini', 'Completed']
    i = 0
    for directory_path in directory_paths:
        for file_name in os.listdir(directory_path):
            if file_name not in ignored_files:
                f = open(f'{directory_path}{file_name}', 'rb')
                document = Document(f)
                tables = document.tables
                if len(tables) == 1:
                    if text.lower() in get_lines(tables[0], column).lower():
                        i = i + 1
                        print(f'{i} {directory_path}{file_name}')

