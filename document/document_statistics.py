from collections import Counter

from document_utils import get_df_list, get_fasttext_mappings
from dummy import get_header_paragraph_dict

from utils import sort_by_descending_keys, csv_reader, repos, sort_by_descending_values

fasttext_mappings = get_fasttext_mappings()


def get_file_name(df):
    file_name = None
    names = df['name'].tolist()
    if len(names) > 0:
        file_name = names[0]
    return file_name


def category_distribution(df_list):
    distribution_dict = dict()
    for df in df_list:
        file_name = get_file_name(df)
        categories = set()
        for labels in df['labels'].tolist():
            categories.update(labels.split(' '))
        for category in categories:
            if category in distribution_dict:
                distribution_dict[category].add(file_name)
            else:
                distribution_dict[category] = {file_name}
    for category in distribution_dict:
        print(f'{fasttext_mappings[category]} {distribution_dict[category]}')


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


def get_header_category_dict():
    header_category_dict = dict()
    file_path = 'M:\\我的雲端硬碟\\UniMelb\\Research Project\\Open Coding\\header_category_mappings.csv'
    for header, paragraph_categories in csv_reader(file_path, encoding='utf-8-sig'):
        header_category_dict[header] = set(filter(lambda x: len(x) > 0, paragraph_categories.split(',')))
    return header_category_dict


def get_header_paragraph_category_statistics(df_list):
    count_dict = dict()
    count = 0
    header_category_dict = get_header_category_dict()
    for df in df_list:
        file_dict = dict()
        file_name = list(set(df['name'].tolist()))[0]
        previous_header = None
        category_set = set()
        categories = map(lambda x: list(map(lambda y: fasttext_mappings[y], x.split(' '))), df['labels'].tolist())
        for header, paragraph_categories in zip(df['headers'].tolist(), categories):
            if previous_header is not None and header != previous_header:
                if file_name in file_dict:
                    file_dict[file_name].append((previous_header, category_set))
                else:
                    file_dict[file_name] = [(previous_header, category_set)]
                category_set = set()
            for category in paragraph_categories:
                category_set.add(category)
            previous_header = header
        if len(category_set) > 0:
            if file_name in file_dict:
                file_dict[file_name].append((previous_header, category_set))
            else:
                file_dict[file_name] = [(previous_header, category_set)]
        for file_name in file_dict:
            for header, paragraph_categories in file_dict[file_name]:
                count = count + 1
                key = header.replace('\xa0', ' ').lower()
                if key in header_category_dict:
                    header_categories = header_category_dict[key]
                else:
                    header_categories = set()
                key = len(paragraph_categories.intersection(header_categories))
                if key in count_dict:
                    count_dict[key] = count_dict[key] + 1
                else:
                    count_dict[key] = 1
                # print(f'{count} {file_name} {header} {paragraph_categories} {header_categories} {key}')
    for key in count_dict:
        print(f'{key} {count_dict[key]}')





def get_top_ten_headers():
    header_dict = dict()
    for a in repos(get_header_paragraph_dict):
        headers = a[1].keys()
        for header in headers:
            if header in header_dict:
                header_dict[header] = header_dict[header] + 1
            else:
                header_dict[header] = 1
    header_dict = sort_by_descending_values(header_dict)
    i = 0
    for header in header_dict:
        print(f'"{header}",{header_dict[header]}')



def hello_world():
    print('Hello World')
    aaa = repos(get_header_paragraph_dict)
    header_dict = dict()
    total = 0
    num = 0
    for a in aaa:
        # print(a)
        repo = a[0]
        headers = a[1].keys()
        for header in headers:
            if header == 'security policy':
                num = num + 1
                number_of_paragraphs = len(a[1][header])
                print(f'{repo} {header} {number_of_paragraphs}')
                total = total + number_of_paragraphs
            # if header in header_dict:
            #     header_dict[header] = header_dict[header] + 1
            # else:
            #     header_dict[header] = 1
    print(f'{total} {num}')
    # header_dict = sort_by_descending_values(header_dict)
    # for header in header_dict:
    #     print(f'{header} {header_dict[header]}')





def get_security_policy_location(repo):
    file_name = repo.replace('/', '_')
    file_name = f'{file_name}.csv'
    file_path = f'C:\\Files\\security policies\\{file_name}'
    a = None
    i = 0
    for row in csv_reader(file_path):
        if i > 0:
            a = (repo.lower(), row[0].lower(),row[1].lower())
        i = i + 1
    if a[0] != a[1]:
        b = 'parent .github'
    else:
        if a[2] == '.github/security.md':
            b = '\'.github\' directory'
        elif a[2] == 'docs/security.md':
            b = '\'docs\' directory'
        else:
            b = 'root directory'
    return b





if __name__ == '__main__':
    # df_list = get_df_list()
    # category_distribution(df_list)
    # print()
    # get_header_paragraph_category_statistics(df_list)

    # print()
    # header_document_distribution(df_list)
    # print()
    # paragraph_document_distribution(document_contents)
    # print()
    # code_document_distribution(df_list)
    # print()
    # distinct_code_header_distribution(document_contents)
    # distinct_header_distribution(document_contents)

    get_top_ten_headers()
    # hello_world()
    # aaa = repos(get_security_policy_location)
    # print(Counter(aaa))


