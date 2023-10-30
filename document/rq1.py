import os

import pandas as pd
from mlxtend.frequent_patterns import apriori, association_rules

from document.document_sampling import get_remaining_and_categorised_file_paths
from document.document_utils import category_names, get_headers_and_paragraphs, directory_paths, get_docx_file_tuple, \
    get_csv_file_tuple
from utils import csv_reader, sort_by_descending_values, get_latest_content, repos

csv_file_path_1 = 'C:\\Files\\Projects\\Header Categorisation.csv'
csv_file_path_2 = 'C:\\Files\\Projects\\Additional Header Categorisation.csv'


def get_header_categorisations(csv_file_path, index):
    my_dict = dict()
    for row in csv_reader(csv_file_path):
        categories = list(filter(lambda x: len(x) > 0, row[index].split(',')))
        my_dict[row[0]] = categories
    return my_dict


def print_header_categorisation():
    header_categorisations = get_header_categorisations(csv_file_path_1, 2)
    additional_header_categorisations = get_header_categorisations(csv_file_path_2, 1)
    count = 0
    total = 0
    # for header in header_categorisations:
    #     if len(header_categorisations[header]) == 0 and header in additional_header_categorisations:
    #         header_categorisations[header] = additional_header_categorisations[header]
    for header in header_categorisations:
        total = total + 1
        if len(header_categorisations[header]) == 0:
            count = count + 1
    category_dict = dict()
    total = 0
    for header in header_categorisations:
        categories = header_categorisations[header]
        if len(categories) > 0:
            total = total + 1
            for category in categories:
                # print(f'"{header}","{category}"')
                if category == 'Reporting proceture':
                    category = 'Reporting procedure'
                elif category == 'Secure communnication':
                    category = 'Secure communication'
                if category in category_dict:
                    category_dict[category] = category_dict[category] + 1
                else:
                    category_dict[category] = 1
            if total == 117:
                break
    for category in category_dict:
        print(f'"{category}",{category_dict[category]},{category_dict[category] / 118}')


def get_manual_repos():
    repo_set = set()
    csv_file_path = 'W:\\My Drive\\UniMelb\\Research Project\\Datasets\\Manual classification.csv'
    for row in csv_reader(csv_file_path):
        repo = row[0].replace('.docx', '').replace('.csv', '').replace('_', '/', 1)
        repo_set.add(repo)
    return list(repo_set)



open_coding_repo_list = ['Automattic/jetpack', 'bitwarden/desktop', 'cortexproject/cortex', 'exim/exim', 'imagemagick/imagemagick6', 'libexif/exif', 'nextauthjs/next-auth', 'odoo/odoo', 'rabbitmq/rabbitmq-jms-client', 'rapidsai/cudf']


def get_semi_automatic_repo_category_dict(manual_repo_filtered):
    i = 0
    repo_category_dict = dict()
    manual_repos = get_manual_repos()
    csv_file_path = 'C:\\Users\\Robert Wan\\Desktop\\Attributes.csv'
    for row in csv_reader(csv_file_path):
        i = i + 1
        if i > 2:
            repo = row[0]
            if manual_repo_filtered and repo in manual_repos:
                continue
            categories = []
            category_dict = eval(row[2])
            for category in category_dict:
                for _ in range(category_dict[category]):
                    categories.append(category)
            repo_category_dict[repo] = categories
    return repo_category_dict


def get_manual_repo_category_dict():
    csv_file_path = 'W:\\My Drive\\UniMelb\\Research Project\\Datasets\\Manual classification.csv'
    repo_category_dict = dict()
    category_dict = dict()
    for row in csv_reader(csv_file_path):
        repo = row[0].replace('.docx', '').replace('.csv', '').replace('_', '/', 1)
        # if open_coding_filtered and repo not in open_coding_repo_list:
        #     continue
        category = row[1]
        if repo in repo_category_dict:
            repo_category_dict[repo].append(category)
        else:
            repo_category_dict[repo] = [category]
    return repo_category_dict


