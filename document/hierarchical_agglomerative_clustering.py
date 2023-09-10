import os
import random
import shutil

import pandas as pd
import numpy as np
from Levenshtein import distance
from matplotlib import pyplot as plt
from scipy.spatial.distance import squareform
from sklearn.cluster import AgglomerativeClustering
import scipy.cluster.hierarchy as sch
from sklearn.metrics import silhouette_score

from document.document_utils import get_docx_content, get_headers_and_paragraphs
from utils import csv_writer, csv_reader, get_repo_and_path, sort_by_ascending_keys, repos

from scipy.cluster.hierarchy import ClusterWarning
from warnings import simplefilter
simplefilter("ignore", ClusterWarning)

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
            rows.append(list(map(lambda x: int(x), row[1:])))
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


def get_graph_list(hook, hooks):
    if hook is not None:
        left = None
        right = None
        for h in hooks:
            if h[1] == hook[0]:
                left = h
            if h[1] == hook[3]:
                right = h
        if hook[1] > 0:
            print(f'{left} {right} {hooks}')
            return [get_graph_list(left, hooks), hook[1], get_graph_list(right, hooks)]
        else:
            return hook[1]
    else:
        return 0.0




def flatten_list(lst):
    flat_list = []
    for item in lst:
        if isinstance(item, list):
            flat_list.extend(flatten_list(item))
        else:
            flat_list.append(item)
    return flat_list


def get_gaps(graph_list, distances, gaps):
    left = graph_list[0]
    distance = graph_list[1]
    right = graph_list[2]
    if type(left) == list:
        gaps.append((left[1], distance, 'left'))
        distances.add(left[1])
        distances.add(distance)
        get_gaps(left, distances, gaps)
    else:
        gaps.append((left, distance, 'left'))
        distances.add(left)
        distances.add(distance)
    if type(right) == list:
        gaps.append((right[1], distance, 'right'))
        distances.add(right[1])
        distances.add(distance)
        get_gaps(right, distances, gaps)
    else:
        gaps.append((right, distance, 'right'))
        distances.add(right)
        distances.add(distance)


def get_largest_gaps(graph_list):
    largest_gaps = []
    distances = set()
    gaps = []
    get_gaps(graph_list, distances, gaps)
    distances = list(distances)
    distances.sort()
    largest_gap_start = 0
    largest_gap_end = 0
    largest_gap = 0
    for i in range(len(distances) - 1):
        start = distances[i]
        end = distances[i + 1]
        gap = end - start
        if gap > largest_gap:
            largest_gap_start = start
            largest_gap_end = end
            largest_gap = gap
    for gap in gaps:
        start, end, _ = gap
        if largest_gap_start >= start and largest_gap_end <= end:
            largest_gaps.append(gap)
    return largest_gaps


def rq2_extend():
    root_matched_set = set()
    root_mismatched_set = set()
    github_matched_set = set()
    github_mismatched_set = set()
    docs_matched_set = set()
    docs_mismatched_set = set()
    my_dict = dict()
    for user in get_users():
        names = get_names(user=user)
        contents = get_contents(names, show_path=False)
        write_csv(names, contents)
        parent_github_contents, root_contents, github_contents, docs_contents = get_contents_by_security_policy_repos(contents)
        for parent_github_content in parent_github_contents:
            for root_content in root_contents:
                d = distance(parent_github_content[1], root_content[1])
                if d == 0:
                    root_matched_set.add(root_content)
                else:
                    root_mismatched_set.add(root_content)
                    key = f'{user},root,{d}'
                    if key in my_dict:
                        my_dict[key].append(root_content)
                    else:
                        my_dict[key] = [root_content]
            for github_content in github_contents:
                d = distance(parent_github_content[1], github_content[1])
                if d == 0:
                    github_matched_set.add(github_content)
                else:
                    github_mismatched_set.add(github_content)
                    key = f'{user},github,{d}'
                    if key in my_dict:
                        my_dict[key].append(github_content)
                    else:
                        my_dict[key] = [github_content]
            for docs_content in docs_contents:
                d = distance(parent_github_content[1], docs_content[1])
                if d == 0:
                    docs_matched_set.add(docs_content)
                else:
                    docs_mismatched_set.add(docs_content)
                    key = f'{user},docs,{d}'
                    if key in my_dict:
                        my_dict[key].append(docs_content)
                    else:
                        my_dict[key] = [docs_content]
    print(f'{len(root_matched_set)},{len(root_mismatched_set)}')
    print(f'{len(github_matched_set)},{len(github_mismatched_set)}')
    print(f'{len(docs_matched_set)},{len(docs_mismatched_set)}')
    return my_dict


