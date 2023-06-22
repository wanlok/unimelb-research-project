from document_utils import get_df_list, get_fasttext_mappings

from utils import sort_by_descending_keys, csv_reader

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




def doSomething(df_list):
    header_category_mappings = dict()
    for header, paragraph_categories in csv_reader('M:\\我的雲端硬碟\\UniMelb\\Research Project\\Open Coding\\header_category_mappings.csv', encoding='utf-8-sig'):
        header_category_mappings[header] = set(paragraph_categories.split(','))

    count = 0
    exact_match_count = 0
    not_exact_match_count = 0
    one_match_count = 0
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
                if key in header_category_mappings:
                    header_categories = header_category_mappings[key]
                    if paragraph_categories == header_categories:
                        exact_match = True
                        exact_match_count = exact_match_count + 1
                    else:
                        exact_match = False
                        not_exact_match_count = not_exact_match_count + 1
                    if len(paragraph_categories.intersection(header_categories)) == 1:
                        one_match = True
                        one_match_count = one_match_count + 1
                    else:
                        one_match = False
                    print(f'{count} {file_name} {header} {paragraph_categories} {header_categories} {exact_match} {one_match}')
                else:
                    not_exact_match_count = not_exact_match_count + 1
                    print(f'{count} {file_name} {header} {paragraph_categories} {{}} False False')
    print(f'EXACT MATCH     : {exact_match_count} / {count} = {exact_match_count / count}')
    print(f'ONE MATCH       : {one_match_count} / {count} = {one_match_count / count}')
    print(f'NOT EXACT MATCH : {not_exact_match_count} / {count} = {not_exact_match_count / count}')







if __name__ == '__main__':
    df_list = get_df_list()
    # category_distribution(df_list)
    # print()
    doSomething(df_list)

    # print()
    # header_document_distribution(df_list)
    # print()
    # paragraph_document_distribution(document_contents)
    # print()
    # code_document_distribution(df_list)
    # print()
    # distinct_code_header_distribution(document_contents)
    # distinct_header_distribution(document_contents)




