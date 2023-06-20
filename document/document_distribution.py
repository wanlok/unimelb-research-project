import os
from functools import reduce

from docx import Document
from numpy import ndarray

from document_utils import get_lines, get_type_1_header, get_type_2_header, get_df_list, directory_paths

from utils import sort_by_descending_keys


def get_file_name(df):
    file_name = None
    names = df['name'].tolist()
    if len(names) > 0:
        file_name = names[0]
    return file_name


def category_distribution(df_list):
    my_dict = dict()
    for df in df_list:
        file_name = get_file_name(df)
        categories = set()
        for labels in df['labels'].tolist():
            categories.update(set(map(lambda x: x.replace('__label__', ''), labels.split(' '))))
        for category in categories:
            if category in my_dict:
                my_dict[category].add(file_name)
            else:
                my_dict[category] = {file_name}
    for category in my_dict:
        print(f'{category} {my_dict[category]}')


def dummy_dummy(distribution_dict, name):
    for key in sort_by_descending_keys(distribution_dict):
        value = distribution_dict[key]
        print(f'{name}: {key}, FILES: {len(value)} {value}')


def append(dict, key, value):
    if key in dict:
        dict[key].append(value)
    else:
        dict[key] = [value]


def header_document_distribution(df_list):
    header_dict = dict()
    paragraph_dict = dict()
    for df in df_list:
        file_name = get_file_name(df)
        append(header_dict, len(set(df['headers'].tolist())), file_name)
        append(paragraph_dict, len(set(df['paragraph'].tolist())), file_name)
    dummy_dummy(header_dict, 'HEADERS')
    print()
    dummy_dummy(paragraph_dict, 'PARAGRAPHS')


def code_document_distribution(df_list):
    distribution_dict = dict()
    for df in df_list:
        file_name = get_file_name(df)
        document_headers = df['headers'].tolist()
        document_categories = df['labels'].tolist()
        # file_name, document_headers, _, document_categories = document_content
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
        print(f'VALIDATING: {document_category_dict}')
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
#
#
# def distinct_code_header_distribution(document_contents):
#     distribution_dict = dict()
#     for document_content in document_contents:
#         file_name, document_headers, _, document_categories = document_content
#         document_category_dict = dict()
#         for i in range(len(document_headers)):
#             key = document_headers[i]
#             if i < len(document_categories):
#                 value = set(document_categories[i])
#             else:
#                 value = set()
#             if key in document_category_dict:
#                 document_category_dict[key] = document_category_dict[key].union(value)
#             else:
#                 document_category_dict[key] = value
#         for key in document_category_dict:
#             size = len(document_category_dict[key])
#             value = f'{file_name}|{key}'
#             if size in distribution_dict:
#                 distribution_dict[size].append(value)
#             else:
#                 distribution_dict[size] = [value]
#     for key in sort_by_descending_keys(distribution_dict):
#         value = distribution_dict[key]
#         print(f'CODES: {key}, SECTIONS: {len(value)}, FILES: {value}')


# def distinct_header_distribution(document_contents):
    # header_dict = dict()
    # for i in range(len(document_contents)):
    #     document_content = document_contents[i]
    #     file_name, document_headers, _, _ = document_content
    #     for header in document_headers:
    #         if len(header) == 0:
    #             continue
    #         header = header.lower()
    #         if header in header_dict:
    #             header_dict[header].add(file_name)
    #         else:
    #             header_dict[header] = {file_name}
    # for header in header_dict:
    #     print(f'"{header}",{len(header_dict[header])}')








if __name__ == '__main__':
    df_list = get_df_list(directory_paths)
    category_distribution(df_list)
    print()
    header_document_distribution(df_list)
    # print()
    # paragraph_document_distribution(document_contents)
    # print()
    # code_document_distribution(df_list)
    # print()
    # distinct_code_header_distribution(document_contents)
    # distinct_header_distribution(document_contents)