def get_repo_count_and_category_dict(repo_category_dict, deduplicated):
    category_dict = dict()
    for repo in repo_category_dict:
        categories = repo_category_dict[repo]
        for category in categories:
            if category in category_dict:
                category_dict[category].append(repo)
            else:
                category_dict[category] = [repo]
    for category in category_dict:
        if deduplicated:
            category_dict[category] = len(set(category_dict[category]))
        else:
            category_dict[category] = len(category_dict[category])
    order_list = list(filter(lambda x: len(x) > 0, sort_by_descending_values(category_dict).keys()))
    return len(repo_category_dict), category_dict, order_list


def print_results():
    manual_repo_category_dict = get_manual_repo_category_dict()
    semi_automatic_repo_category_dict = get_semi_automatic_repo_category_dict(True)
    print(f'CHECK: {len(manual_repo_category_dict)} {len(semi_automatic_repo_category_dict)}')
    repo_count_1, category_dict_1, order_list_1 = get_repo_count_and_category_dict(manual_repo_category_dict, True)
    repo_count_2, category_dict_2, order_list_2 = get_repo_count_and_category_dict(manual_repo_category_dict, False)
    repo_count_3, category_dict_3, order_list_3 = get_repo_count_and_category_dict(semi_automatic_repo_category_dict, True)
    repo_count_4, category_dict_4, order_list_4 = get_repo_count_and_category_dict(semi_automatic_repo_category_dict, False)
    for category in category_names:
        col_1 = category
        col_2 = category_dict_1[category]
        col_3 = category_dict_1[category] / repo_count_1
        col_4 = category_dict_2[category]
        col_5 = category_dict_2[category] / repo_count_2
        col_6 = category_dict_3[category]
        col_7 = category_dict_3[category] / repo_count_3
        col_8 = category_dict_4[category]
        col_9 = category_dict_4[category] / repo_count_4
        print(f'{col_1},{col_2},{col_3},,{col_4},{col_5},,{col_6},{col_7},,{col_8},{col_9}')
    for i in range(len(order_list_1)):
        col_1 = order_list_1[i]
        col_2 = order_list_2[i]
        col_3 = order_list_3[i]
        col_4 = order_list_4[i]
        print(f'"{col_1}","{col_2}","{col_3}","{col_4}"')


def print_distribution_dict(distribution_dict):
    counts = list(distribution_dict.keys())
    counts.sort()
    for count in counts:
        print(f'{count},{distribution_dict[count]}')


def print_number_of_categories_per_header_paragraph_pairs():
    distribution_dict = dict()
    header_paragraph_pair_categorisations = get_header_paragraph_pair_categorisations()
    for categorisation in header_paragraph_pair_categorisations:
        count = len(categorisation)
        if count in distribution_dict:
            distribution_dict[count] = distribution_dict[count] + 1
        else:
            distribution_dict[count] = 1
    print_distribution_dict(distribution_dict)

    distribution_dict = dict()
    header_categorisations = get_header_categorisations(csv_file_path_1, 2)
    total = 0
    for header in header_categorisations:
        categorisation = header_categorisations[header]
        if len(categorisation) > 0:
            total = total + 1
            for i in range(len(categorisation)):
                category = categorisation[i]
                if category == 'Reporting proceture':
                    category = 'Reporting procedure'
                elif category == 'Secure communnication':
                    category = 'Secure communication'
                categorisation[i] = category
                count = len(categorisation)
                if count in distribution_dict:
                    distribution_dict[count] = distribution_dict[count] + 1
                else:
                    distribution_dict[count] = 1
            if total == 117:
                break
    print_distribution_dict(distribution_dict)



