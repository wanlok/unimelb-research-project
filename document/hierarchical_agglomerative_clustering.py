import os
import random

import pandas as pd
import numpy as np
from Levenshtein import distance
from matplotlib import pyplot as plt
from sklearn.cluster import AgglomerativeClustering
import scipy.cluster.hierarchy as sch
from sklearn.metrics import silhouette_score

from document.document_utils import get_docx_content
from utils import csv_writer, csv_reader, get_repo_and_path, sort_by_ascending_keys

csv_file_path = f'C:\\Files\\zzz.csv'

directory_path = 'C:\\Users\\WAN Tung Lok\\Desktop\\Step 1\\'
# directory_path_2 = 'C:\\Users\\WAN Tung Lok\\Desktop\\Step 2\\'


def get_users():
    users = set()
    for name in os.listdir(directory_path):
        users.add(name.replace('.docx', '').split('_')[0].lower())
    return users


def get_names(user=None, random_n=None):
    if user is not None:
        user = user.lower()
        names = []
        for name in os.listdir(directory_path):
            if user == name.split('_')[0].lower():
                names.append(name)
    else:
        names = os.listdir(directory_path)
    if random_n is not None:
        names = random.sample(names, random_n)
    return names


def get_contents(names, show_path=False):
    contents = []
    i = 0
    for name in names:
        path = f'{directory_path}{name}'
        if os.path.isdir(path):
            path = f'{path}\\{os.listdir(path)[0]}'
        contents.append((name, get_docx_content(f'{path}')))
        if show_path:
            print(f'{i} "{path}"')
        i = i + 1
    return contents


def write_csv(contents):
    writer = csv_writer(csv_file_path, mode='w')
    writer.writerow([''] + names)
    for i in range(len(contents)):
        row = []
        for j in range(len(contents)):
            row.append(distance(contents[i][1], contents[j][1]))
        writer.writerow([contents[i][0]] + row)


def read_csv():
    rows = []
    i = 0
    for row in csv_reader(csv_file_path):
        if i > 0:
            rows.append(row[1:])
        i = i + 1
    # 18 22 25 27 42 43
    # rows.append([0, 4, 7, 9, 24, 25])
    # rows.append([4, 0, 3, 5, 20, 21])
    # rows.append([7, 3, 0, 2, 17, 18])
    # rows.append([9, 5, 2, 0, 15, 16])
    # rows.append([24, 20, 17, 15, 0, 1])
    # rows.append([25, 21, 18, 16, 1, 0])
    return pd.DataFrame(rows).to_numpy()


def plot_dendrogram(X):
    if len(X) > 1:
        # # dataset = pd.read_csv('C:\\Files\\Mall_Customers.csv')
        # #
        # # X = dataset.iloc[:, [2, 3, 4]].values
        plt.figure()
        # method='single'
        # method='centroid'
        dendrogram = sch.dendrogram(sch.linkage(X, method='single'))
        plt.show()


# def get_security_policy_repos(file_names):
#     security_policy_repos = []
#     d_path = 'C:\\Files\\security policies\\'
#     for file_name in file_names:
#         file_name = file_name.replace('.docx', '.csv')
#         file_path = f'{d_path}{file_name}'
#         security_policy_repo = get_latest_security_policy_repo(file_path)
#         security_policy_repos.append(security_policy_repo)
#     return security_policy_repos
#
#
# def get_same_content_groups(model, contents):
#     total = 0
#     groups = []
#     label_dict = dict()
#     labels = model.labels_
#     for i in range(len(labels)):
#         label = labels[i]
#         if label in label_dict:
#             label_dict[label].append(i)
#         else:
#             label_dict[label] = [i]
#     for label in label_dict:
#         file_names = list(map(lambda x: contents[x][0], label_dict[label]))
#         texts = list(map(lambda x: contents[x][1], label_dict[label]))
#         rows = []
#         for i in range(len(texts)):
#             row = []
#             for j in range(len(texts)):
#                 row.append(distance(texts[i], texts[j]))
#             rows.append(row)
#         df = pd.DataFrame(rows)
#         # print(df)
#         if df.sum().sum() == 0:
#             group = get_security_policy_repos(file_names)
#             groups.append(group)
#             total = total + len(group)
#     return total, groups


def get_df(contents):
    # file_names = list(map(lambda x: contents[x][0], label_dict[label]))
    texts = list(map(lambda x: x[1], contents))
    rows = []
    for i in range(len(texts)):
        row = []
        for j in range(len(texts)):
            row.append(distance(texts[i], texts[j]))
        rows.append(row)
    return pd.DataFrame(rows)


def get_text_dict(contents):
    text_dict = dict()
    d_path = 'C:\\Files\\security policies\\'
    for content in contents:
        docx_file_name = content[0]
        # docx_file_path = f'{directory_path}{docx_file_name}'
        csv_file_name = docx_file_name.replace('.docx', '.csv')
        csv_file_path = f'{d_path}{csv_file_name}'
        text = content[1]
        repo, path = get_repo_and_path(csv_file_path)
        key = f'{repo}|{path}'.lower()
        if text in text_dict:
            if key in text_dict[text]:
                text_dict[text][key].append(content)
            else:
                text_dict[text][key] = [content]
        else:
            text_dict[text] = dict()
            text_dict[text][key] = [content]
    return text_dict