def get_levenshtein_distance_pairs(user, location, contents, my_dict):
    rows = []
    levenshtein_distance_pairs = []
    for i in range(len(contents)):
        row = []
        for j in range(len(contents)):
            d = distance(contents[i][1], contents[j][1])
            row.append(d)
            if i < j:
                levenshtein_distance_pairs.append((contents[i], contents[j], d))
        rows.append(row)
    # for row in rows:
    #     print(row)
    # if len(levenshtein_distance_pairs) > 0:
    #     print(f'{user},{levenshtein_distance_pairs}')
    # all_zeros = True
    for x, y, d in levenshtein_distance_pairs:
        key = f'{user},{location},{d}'
        if key in my_dict:
            my_dict[key].append((x, y))
        else:
            my_dict[key] = [(x, y)]

    # if len(levenshtein_distance_pairs) > 0 and all_zeros:
    #     print(f'{user},{levenshtein_distance_pairs}')
    return levenshtein_distance_pairs


def rq2_2_same_content():
    user_directory_levenshtein_dict = dict()
    user_directory_dict = dict()

    for user in get_users():
        names = get_names(user=user)
        contents = get_contents(names, show_path=False)
        parent_github_contents, root_contents, github_contents, docs_contents = get_contents_by_security_policy_repos(
            contents)
        get_levenshtein_distance_pairs(user, '"root directory"', root_contents, user_directory_levenshtein_dict)
        get_levenshtein_distance_pairs(user, '"\'.github\' directory"', github_contents, user_directory_levenshtein_dict)
        get_levenshtein_distance_pairs(user, '"\'docs\' directory"', docs_contents, user_directory_levenshtein_dict)

    for user_directory_levenshtein in user_directory_levenshtein_dict:
        slices = user_directory_levenshtein.split(',')
        count = len(set(map(lambda x: x[0], user_directory_levenshtein_dict[user_directory_levenshtein])))
        user_directory = ','.join(slices[:2])
        if user_directory in user_directory_dict:
            user_directory_dict[user_directory] = user_directory_dict[user_directory] + count
        else:
            user_directory_dict[user_directory] = count

    for user_directory_levenshtein in user_directory_levenshtein_dict:
        slices = user_directory_levenshtein.split(',')
        user_directory = ','.join(slices[:2])
        count = len(set(map(lambda x: x[0], user_directory_levenshtein_dict[user_directory_levenshtein])))
        total = user_directory_dict[user_directory]
        # if slices[2] == '0' and count != total:
        if slices[2] == '0':
            print(f'{user_directory},{count},{total}')


def rq2_similar_content():
    user_directory_levenshtein_dict = dict()
    user_directory_dict = dict()

    for user in get_users():
        names = get_names(user=user)
        contents = get_contents(names, show_path=False)
        # write_csv(names, contents)
        parent_github_contents, root_contents, github_contents, docs_contents = get_contents_by_security_policy_repos(contents)
        get_levenshtein_distance_pairs(user, '"root directory"', root_contents, user_directory_levenshtein_dict)
        get_levenshtein_distance_pairs(user, '"\'.github\' directory"', github_contents, user_directory_levenshtein_dict)
        get_levenshtein_distance_pairs(user, '"\'docs\' directory"', docs_contents, user_directory_levenshtein_dict)

    for user_directory_levenshtein in user_directory_levenshtein_dict:
        slices = user_directory_levenshtein.split(',')
        count = len(set(map(lambda x: x[0], user_directory_levenshtein_dict[user_directory_levenshtein])))
        user_directory = ','.join(slices[:2])
        if user_directory in user_directory_dict:
            user_directory_dict[user_directory] = user_directory_dict[user_directory] + count
        else:
            user_directory_dict[user_directory] = count

    for user_directory_levenshtein in user_directory_levenshtein_dict:
        slices = user_directory_levenshtein.split(',')
        user_directory = ','.join(slices[:2])
        count = len(set(map(lambda x: x[0], user_directory_levenshtein_dict[user_directory_levenshtein])))
        total = user_directory_dict[user_directory]
        # if slices[2] == '0' and count != total:
        # if slices[2] == '0':
        print(f'{user_directory},{count},{total}')


