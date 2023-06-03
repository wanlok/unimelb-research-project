import os

from docx import Document

from document_utils import get_lines, get_type_1_header, get_type_2_header, get_document_contents

from utils import sort_by_descending_keys


def category_distribution(directory_path):
    my_dict = dict()
    for file_name in os.listdir(directory_path):
        f = open(f'{directory_path}{file_name}', 'rb')
        document = Document(f)
        tables = document.tables
        if len(tables) == 1:
            columns = tables[0].columns
            if len(columns) == 2:
                cells = tables[0].columns[0].cells
                if len(cells) == 1:
                    for key in cells[0].text.split('\n'):
                        if len(key) > 0:
                            if key in my_dict:
                                my_dict[key].add(file_name)
                                # my_dict[key] = my_dict[key] + 1
                            else:
                                my_set = set()
                                my_set.add(file_name)
                                my_dict[key] = my_set
                                # my_dict[key] = 1
        f.close()
    for key in my_dict:
        print(f'\"{key}\",{my_dict[key]}')
        # print(f'\"{key}\",{len(my_dict[key])}')


def header_document_distribution(document_contents):
    distribution_dict = dict()
    for document_content in document_contents:
        file_name, document_headers, _, _ = document_content
        key = len(set(document_headers))
        if key in distribution_dict:
            distribution_dict[key].append(file_name)
        else:
            distribution_dict[key] = [file_name]
    for key in sort_by_descending_keys(distribution_dict):
        value = distribution_dict[key]
        print(f'HEADERS: {key}, FILES: {len(value)} {value}')


def paragraph_document_distribution(document_contents):
    distribution_dict = dict()
    for document_content in document_contents:
        file_name, _, document_paragraphs, _ = document_content
        key = len(document_paragraphs)
        if key in distribution_dict:
            distribution_dict[key].append(file_name)
        else:
            distribution_dict[key] = [file_name]
    for key in sort_by_descending_keys(distribution_dict):
        value = distribution_dict[key]
        print(f'PARAGRAPHS: {key}, FILES: {len(value)} {value}')


def code_document_distribution(document_contents):
    distribution_dict = dict()
    for document_content in document_contents:
        file_name, document_headers, _, document_categories = document_content
        document_category_dict = dict()
        for i in range(len(document_headers)):
            key = document_headers[i]
            if i < len(document_categories):
                value = set(document_categories[i])
            else:
                value = set()
            if key in document_category_dict:
                document_category_dict[key] = document_category_dict[key].union(value)
            else:
                document_category_dict[key] = value
        size = 0
        for key in document_category_dict:
            size = size + len(document_category_dict[key])
        if size in distribution_dict:
            distribution_dict[size].append(file_name)
        else:
            distribution_dict[size] = [file_name]
    for key in sort_by_descending_keys(distribution_dict):
        value = distribution_dict[key]
        print(f'CODES: {key}, FILES: {len(value)} {value}')


def distinct_code_header_distribution(document_contents):
    distribution_dict = dict()
    for document_content in document_contents:
        file_name, document_headers, _, document_categories = document_content
        document_category_dict = dict()
        for i in range(len(document_headers)):
            key = document_headers[i]
            if i < len(document_categories):
                value = set(document_categories[i])
            else:
                value = set()
            if key in document_category_dict:
                document_category_dict[key] = document_category_dict[key].union(value)
            else:
                document_category_dict[key] = value
        for key in document_category_dict:
            size = len(document_category_dict[key])
            value = f'{file_name}|{key}'
            if size in distribution_dict:
                distribution_dict[size].append(value)
            else:
                distribution_dict[size] = [value]
    for key in sort_by_descending_keys(distribution_dict):
        value = distribution_dict[key]
        print(f'CODES: {key}, SECTIONS: {len(value)}, FILES: {value}')


if __name__ == '__main__':
    directory_path = 'C:\Files\\c\\Completed\\'
    # directory_path = 'C:\Files\\d\\'

    document_contents = get_document_contents(directory_path)
    category_distribution(directory_path)
    print()
    header_document_distribution(document_contents)
    print()
    paragraph_document_distribution(document_contents)
    print()
    code_document_distribution(document_contents)
    print()
    distinct_code_header_distribution(document_contents)




