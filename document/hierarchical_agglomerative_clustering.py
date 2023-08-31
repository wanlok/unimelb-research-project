import os
import random

import pandas as pd
import numpy as np
from Levenshtein import distance
from matplotlib import pyplot as plt
from sklearn.cluster import AgglomerativeClustering
import scipy.cluster.hierarchy as sch
from sklearn.metrics import silhouette_score

from document.document_utils import get_docx_content, get_headers_and_paragraphs
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


def write_csv(names, contents):
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
        # print(len(set(dendrogram['color_list'])) - 1)
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
            max_change_length = max(len(texts[i]), len(texts[j]))
            if max_change_length > 0:
                row.append(distance(texts[i], texts[j]) / max_change_length)
            else:
                row.append(0)
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
            model = AgglomerativeClustering(n_clusters=n, metric='precomputed', linkage='single')
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
    return parent_github_contents, root_contents, github_contents, docs_contents


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


def get_key(number, max_value):
    if number == 0:
        key = '0'
    elif number <= max_value * 1 / 5:
        key = '0.2'
    elif number <= max_value * 1 / 4:
        key = '0.25'
    elif number <= max_value * 1 / 3:
        key = '0.33'
    elif number <= max_value * 1 / 2:
        key = '0.5'
    else:
        key = '1'
    return key


def get_key_2(percentage):
    if percentage == 0:
        key = 0
    elif percentage < 0.1:
        key = 0.1
    elif percentage < 0.2:
        key = 0.2
    elif percentage < 0.3:
        key = 0.3
    elif percentage < 0.4:
        key = 0.4
    elif percentage < 0.5:
        key = 0.5
    elif percentage < 0.6:
        key = 0.6
    elif percentage < 0.7:
        key = 0.7
    elif percentage < 0.8:
        key = 0.8
    elif percentage < 0.9:
        key = 0.9
    else:
        key = 1
    return key


def get_bucket(contents):
    distance_dict = dict()
    df = get_df(contents)
    df_length = len(df)
    # max_value = None
    for i in range(df_length):
        # for j in range(df_length):
        #     if i < j:
        #         value = df[i][j]
        #         if max_value is None or value > max_value:
        #             max_value = value
        for j in range(df_length):
            if i < j:
                value = df[i][j]
                key = get_key_2(value)
                # key = nearest_range(value)
                if key in distance_dict:
                    distance_dict[key].append(value)
                else:
                    distance_dict[key] = [value]
    for key in distance_dict:
        distance_dict[key] = len(distance_dict[key])
    return sort_by_ascending_keys(distance_dict)


def get_statistics(user, location, contents):
    same_count = 0
    same_percentage = 0
    similar_count = 0
    similar_percentage = 0
    other_count = 0
    other_percentage = 0
    content_length = len(contents)
    number_of_combinations = int((content_length * content_length - content_length) / 2)
    distance_dict = get_bucket(contents)



    similar_threshold = 0
    # if len(distance_dict.keys()) > 0:
    #     max_key = max(distance_dict.keys())
    #     if max_key >= 100:

    for key in distance_dict:
        if key == 0:
        # if key == '0':
            same_count = same_count + distance_dict[key]
        # elif key < 300:
        elif key < 0.2:
        # elif key == '0.2' or key == '0.25' or key == '0.33':
            similar_count = similar_count + distance_dict[key]
        else:
            other_count = other_count + distance_dict[key]
    if number_of_combinations > 0:
        same_percentage = same_count / number_of_combinations
        similar_percentage = similar_count / number_of_combinations
        other_percentage = other_count / number_of_combinations
    if len(distance_dict) > 0:
        print(f'"{user}","{location}",{content_length},{same_percentage},{similar_percentage},{other_percentage},"{distance_dict}"')


def get_by_locations(users):
    locations = ['root', 'github', 'docs']
    for i in range(len(locations)):
        for user in users:
            names = get_names(user=user)
            contents = get_contents(names, show_path=show)
            write_csv(names, contents)
            t = get_contents_by_security_policy_repos(contents)
            get_statistics(user, locations[i], t[i + 1])


def dum_dum(map):
    count = 0
    same_count = 0
    similar_count = 0
    other_count = 0
    for key in map:
        length = len(map[key])
        # print(f'{key} {length}')
        count = count + length
        if key == 0:
            same_count = same_count + length
        elif key < 0.2:
            similar_count = similar_count + length
        else:
            other_count = other_count + length
    return count, same_count, similar_count, other_count