def get_document_pair_file_names(document_pairs):
    document_pair_file_names = []
    for document_pair in document_pairs:
        document_pair_file_names.append((document_pair[0][0], document_pair[1][0]))
    return document_pair_file_names


def get_document_pair_file_contents(document_pairs):
    document_pair_file_contents = []
    for document_pair in document_pairs:
        document_pair_file_contents.append((document_pair[0][1], document_pair[1][1]))
    return document_pair_file_contents


def rq2_3_3():
    user_directory_levenshtein_dict = dict()
    user_directory_dict = dict()

    for user in get_users():
        names = get_names(user=user)
        contents = get_contents(names, show_path=False)
        parent_github_contents, root_contents, github_contents, docs_contents = get_contents_by_security_policy_repos(contents)
        get_levenshtein_distance_pairs(user, '"root directory"', root_contents, user_directory_levenshtein_dict)
        get_levenshtein_distance_pairs(user, '"\'.github\' directory"', github_contents, user_directory_levenshtein_dict)
        get_levenshtein_distance_pairs(user, '"\'docs\' directory"', docs_contents, user_directory_levenshtein_dict)

    for x_key in user_directory_levenshtein_dict:
        file_names = get_document_pair_file_names(user_directory_levenshtein_dict[x_key])
        y_key = ','.join(x_key.split(',')[:2])
        if y_key in user_directory_dict:
            user_directory_dict[y_key] = user_directory_dict[y_key] + len(file_names)
        else:
            user_directory_dict[y_key] = len(file_names)

    for x_key in user_directory_levenshtein_dict:
        file_names = get_document_pair_file_names(user_directory_levenshtein_dict[x_key])
        file_contents = get_document_pair_file_contents(user_directory_levenshtein_dict[x_key])
        count = len(file_names)
        slices = x_key.split(',')
        levenshtein_distance = int(slices[2])
        x_key = ','.join(slices)
        total = user_directory_dict[','.join(slices[:2])]
        # if 0 < levenshtein_distance < 10 and count != total:
        if levenshtein_distance == 0 and count != total:
            my_dict = dict()
            if len(file_contents) > 0:
                for file_content, _ in file_contents:
                    key = distance(file_contents[0][0], file_content)
                    if key in my_dict:
                        my_dict[key] = my_dict[key] + 1
                    else:
                        my_dict[key] = 1
            print(f'{x_key},{count},{total},{my_dict}')
            # print(f'{x_key},{count},{total}')


def get_tree(tree, tree_nodes):
    if tree is not None:
        l, d, r = tree
        left_tree = None
        right_tree = None
        for i in reversed(range(len(tree_nodes))):
            if tree_nodes[i][1] == l:
                left_tree = tree_nodes.pop(i)
                break
        for i in reversed(range(len(tree_nodes))):
            if tree_nodes[i][1] == r:
                right_tree = tree_nodes.pop(i)
                break
        return [get_tree(left_tree, tree_nodes), d, get_tree(right_tree, tree_nodes)]
    else:
        return 0.0


def get_largest_gap_index(largest_gaps, distance, direction):
    index = None
    for i in range(len(largest_gaps)):
        _, largest_gap_distance, largest_gap_direction = largest_gaps[i]
        if distance == largest_gap_distance and direction == largest_gap_direction:
            index = i
            break
    # print(index)
    return index


def traverse(tree, largest_gaps, results=[], cluster=None):
    left, d, right = tree
    if type(left) == list:
        new_cluster = get_largest_gap_index(largest_gaps, d, 'left')
        if new_cluster is not None:
            cluster = new_cluster
        traverse(left, largest_gaps, results, cluster)
    elif type(left) == float:
        if cluster is None:
            results.append(get_largest_gap_index(largest_gaps, d, 'left'))
        else:
            results.append(cluster)
    if type(right) == list:
        new_cluster = get_largest_gap_index(largest_gaps, d, 'right')
        if new_cluster is not None:
            cluster = new_cluster
        traverse(right, largest_gaps, results, cluster)
    elif type(right) == float:
        if cluster is None:
            results.append(get_largest_gap_index(largest_gaps, d, 'right'))
        else:
            results.append(cluster)