def get_file_names():
    file_names = []
    directory_paths = [
        'W:\\My Drive\\UniMelb\\Research Project\\Open Coding\\20230522\\',
        'W:\\My Drive\\UniMelb\\Research Project\\Open Coding\\20230601\\',
        'W:\\My Drive\\UniMelb\\Research Project\\Open Coding\\20230606\\',
        'W:\\My Drive\\UniMelb\\Research Project\\Open Coding\\20230607\\',
        'W:\\My Drive\\UniMelb\\Research Project\\Open Coding\\20230608\\',
        'W:\\My Drive\\UniMelb\\Research Project\\Open Coding\\20230609\\',
        'W:\\My Drive\\UniMelb\\Research Project\\Open Coding\\20230610\\',
        'W:\\My Drive\\UniMelb\\Research Project\\Open Coding\\20230622\\',
    ]
    for directory_path in directory_paths:
        for file_name in os.listdir(directory_path):
            if file_name not in ['desktop.ini']:
                if file_name[-5:] == '.docx':
                    file_name = file_name[:-5]
                file_names.append(file_name)
    return file_names


def dummy(repo, file_names):
    file_name = repo.replace('/', '_', 1)
    file_name = f'{file_name}.csv'
    if file_name in file_names:
        return 0
    content = get_latest_content(f'C:\\Files\\security policies\\{file_name}')
    headers, paragraphs = get_headers_and_paragraphs(content)
    l_1 = len(headers)
    l_2 = len(paragraphs)
    return l_1 if l_1 == l_2 else 0


def print_numbers():
    l = repos(dummy, get_file_names())
    print(sum(l))
    # total = 0
    # for file_name in :
    #     content = get_latest_content(f'C:\\Files\\security policies\\{file_name}')
    #     headers, paragraphs = get_headers_and_paragraphs(content)
    #     total = total + len(headers)
    # print(total)

def print_association_rules(items, min_support):
    df = pd.DataFrame(items, columns=category_names)
    # x = (5 * len(items)) / 4426
    # min_support = x / len(items)
    frequent_itemsets  = apriori(df, min_support=min_support, use_colnames=True)
    rules = association_rules(frequent_itemsets, metric="confidence")
    for _, rule in rules.iterrows():
        antecedents = list(rule['antecedents'])
        antecedents.sort()
        antecedents = ', '.join(antecedents)
        consequents = list(rule['consequents'])
        consequents.sort()
        consequents = ', '.join(consequents)
        support = rule['support']
        confidence = rule['confidence']
        # if support >= 0.1:
        print(f'"{{{antecedents}}}","->","{{{consequents}}}",{support},{confidence}')
    # print(f'{x} {len(items)}')


def print_security_policy_association_rules():
    items = []
    i = 0
    csv_file_path = 'C:\\Users\\Robert Wan\\Desktop\\Attributes.csv'
    for row in csv_reader(csv_file_path):
        i = i + 1
        if i > 2:
            item = []
            categories = list(eval(row[2]).keys())
            for category in category_names:
                item.append(True if category in categories else False)
            items.append(item)
    print(len(items))
    print_association_rules(items, 0.00000000001)


def print_header_paragraph_pair_association_rules():
    items = []
    for a in get_header_paragraph_pair_categorisations():
        item = []
        for category in category_names:
            item.append(True if category in a else False)
        items.append(item)
    print_association_rules(items, 0.002)


def get_header_paragraph_pair_categorisations():
    _, categorised_file_paths = get_remaining_and_categorised_file_paths()
    my_list = []
    for file_path in categorised_file_paths:
        file_name = file_path.split('\\')[-1]
        file_extension = file_name.split('.')[-1]
        if file_extension == 'docx':
            file_tuple = get_docx_file_tuple(file_path)
        elif file_extension == 'csv':
            file_tuple = get_csv_file_tuple(file_path)
        for a in file_tuple[2]:
            my_list.append(a)
    my_list = my_list[:-2]
    directory_path = 'C:\\Files\\Projects\\jupyter\\samples\\'
    for file_name in os.listdir(directory_path):
        for row in csv_reader(f'{directory_path}{file_name}'):
            my_list.append(row[2].split(','))
    return my_list


if __name__ == '__main__':
    # print_header_categorisation()
    # print_number_of_categories_per_header_paragraph_pairs()
    # print_results()
    # my_dict = get_manual_repo_category_dict()
    # print_security_policy_association_rules()
    print_header_paragraph_pair_association_rules()

    # aaa = get_header_paragraph_pair_categorisations()
    # for a in aaa:
    #     print(f'{a}')
    # print(len(aaa))