def as5(target_content, contents):
    my_dict = dict()
    for content in contents:
        max_change_length = max(len(target_content[1]), len(content[1]))
        if max_change_length > 0:
            key = get_key_2(distance(target_content[1], content[1]) / max_change_length)
            # print(f'LEV: {distance(target_content[1], content[1])} / {max_change_length}, {key}, {target_content[0]}, {content[0]}')
            if key in my_dict:
                my_dict[key].append((target_content[0], content[0]))
            else:
                my_dict[key] = [(target_content[0], content[0])]
    return my_dict


def rq2_2_1():
    print('Hello World')


def rl_traversal(node):
    # skipping leaves
    if not node.is_leaf():
        yield node.id
        yield from rl_traversal(node.right)
        yield from rl_traversal(node.left)


def graph_list(hook, hooks):
    left_hook = None
    right_hook = None
    for h in hooks:
        if h[1] == hook[0]:
            left_hook = h
        if h[1] == hook[3]:
            right_hook = h
    if hook[1] > 0:
        return [graph_list(left_hook, hooks), hook[1], graph_list(right_hook, hooks)]
    else:
        return hook[1]


def flatten_list(lst):
    flat_list = []
    for item in lst:
        if isinstance(item, list):
            flat_list.extend(flatten_list(item))
        else:
            flat_list.append(item)
    return flat_list


def oncd(X):
    number_of_cluster = 1
    ddd = dict()
    max_index = 0
    for i in range(len(X)):
        for j in range(len(X)):
            if i < j:
                ddd[f'{[i, j]}'] = X[i][j]
                if j > max_index:
                    max_index = j
    x_length = len(X)

    print(f'LENGTH: {len(ddd)} {max_index}')

    ddata = sch.dendrogram(sch.linkage(X, method='single'))

    hooks = ddata['dcoord']
    if len(hooks) > 0:
        root_hook = hooks[0]
        for hook in hooks:
            if hook[1] > root_hook[1]:
                root_hook = hook
        # hooks.remove(root_hook)
        aaa = graph_list(root_hook, hooks)
        print(aaa)
        print(flatten_list(aaa))

    return 0