def get_clusters(user, location, contents):
    names = []
    new_contents = []
    content_dict = dict()
    for file_name, content in contents:
        if content in content_dict:
            content_dict[content].append(file_name)
        else:
            content_dict[content] = [file_name]
    for key in content_dict:
        name = f'"{content_dict[key]}"'
        names.append(name)
        new_contents.append((name, key))
    write_csv(names, new_contents)
    X = read_csv()
    # plot_dendrogram(X)
    if len(X) > 0:
        names = list(map(lambda x: eval(eval(x)), names))
        if sum(sum(X)) > 1:
            tree_nodes = [[x[0], x[1], x[3]] for x in sch.dendrogram(sch.linkage(X, method='single'))['dcoord']]
            tree_root_node = None
            for tree_node in tree_nodes:
                if tree_root_node is None or tree_node[1] > tree_root_node[1]:
                    tree_root_node = tree_node
            clusters = []
            tree = get_tree(tree_root_node, [] + tree_nodes)
            traverse(tree, get_largest_gaps(tree), clusters)
            for i in range(len(names)):
                for j in range(len(names[i])):
                    names[i][j] = (names[i][j], user, location, clusters[i], max(clusters) + 1)
        else:
            for i in range(len(names)):
                for j in range(len(names[i])):
                    names[i][j] = (names[i][j], user, location, 0, 1)
        clusters = flatten_list(names)
    else:
        clusters = []
    return clusters


def rq2_ahc_results(repo, my_set):
    file_name = repo.replace('/', '_')
    file_name = f'{file_name}.docx'
    for m in my_set:
        if m[0] == file_name:
            # print(m)
            print(f'{repo},{m[1]},{m[2]},{m[3]},{m[4]}')
            break


def rq2_ahc():
    my_set = set()
    for user in get_users():
        # if user == 'google':
        if True:
            names = get_names(user=user)
            contents = get_contents(names, show_path=False)
            parent_github_contents, root_contents, github_contents, docs_contents = get_contents_by_security_policy_repos(contents)
            # print(f'{user} {len(parent_github_contents)} {len(root_contents)} {len(github_contents)} {len(docs_contents)}')
            parent_github_clusters = get_clusters(user, 'parent_github', parent_github_contents)
            root_clusters = get_clusters(user, 'root', root_contents)
            github_clusters = get_clusters(user, 'github', github_contents)
            docs_clusters = get_clusters(user, 'docs', docs_contents)
            # if a > 0 and b == 0 and c == 0 and d == 0:
            # print(f'{user} {parent_github_clusters + root_clusters + github_clusters + docs_clusters}')
            my_set.update(parent_github_clusters)
            my_set.update(root_clusters)
            my_set.update(github_clusters)
            my_set.update(docs_clusters)
    repos(rq2_ahc_results, my_set)


def copy_file(file_name):
    from_directory_path = 'C:\\Users\\WAN Tung Lok\\Desktop\\Step 1\\'
    to_directory_path = 'C:\\Users\\WAN Tung Lok\\Desktop\\Default Template\\'
    shutil.copyfile(f'{from_directory_path}{file_name}', f'{to_directory_path}{file_name}')