def get_number_of_clusters(X):
    number_of_cluster = 1
    x_length = len(X)
    if x_length >= 2:
        scores = []
        n = 2
        while n <= x_length:
            model = AgglomerativeClustering(n_clusters=n, metric='euclidean', linkage='single')
            model.fit(X)
            if n < x_length:
                score = silhouette_score(X, model.labels_)
                scores.append(score)
            n = n + 1
        score_length = len(scores)
        if score_length > 0:
            max_score = max(scores)
            for i in range(score_length):
                score = scores[i]
                if score == max_score and score > 0.5:
                    number_of_cluster = i + 2
                    break
    return number_of_cluster


def get_contents_by_security_policy_repos(contents):
    parent_github_contents = []
    github_contents = []
    docs_contents = []
    root_contents = []
    text_dict = get_text_dict(contents)
    for text in text_dict:
        count_dict = text_dict[text]
        for repo_path in count_dict:
            slices = repo_path.split('|')
            repo = slices[0]
            project = repo.split('/')[1]
            path = slices[1]
            contents = count_dict[repo_path]
            # print(contents)
            if project == '.github':
                parent_github_contents.extend(contents)
            elif path == '.github/security.md':
                github_contents.extend(contents)
            elif path == 'docs/security.md':
                docs_contents.extend(contents)
            else:
                root_contents.extend(contents)
    return parent_github_contents, github_contents, docs_contents, root_contents


def get_distances(parent_github_contents, contents):
    if len(parent_github_contents) > 0:
        merged_contents = []
        text_dict = get_text_dict(contents)
        for text in text_dict:
            merged_contents.append((list(text_dict[text].keys()), text))
        contents = [parent_github_contents[0]] + merged_contents
        distances = list(zip(map(lambda x: x[0], contents), get_df(contents).iloc[0].tolist()))[1:]
        distances = sorted(distances, key=lambda x: x[1])
    else:
        distances = []
    return distances


def nearest_range(number):
    a = list(f'{number}')
    if number == 0:
        a = ['0']
    elif len(a) > 2:
        a[-1] = '0'
        a[-2] = '0'
    else:
        a = ['1']
    return int(''.join(a))


def get_distance_dict(contents):
    distance_dict = dict()
    df = get_df(contents)
    df_length = len(df)
    for i in range(df_length):
        for j in range(df_length):
            if i != j:
                value = df[i][j]
                key = nearest_range(value)
                if key in distance_dict:
                    distance_dict[key].append(value)
                else:
                    distance_dict[key] = [value]
    for key in distance_dict:
        distance_dict[key] = len(distance_dict[key])
    return sort_by_ascending_keys(distance_dict)


if __name__ == '__main__':
    users = get_users()
    # users = ['socketio']
    # users = ['google']
    # users = ['opencontainers']
    # users = ['npm']
    # users = ['oracle']
    # users = ['microsoft']
    # users = ['facebook']
    # users = ['angular']
    # users = ['thehive-project']
    # users = ['stripe']
    # users = ['rancher']
    # users = ['academysoftwarefoundation']
    # users = ['kubernetes-sigs']
    # users = ['socketio', 'google', 'opencontainers', 'npm', 'oracle', 'microsoft', 'facebook', 'angular', 'thehive-project', 'stripe']
    # users = ['pallets']
    show = len(users) == 1
    # show = False
    total = 0
    for user in users:
        names = get_names(user=user)
        contents = get_contents(names, show_path=show)
        write_csv(contents)
        parent_github_contents, github_contents, docs_contents, root_contents = get_contents_by_security_policy_repos(contents)
        github_distance_dict = get_distance_dict(github_contents)
        docs_distance_dict = get_distance_dict(docs_contents)
        root_distance_dict = get_distance_dict(root_contents)
        parent_github_github_distances = f'"{get_distances(parent_github_contents, github_contents)}"'
        parent_github_docs_distances = f'"{get_distances(parent_github_contents, docs_contents)}"'
        parent_github_root_distances = f'"{get_distances(parent_github_contents, root_contents)}"'
        X = read_csv()
        number_of_clusters = get_number_of_clusters(X)
        print(f'{user},{len(parent_github_contents)},{len(github_contents)},{len(docs_contents)},{len(root_contents)},{parent_github_github_distances},{parent_github_docs_distances},{parent_github_root_distances},{number_of_clusters},"{github_distance_dict}","{docs_distance_dict}","{root_distance_dict}"')



        # if len(parent_github_contents) > 0:
        #     parent_github_content = [parent_github_contents[0]]
        #     if len(github_contents) > 0:
        #         print(f'////////// {user} parent_github - github')
        #         print(ddd(parent_github_content, github_contents))
        #     if len(docs_contents) > 0:
        #         print(f'////////// {user} parent_github - docs')
        #         print(get_df(parent_github_content + dummy_dummy(docs_contents)).iloc[0].tolist())
        #     if len(root_contents) > 0:
        #         print(f'////////// {user} parent_github - root')
        #         print(get_df(parent_github_content + dummy_dummy(root_contents)).iloc[0].tolist())

        # for content in github_contents:
        #     print(content)
        # print(len(github_contents))
        # get_levenshtein_distance_df(github_contents)
        # get_levenshtein_distance_df(root_contents)
        # for i in range(len(mmm.keys())):
        #     print(mmm[mmm.keys[i]])
        # print(f'{user} {}')
        # print(f'{user},{number_of_clusters}')
        if show:
            plot_dendrogram(X)