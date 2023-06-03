import os

from docx import Document


def get_lines(table, column_index):
    lines = None
    cells = table.columns[column_index].cells
    if len(cells) == 1:
        lines = cells[0].text
    return lines


def get_type_1_header(line, dummy):
    header = None
    if len(set([*line])) == 1 and ('-' in line[:4] or '=' in line[:4]):
        header = ' '.join(dummy)
    return header


def get_type_2_header(line):
    header = None
    if line[:6] == '######':
        header = line[6:]
    elif line[:5] == '#####':
        header = line[5:]
    elif line[:4] == '####':
        header = line[4:]
    elif line[:3] == '###':
        header = line[3:]
    elif line[:2] == '##':
        header = line[2:]
    elif line[:1] == '#':
        header = line[1:]
    if header is not None:
        header = header.strip()
    return header


def get_document_contents(directory_path):
    document_contents = []
    for file_name in os.listdir(directory_path):
        f = open(f'{directory_path}{file_name}', 'rb')
        tables = Document(f).tables
        if len(tables) == 1:
            table = tables[0]

            document_headers = []
            document_paragraphs = []
            document_categories = []

            categories = []
            for line in get_lines(table, 0).split('\n'):
                if len(line) > 0:
                    categories.append(line)
                elif len(categories) > 0:
                    document_categories.append(categories)
                    categories = []
            if len(categories) > 0:
                document_categories.append(categories)

            header_lines = []
            previous_header = ''
            paragraph = []
            for line in get_lines(table, 1).split('\n'):
                header = get_type_1_header(line, header_lines)
                if header is not None:
                    header_lines.clear()
                    paragraph.clear()
                else:
                    header_lines.append(line)
                    header = get_type_2_header(line)
                if len(line) == 0:
                    header_lines.clear()
                if header is None:
                    if len(line) > 0:
                        paragraph.append(line)
                    elif len(paragraph) > 0:
                        document_headers.append(previous_header)
                        document_paragraphs.append(' '.join(map(lambda x: x.strip(), paragraph)))
                        paragraph.clear()
                if header is not None:
                    previous_header = header
            if len(paragraph) > 0:
                document_headers.append(previous_header)
                document_paragraphs.append(' '.join(map(lambda x: x.strip(), paragraph)))

            # print(file_name)
            # print(document_headers)
            # print(document_paragraphs)
            # print(document_categories)

            document_contents.append((file_name, document_headers, document_paragraphs, document_categories))
    return document_contents


if __name__ == '__main__':
    document_contents = get_document_contents('C:\\Files\\Samples 20230601\\')
    for document_content in document_contents:
        file_name, document_headers, document_paragraphs, document_categories = document_content
        for category in document_categories:
            print(category)
            # print(file_name.replace('.csv.docx', '').replace('_', '/'))
            # print(paragraph)