def rq2_general():
    my_set = set()
    u_set = set()

    default_template = '# Security Policy\n\n## Supported Versions\n\nUse this section to tell people about which versions of your project are\ncurrently being supported with security updates.\n\n| Version | Supported          |\n| ------- | ------------------ |\n| 5.1.x   | :white_check_mark: |\n| 5.0.x   | :x:                |\n| 4.0.x   | :white_check_mark: |\n| < 4.0   | :x:                |\n\n## Reporting a Vulnerability\n\nUse this section to tell people how to report a vulnerability.\n\nTell them where to go, how often they can expect to get an update on a\nreported vulnerability, what to expect if the vulnerability is accepted or\ndeclined, etc.\n'
    is_same_as_default_template = lambda x: x.lower().strip() == default_template.lower().strip()
    is_based_on_default_template = lambda x: 'Use this section to tell'.lower() in x.lower()

    for user in get_users():
        # if user == 'google':
        if True:
            names = get_names(user=user)
            contents = get_contents(names, show_path=False)
            parent_github_contents, root_contents, github_contents, docs_contents = get_contents_by_security_policy_repos(contents)

            a = len(parent_github_contents)
            b = len(root_contents)
            c = len(github_contents)
            d = len(docs_contents)

            for file_name, content in parent_github_contents:
                # if is_same_as_default_template(content):
                if not is_same_as_default_template(content) and is_based_on_default_template(content):
                    print(file_name)
                    # print((file_name, 'parent_github', a, b, c, d))
                    # copy_file(file_name)


            for file_name, content in root_contents:
                # if is_same_as_default_template(content):
                if not is_same_as_default_template(content) and is_based_on_default_template(content):
                    print(file_name)
                #     print((file_name, 'root', a, b, c, d))
                #     copy_file(file_name)

            for file_name, content in github_contents:
                # if is_same_as_default_template(content):
                if not is_same_as_default_template(content) and is_based_on_default_template(content):
                    # if a + b + c + d > 1:
                    print(file_name)
                    # print((file_name, 'github', a, b, c, d)
                    # copy_file(file_name)

            for file_name, content in docs_contents:
                # if is_same_as_default_template(content):
                if not is_same_as_default_template(content) and is_based_on_default_template(content):
                    # if a + b + c + d > 1:
                    print(file_name)
                    # print((file_name, 'docs', a, b, c, d))
                    # copy_file(file_name)

            # if a + b + c + d == 1:
            #     print(f'{user},{a},{b},{c},{d}')







def rq2_without_parent_github():


    my_dict = dict()
    for user in get_users():
        names = get_names(user=user)
        contents = get_contents(names, show_path=False)
        write_csv(names, contents)
        parent_github_contents, root_contents, github_contents, docs_contents = get_contents_by_security_policy_repos(contents)
        get_levenshtein_distance_pairs(user, '"root directory"', root_contents, my_dict)
        get_levenshtein_distance_pairs(user, '"\'.github\' directory"', github_contents, my_dict)
        get_levenshtein_distance_pairs(user, '"\'docs\' directory"', docs_contents, my_dict)


    for key in my_dict:
        a = ','.join(key.split(','))
        my_set = set(map(lambda x: x[0], my_dict[key]))

        if len(my_set) == 0:
            print(f'{a},{len(my_set)}')

        # root_list = []
        # github_list = []
        # docs_list = []

        # for root_content in root_contents:
        #     print(root_content)
        #     # root_user_set.add(user)
        # for github_content in github_contents:
        #     print(github_content)
        #     # github_matched_set.add(github_content[0])
        #     # github_user_set.add(user)
        # for docs_content in docs_contents:
        #     print(docs_content)
        #     # docs_matched_set.add(docs_content[0])
        #     # docs_user_set.add(user)



    # print(len(root_user_set.intersection(github_user_set).intersection(docs_user_set)))

    # print(len(root_matched_set))
    # print(len(root_user_set))
    # print(len(github_matched_set))
    # print(len(github_user_set))
    # print(len(docs_matched_set))
    # print(len(docs_user_set))



def rq2_2():
    my_dict = rq2_extend()
    for key in my_dict:
        a = ','.join(key.split(','))
        my_set = set(map(lambda x: x[0], my_dict[key]))
        print(f'{a},{len(my_set)}')



