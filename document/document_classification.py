import math
import os
import shutil

import numpy as np
import pandas as pd
from Levenshtein import distance

from document.document_utils import write_content_to_file_path, get_docx_content
from utils import get_latest_content, repos

csv_directory_path = 'C:\\Files\\security policies\\'
classification_directory_path = 'C:\\Users\\WAN Tung Lok\\Desktop\\Security Policy Manual Classification 3\\'


def get_content(repo, directory_path):
    slices = repo.split('/')
    file_name = '_'.join(slices)
    content = get_latest_content(f'{directory_path}{file_name}.csv')
    return repo, content


def create_docx(repo_content_list):
    if not os.path.exists(classification_directory_path):
        os.makedirs(classification_directory_path)
    for repo, content in repo_content_list:
        file_name = '_'.join(repo.split('/'))
        file_path = f'{classification_directory_path}{file_name}.docx'
        write_content_to_file_path(content, file_path)


def get_content_dict(repo_content_list):
    content_dict = dict()
    for repo, content in repo_content_list:
        key = content.strip()
        if key in content_dict:
            content_dict[key].append(repo)
        else:
            content_dict[key] = [repo]
    return content_dict


def group_same_documents(repo_content_list):
    group = 0
    content_dict = get_content_dict(repo_content_list)
    for content in content_dict:
        repo_list = content_dict[content]
        number_of_repo = len(repo_list)
        if number_of_repo > 1:
            group = group + 1
            os.makedirs(f'{classification_directory_path}{group}')
            for repo in repo_list:
                file_name = '_'.join(repo.split('/'))
                from_file_path = f'{classification_directory_path}{file_name}.docx'
                to_file_path = f'{classification_directory_path}{group}\\{file_name}.docx'
                shutil.move(from_file_path, to_file_path)


def get_contents():
    grouped_contents = []
    contents = []
    for file_name in os.listdir(classification_directory_path):
        file_path = f'{classification_directory_path}{file_name}'
        if os.path.isfile(file_path):
            contents.append((file_name, get_docx_content(file_path)))
        elif os.path.isdir(file_path):
            file_names = os.listdir(file_path)
            for file_name_2 in file_names:
                file_path_2 = f'{file_path}\\{file_name_2}'
                if os.path.isfile(file_path_2):
                    grouped_contents.append((file_name, get_docx_content(file_path_2)))
                    break
    return grouped_contents, contents


def get_content_by_group(group):
    content = None
    directory_path = f'{classification_directory_path}{group}\\'
    for file_name in os.listdir(directory_path):
        file_path = f'{directory_path}{file_name}'
        if os.path.isfile(file_path):
            content = get_docx_content(file_path)
            break
    return content


def group_similar_documents(grouped_contents, contents, threshold):
    for content in contents:
        min_d = None
        nearest_group = None
        for grouped_content in grouped_contents:
            d = distance(content[1], grouped_content[1])
            if min_d is None or d < min_d:
                min_d = d
                nearest_group = grouped_content
        if min_d <= threshold:
            directory_path = f'{classification_directory_path}{nearest_group[0]}\\levenshtein\\{threshold}\\'
            if not os.path.exists(directory_path):
                os.makedirs(directory_path)
            from_file_path = f'{classification_directory_path}{content[0]}'
            to_file_path = f'{directory_path}{content[0]}'
            shutil.move(from_file_path, to_file_path)


# def print_summary(repo_content_list):
#     group = 0
#     content_dict = get_content_dict(repo_content_list)
#     for content in content_dict:
#         repo_list = content_dict[content]
#         number_of_repo = len(repo_list)
#         if number_of_repo > 1:
#             group = group + 1
#             directory_path = f'{classification_directory_path}{group}\\levenshtein\\'
#             levenshtein_list = []
#             if os.path.exists(directory_path):
#                 levenshtein_list = os.listdir(directory_path)
#             print([group, number_of_repo, levenshtein_list])


def print_summary(directory_path=classification_directory_path):
    f_list = []
    for name_1 in os.listdir(directory_path):
        directory_path_1 = f'{directory_path}{name_1}\\'
        if os.path.isdir(directory_path_1):
            list_1 = []
            list_2 = []
            for name_2 in os.listdir(directory_path_1):
                directory_path_2 = f'{directory_path_1}{name_2}\\'
                if os.path.isdir(directory_path_2):
                    if name_2 == 'levenshtein':
                        for name_3 in os.listdir(directory_path_2):
                            list_1.append((int(name_3), len(os.listdir(f'{directory_path_2}{name_3}\\'))))
                    else:
                        list_2.append((int(name_2), len(os.listdir(directory_path_2))))
            group = int(name_1)
            index = 0
            for i in range(len(f_list)):
                if group > f_list[i][0]:
                    index = index + 1
            f_list.insert(index, [group, list_1, list_2])
    for a in f_list:
        print(f'{a[0]}, LEVENSHTEIN: {len(a[1])} {a[1]}, CHILDREN: {len(a[2])} {a[2]}')