if __name__ == '__main__':
    users = get_users()

    # users = ['socketio']
    users = ['google']
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
    # show = len(users) == 1
    show = False
    total = 0
    i = 0
    j = 0
    k = 0

    # get_by_locations(users)
    a_count = 0
    for user in users:
        names = get_names(user=user)
        contents = get_contents(names, show_path=show)
        write_csv(names, contents)
        parent_github_contents, github_contents, docs_contents, root_contents = get_contents_by_security_policy_repos(contents)


        parent_github_distance_dict = get_bucket(parent_github_contents)
        github_distance_dict = get_bucket(github_contents)
        docs_distance_dict = get_bucket(docs_contents)
        root_distance_dict = get_bucket(root_contents)

        global_contents = []
        # if len(parent_github_contents) > 0:
        #     global_contents = global_contents + [parent_github_contents[0]]
        # if len(github_contents) > 0:
        #     global_contents = global_contents + github_contents
        # if len(docs_contents) > 0:
        #     global_contents = global_contents + docs_contents
        # if len(root_contents) > 0:
        #     global_contents = global_contents + root_contents

        # number_of_parent_github_contents = len(parent_github_contents)
        # if number_of_parent_github_contents > 0:
        #     a_count = a_count + 1
        #     parent_github_content = parent_github_contents[0]
        #
        #     # a = dict()
        #     # b = dict()
        #     # c = dict()
        #     # for root_content in root_contents:
        #     #     max_change_length = max(len(parent_github_content[1]), len(root_content[1]))
        #     #     if max_change_length > 0:
        #     #         key = get_key_2(distance(parent_github_content[1], root_content[1]) / max_change_length)
        #     #         if key in a:
        #     #             a[key].append((parent_github_content[0], root_content[0]))
        #     #         else:
        #     #             a[key] = [(parent_github_content[0], root_content[0])]
        #     # for github_content in github_contents:
        #     #     max_change_length = max(len(parent_github_content[1]), len(github_content[1]))
        #     #     if max_change_length > 0:
        #     #         key = get_key_2(distance(parent_github_content[1], github_content[1]) / max_change_length)
        #     #         if key in b:
        #     #             b[key].append((parent_github_content[0], github_content[0]) )
        #     #         else:
        #     #             b[key] = [(parent_github_content[0], github_content[0])]
        #     # for docs_content in docs_contents:
        #     #     max_change_length = max(len(parent_github_content[1]), len(docs_content[1]))
        #     #     if max_change_length > 0:
        #     #         key = get_key_2(distance(parent_github_content[1], docs_content[1]) / max_change_length)
        #     #         if key in c:
        #     #             c[key].append((parent_github_content[0], docs_content[0]))
        #     #         else:
        #     #             c[key] = [(parent_github_content[0], docs_content[0])]
        #     root_count, root_same_count, root_similar_count, root_other_count = dum_dum(as5(parent_github_content, root_contents))
        #     github_count, github_same_count, github_similar_count, github_other_count = dum_dum(as5(parent_github_content, github_contents))
        #     docs_count, docs_same_count, docs_similar_count, docs_other_count = dum_dum(as5(parent_github_content, docs_contents))
        #
        #     print(f'\"{user}\",{len(contents)},{number_of_parent_github_contents},{root_count},{root_same_count},{root_similar_count},{root_other_count},{github_count},{github_same_count},{github_similar_count},{github_other_count},{docs_count},{docs_same_count},{docs_similar_count},{docs_other_count}')




        # for row in root_distance_dict:
        #     print(root_distance_dict[row])

        # print(parent_github_distance_dict)
        # print(github_distance_dict)
        # print(docs_distance_dict)
        # print(root_distance_dict)


        # print(len(parent_github_contents))
        # print(len(github_contents))
        # print(len(docs_contents))
        # print(len(root_contents))

        # print(user)

        # if len(github_contents) > 0:
        #     i = i + len(github_contents)
        # if len(docs_contents) > 0:
        #     j = j + len(docs_contents)
        # if len(root_contents) > 0:
        #     k = k + len(root_contents)

        # get_statistics(user, 'AAAA', global_contents)
        # get_statistics(user, 'root', root_contents)
        # get_statistics(user, 'github', github_contents)
        # get_statistics(user, 'docs', docs_contents)


        # get_segment(user, len(github_contents), github_distance_dict, len(docs_contents), docs_distance_dict, len(root_contents), root_distance_dict)



        # get_segment(docs_distance_dict, 300)
        # get_segment(root_distance_dict, 300)

        # i = i + 1
        # if len(github_distance_dict) > 0 or len(docs_distance_dict) > 0 or len(root_distance_dict) > 0:
        #
        #     print(f'{i} {user} {len(github_contents)} {len(docs_contents)} {len(root_contents)} {github_distance_dict} {docs_distance_dict} {root_distance_dict}')
        #     j = j + 1




        ## 20230803

        parent_github_github_distances = f'"{get_distances(parent_github_contents, github_contents)}"'
        parent_github_docs_distances = f'"{get_distances(parent_github_contents, docs_contents)}"'
        parent_github_root_distances = f'"{get_distances(parent_github_contents, root_contents)}"'

        # print(get_df(global_contents))
        # print(get_bucket(global_contents))

        X = read_csv()


        oncd(X)

        # number_of_clusters = get_number_of_clusters(X)

        # cluster = AgglomerativeClustering(n_clusters=None, affinity='euclidean', linkage='single', compute_full_tree=True,
        #                                   distance_threshold=1000)
        # # Cluster the data
        # cluster.fit_predict(X)

        # print(f"Number of clusters = {1 + np.amax(cluster.labels_)}")



        #
        # print(f'NUMBER OF CLUSTERS: {number_of_clusters}')

        # print(f'{user},{len(parent_github_contents)},{len(github_contents)},{len(docs_contents)},{len(root_contents)},{parent_github_github_distances},{parent_github_docs_distances},{parent_github_root_distances},{number_of_clusters},"{githb}","{docs_distance_dict}","{root_distance_dict}"')



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

        # if len(X) > 1:
        #     dendrogram = sch.dendrogram(sch.linkage(X, method='centroid'))
        #     number_of_clusters = len(set(dendrogram['color_list'])) - 1
        #     print(f'{user} {number_of_clusters}')
        # else:
        #     print(f'{user} {1}')
        if show:
            plot_dendrogram(X)
    # print(a_count)
    # print(f'{i} {j} {k}')