# if __name__ == '__main__':
#     users = get_users()
#
#     # users = ['socketio']
#     # users = ['google']
#     # users = ['opencontainers']
#     # users = ['npm']
#     # users = ['oracle']
#     # users = ['microsoft']
#     # users = ['facebook']
#     # users = ['angular']
#     # users = ['thehive-project']
#     # users = ['stripe']
#     # users = ['rancher']
#     # users = ['academysoftwarefoundation']
#     # users = ['kubernetes-sigs']
#     # users = ['socketio', 'google', 'opencontainers', 'npm', 'oracle', 'microsoft', 'facebook', 'angular', 'thehive-project', 'stripe']
#     # users = ['pallets']
#     show = len(users) == 1
#     # show = False
#     total = 0
#     i = 0
#     j = 0
#     k = 0
#
#     # get_by_locations(users)
#     a_count = 0
#     for user in users:
#         names = get_names(user=user)
#         contents = get_contents(names, show_path=show)
#         write_csv(names, contents)
#         parent_github_contents, github_contents, docs_contents, root_contents = get_contents_by_security_policy_repos(contents)
#
#
#         # parent_github_distance_dict = get_bucket(parent_github_contents)
#         # github_distance_dict = get_bucket(github_contents)
#         # docs_distance_dict = get_bucket(docs_contents)
#         # root_distance_dict = get_bucket(root_contents)
#
#
#
#         # get_segment(user, len(github_contents), github_distance_dict, len(docs_contents), docs_distance_dict, len(root_contents), root_distance_dict)
#
#
#
#         # get_segment(docs_distance_dict, 300)
#         # get_segment(root_distance_dict, 300)
#
#         # i = i + 1
#         # if len(github_distance_dict) > 0 or len(docs_distance_dict) > 0 or len(root_distance_dict) > 0:
#         #
#         #     print(f'{i} {user} {len(github_contents)} {len(docs_contents)} {len(root_contents)} {github_distance_dict} {docs_distance_dict} {root_distance_dict}')
#         #     j = j + 1
#
#
#
#
#         ## 20230803
#
#         parent_github_github_distances = f'"{get_distances(parent_github_contents, github_contents)}"'
#         parent_github_docs_distances = f'"{get_distances(parent_github_contents, docs_contents)}"'
#         parent_github_root_distances = f'"{get_distances(parent_github_contents, root_contents)}"'
#
#
#         print(parent_github_github_distances)
#         print(parent_github_docs_distances)
#         print(parent_github_root_distances)
#
#         # print(get_df(global_contents))
#         # print(get_bucket(global_contents))
#
#         # X = read_csv()
#         #
#         # print(f'{user},{get_number_of_clusters_2(X)}')
#
#         # number_of_clusters = get_number_of_clusters(X)
#
#         # cluster = AgglomerativeClustering(n_clusters=None, affinity='euclidean', linkage='single', compute_full_tree=True,
#         #                                   distance_threshold=1000)
#         # # Cluster the data
#         # cluster.fit_predict(X)
#
#         # print(f"Number of clusters = {1 + np.amax(cluster.labels_)}")
#
#
#
#         #
#         # print(f'NUMBER OF CLUSTERS: {number_of_clusters}')
#
#         # print(f'{user},{len(parent_github_contents)},{len(github_contents)},{len(docs_contents)},{len(root_contents)},{parent_github_github_distances},{parent_github_docs_distances},{parent_github_root_distances},{number_of_clusters},"{githb}","{docs_distance_dict}","{root_distance_dict}"')
#
#
#
#         # if len(parent_github_contents) > 0:
#         #     parent_github_content = [parent_github_contents[0]]
#         #     if len(github_contents) > 0:
#         #         print(f'////////// {user} parent_github - github')
#         #         print(ddd(parent_github_content, github_contents))
#         #     if len(docs_contents) > 0:
#         #         print(f'////////// {user} parent_github - docs')
#         #         print(get_df(parent_github_content + dummy_dummy(docs_contents)).iloc[0].tolist())
#         #     if len(root_contents) > 0:
#         #         print(f'////////// {user} parent_github - root')
#         #         print(get_df(parent_github_content + dummy_dummy(root_contents)).iloc[0].tolist())
#
#         # for content in github_contents:
#         #     print(content)
#         # print(len(github_contents))
#         # get_levenshtein_distance_df(github_contents)
#         # get_levenshtein_distance_df(root_contents)
#         # for i in range(len(mmm.keys())):
#         #     print(mmm[mmm.keys[i]])
#         # print(f'{user} {}')
#         # print(f'{user},{number_of_clusters}')
#
#         # if len(X) > 1:
#         #     dendrogram = sch.dendrogram(sch.linkage(X, method='centroid'))
#         #     number_of_clusters = len(set(dendrogram['color_list'])) - 1
#         #     print(f'{user} {number_of_clusters}')
#         # else:
#         #     print(f'{user} {1}')
#         # if show:
#         #     plot_dendrogram(X)
#     # print(a_count)
#     # print(f'{i} {j} {k}')
#     # print('DONE')


if __name__ == '__main__':

    # rq2_2()
    # rq2_2_same_content()
    # rq2_without_parent_github()
    # rq2_3_3()
    rq2_ahc()
    # rq2_general()