def start_grouping():
    repo_content_list = repos(get_content, csv_directory_path)
    number_of_documents = len(repo_content_list)
    create_docx(repo_content_list)
    group_same_documents(repo_content_list)
    grouped_documents, ungrouped_documents = get_contents()
    number_of_ungrouped_documents = len(ungrouped_documents)
    threshold = 100
    # target = math.ceil(number_of_documents * 0.8)
    while number_of_ungrouped_documents > 0:
    # while number_of_documents - number_of_ungrouped_documents < target:
    # while threshold <= 200:
        print(f'NUMBER_OF_UNGROUPED_DOCUMENTS: {number_of_ungrouped_documents}, THRESHOLD: {threshold}')
        group_similar_documents(grouped_documents, ungrouped_documents, threshold)
        grouped_documents, ungrouped_documents = get_contents()
        number_of_ungrouped_documents = len(ungrouped_documents)
        threshold = threshold + 100
    merge_document_groups(100)
    merge_document_groups(200)
    print_summary()


def get_levenshtein_distances():
    grouped_documents, _ = get_contents()
    number_of_documents = len(grouped_documents)
    levenshtein_distances = []
    for i in range(number_of_documents):
        document_levenshtein_distances = []
        x = int(grouped_documents[i][0])
        x_content = grouped_documents[i][1]
        for j in range(number_of_documents):
            y = int(grouped_documents[j][0])
            y_content = grouped_documents[j][1]
            if x != y:
                d = distance(x_content, y_content)
                if x > y:
                    document_levenshtein_distances.append((y, x, d))
                else:
                    document_levenshtein_distances.append((x, y, d))
        levenshtein_distances.append(document_levenshtein_distances)
    return levenshtein_distances


def get_levenshtein_distance_matrix(contents):
    matrix = []
    number_of_contents = len(contents)
    for i in range(number_of_contents):
        row = []
        for j in range(number_of_contents):
            row.append(distance(contents[i], contents[j]))
        matrix.append(row)
    return matrix


def merge_document_groups(threshold):
    grouped_documents, _ = get_contents()
    matrix = get_levenshtein_distance_matrix([document[1] for document in grouped_documents])
    rows = list(map(lambda x: list(map(lambda y: 1 if y <= threshold else 0, x)), matrix))
    for row in get_groupings(rows):
        a = [int(grouped_documents[i][0]) for i in range(len(row)) if row[i] == 1]
        if len(a) > 1:
            a.sort()
            i = None
            for j in a:
                if i is None:
                    i = j
                else:
                    directory_path = f'{classification_directory_path}{i}\\{threshold}'
                    if not os.path.exists(directory_path):
                        os.makedirs(directory_path)
                    shutil.move(f'{classification_directory_path}{j}', f'{directory_path}\\{j}')


def search_by_user_recur(user, path=classification_directory_path, results=[]):
    for name in os.listdir(path):
        path_1 = f'{path}{name}'
        if os.path.isdir(path_1):
            search_by_user_recur(user, f'{path_1}\\')
        elif user.lower() == name.split('_')[0].lower():
            results.append(path_1)
    return results


def group_by_paths(results):
    path_set = set()
    path_dict = dict()
    for result in results:
        slices = result.split('\\')
        if 'levenshtein' in slices:
            path_set.add((1, '\\'.join(slices)))
        else:
            key = '\\'.join(slices[:-1])
            file_name = slices[-1]
            if key in path_dict:
                path_dict[key].append(file_name)
            else:
                path_dict[key] = [file_name]
    for path in path_dict:
        file_names = path_dict[path]
        path_set.add((len(file_names), f'{path}\\{file_names[0]}'))
    return list(path_set)


def get_groupings(rows):
    flatten_rows = []
    column = 0
    proceed = True
    while proceed:
        flatten_row = None
        for row in rows:
            number_of_columns = len(row)
            if column < number_of_columns:
                if row[column] == 1:
                    if flatten_row is None:
                        flatten_row = row
                    else:
                        for i in range(number_of_columns):
                            if row[i] == 1:
                                flatten_row[i] = 1
            else:
                proceed = False
        if flatten_row is not None:
            flatten_rows.append(flatten_row)
        column = column + 1
    group_dict = dict()
    for row in flatten_rows:
        group_dict[''.join(map(lambda x: f'{x}', row))] = row
    rows = []
    for key in group_dict:
        row = group_dict[key]
        # if len([x for x in row if x == 1]) > 1:
        rows.append(row)
    return rows


def dummy_dummy(threshold, user):
    documents = search_by_user_recur(user)
    distinct_documents = group_by_paths(documents)
    print(f'{len(documents)} {len(distinct_documents)}')
    print([x[0] for x in distinct_documents])
    contents = [get_docx_content(document[1]) for document in distinct_documents]
    matrix = get_levenshtein_distance_matrix(contents)
    rows = list(map(lambda x: list(map(lambda y: 1 if y <= threshold else 0, x)), matrix))
    total = 0
    for row in get_groupings(rows):
        a = [distinct_documents[i] for i in range(len(row)) if row[i] == 1]
        for document in a:
            print(f'{document[0]} "{document[1]}"')
        print()
        total = total + len(a)
    print(total)


if __name__ == '__main__':
    # start_grouping()

    # x_content = get_content_by_group(3)
    # y_content = get_content_by_group(37)
    # print(distance(x_content, y_content))

    # print_summary()

    # grouped_documents, _ = get_contents()
    # for document in grouped_documents:
    #     print(document)

    dummy_dummy(100, 'facebook')



