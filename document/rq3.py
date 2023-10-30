import difflib
import math
import os
import re
from collections import Counter
from datetime import datetime

from nltk import WordNetLemmatizer
from nltk.stem import PorterStemmer
from nltk.corpus import stopwords

import nltk
# nltk.download('stopwords')
# nltk.download('wordnet')

from Levenshtein import distance
from numpy import average, median, ceil
from scipy import stats

from chart import scatter_plot, box_plot
from cwe import get_cwe_dict
from document.document_categorisation_all import get_repo_categorisation_results, get_repo_header_paragraph_categories
from document.document_utils import get_headers_and_paragraphs, category_names
from document.my_statistics import compute_mann_whitney_effect_size
from document.owasp import get_owasp_cwe_dict
from nvdcve import get_list
from utils import csv_reader, sort_by_descending_values, get_latest_content, csv_writer


def get_contents(directory_path, file_name):
    contents = []
    i = 0
    for row in csv_reader(f'{directory_path}{file_name}'):
        if i > 0:
            contents.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6]))
        i = i + 1
    return contents



def print_number_of_changes():
    directory_path = 'C:\\Files\\security policies\\'
    content_dict = dict()
    for file_name in os.listdir(directory_path):
        contents = get_contents(directory_path, file_name)
        content_length = len(contents) - 1
        distances = []
        for content in contents:
            distances.append(int(content[6]))
        # t = average(distances)
        t = (file_name, distances)
        if content_length in content_dict:
            content_dict[content_length].append(t)
        else:
            content_dict[content_length] = [t]
    keys = list(content_dict.keys())
    keys.sort()
    total = 0
    data_list = []
    for key in keys:
        count = len(content_dict[key])
        total = total + count
        print(f'{key},{count},{content_dict[key]}')
        if key > 0:
            for i in range(count):
                data_list.append(key)
    print(total)
    print(data_list)
    print(sum(data_list))
    print(median(data_list))
    print(average(data_list))
    box_plot([data_list], 'W:\\My Drive\\UniMelb\\Research Project\\Diagrams\\RQ1\\number of changes.png')


def print_change_periods(is_a=True):
    file_path_list = get_file_path_list()
    for repo, histories in file_path_list:
        a_d = []
        a_l = []
        b_d = []
        b_l = []
        for history in histories:
            date_time_diff = history[6]
            if date_time_diff is not None:
                if date_time_diff.days == 0:
                    a_d.append(history[4])
                    a_l.append(history[5])
                if date_time_diff.days > 0:
                    b_d.append(history[4])
                    b_l.append(history[5])
        a_l_0 = list(filter(lambda x: x == 0, a_l))
        b_l_0 = list(filter(lambda x: x == 0, b_l))
        if is_a:
            number_of_a = len(a_d)
            if number_of_a > 0:
                print(f'{repo},{number_of_a},{average(a_d)},{len(a_l_0)},"{a_d}","{a_l}"')
        else:
            number_of_b = len(b_d)
            if number_of_b > 0:
                print(f'{repo},{number_of_b},{average(b_d)},{len(b_l_0)},"{b_d}","{b_l}"')


# def print_change_periods_2():
#     file_path_list = get_file_path_list()
#     for repo, histories in file_path_list:
#         a_d = []
#         a_l = []
#         for history in histories:
#             date_time_diff = history[6]
#             if date_time_diff is not None:
#                 days = (date_time_diff.days * 24 + date_time_diff.seconds / 3600) / 24
#                 print(f'{repo}|{days}|')



def get_number_of_days(date_diff):
    return date_diff.days + date_diff.seconds / 3600 / 24


def print_repo_histories():
    file_path_list = get_file_path_list()
    count = 0
    day_occurrence_counts = []
    day_counts = []
    for repo, histories in file_path_list:
        if len(histories) > 1:
            date_diffs = [x[4] for x in histories]
            day_diffs = [x.days for x in date_diffs if x is not None]
            short_period_changes = [x for x in day_diffs if x == 0]
            long_period_changes = [x for x in day_diffs if x > 0]
            count = count + 1
            days = [get_number_of_days(date_diffs[i + 1]) for i in range(len(date_diffs) - 1)]
            day_occurrence_count = len(days)
            day_occurrence_counts.append(day_occurrence_count)
            day_count = average(days)
            day_counts.append(day_count)
            print(f'{count},"{repo}",{len(day_diffs)},{len(short_period_changes)},{len(long_period_changes)},"{days}",{day_count}')
    print(f'- - - - - - - - - - {average(day_occurrence_counts)} {average(day_counts)}')
    box_plot([day_occurrence_counts], 'W:\\My Drive\\UniMelb\\Research Project\\Diagrams\\RQ3\\All Changes.png')


def get_deleted_list(histories):
    deleted_list = []
    for history in histories:
        deleted_list.append(len(history[6]) == 0 and int(history[7]) > 0)
    return deleted_list


def print_insert_replace_delete():
    file_name_dict = get_file_name_dict()
    insert = 0
    replace = 0
    delete = 0
    file_dict = dict()
    for file_name in file_name_dict:
        aa = file_name_dict[file_name]
        for date_time in aa:
            actions = aa[date_time]
            for action in actions:
                insert = insert + action[1]
                replace = replace + action[2]
                delete = delete + action[3]
                if file_name in file_dict:
                    if date_time in file_dict[file_name]:
                        date_time_dict = file_dict[file_name]
                        b_1, b_2, b_3 = date_time_dict[date_time]
                        date_time_dict[date_time] = (b_1 + action[1], b_2 + action[2], b_3 + action[3])
                    else:
                        file_dict[file_name][date_time] = (action[1], action[2], action[3])
                else:
                    file_dict[file_name] = dict()
                    file_dict[file_name][date_time] = (action[1], action[2], action[3])
                # print(f'{file_name} {date_time} {action[1]} {action[2]} {action[3]}')
    count = 0
    s_p_c_insert = []
    s_p_c_replace = []
    s_p_c_delete = []
    l_p_c_insert = []
    l_p_c_replace = []
    l_p_c_delete = []
    s_r_c = 0
    s_d_c = 0
    l_d_c = 0
    for file_name in file_dict:
        date_time_dict = file_dict[file_name]
        date_time_list = list(date_time_dict.keys())
        date_time_list.sort()
        previous_date_time = None
        l_list = []
        delta_list = []
        for i in range(0, len(date_time_list)):
            date_time = date_time_list[i]
            l_list.append(date_time_dict[date_time])
            if previous_date_time is not None:
                delta_list.append((date_time - previous_date_time).days)
            previous_date_time = date_time
        s_p_c_indexes = [i + 1 for i in range(len(delta_list)) if delta_list[i] == 0]
        l_p_c_indexes = [i + 1 for i in range(len(delta_list)) if delta_list[i] > 0]
        s_p_c = [l_list[i] for i in range(len(l_list)) if i in s_p_c_indexes]
        l_p_c = [l_list[i] for i in range(len(l_list)) if i in l_p_c_indexes]
        count = count + len(date_time_dict) - 1
        print(file_name, len(date_time_dict), l_list, s_p_c, l_p_c, delta_list)
        for insert, replace, delete in s_p_c:
            s_p_c_insert.append(insert)
            s_p_c_replace.append(replace)
            s_p_c_delete.append(delete)
            if delete == 0:
                s_d_c = s_d_c + 1
        for insert, replace, delete in l_p_c:
            l_p_c_insert.append(insert)
            l_p_c_replace.append(replace)
            l_p_c_delete.append(delete)
            if delete == 0:
                l_d_c = l_d_c + 1

        # for date_time in date_time_dict:
        #     print((file_name, date_time))
        # t = file_dict[file_name]
        # insert = insert + t[0]
        # replace = replace + t[1]
        # delete = delete + t[2]
    # print(count)

    print(f'{len(s_p_c_insert)} {average(s_p_c_insert)} {median(s_p_c_insert)} {s_p_c_insert}')
    print(f'{len(l_p_c_insert)} {average(l_p_c_insert)} {median(l_p_c_insert)} {l_p_c_insert}')
    box_plot([s_p_c_insert, l_p_c_insert], 'W:\\My Drive\\UniMelb\\Research Project\\Diagrams\\RQ3\\action_insert.png')
    print(f'{len(s_p_c_replace)} {average(s_p_c_replace)} {median(s_p_c_replace)} {s_p_c_replace}')
    print(f'{len(l_p_c_replace)} {average(l_p_c_replace)} {median(l_p_c_replace)} {l_p_c_replace}')
    box_plot([s_p_c_replace, l_p_c_replace], 'W:\\My Drive\\UniMelb\\Research Project\\Diagrams\\RQ3\\action_replace.png')
    print(f'{len(s_p_c_delete)} {len([x for x in s_p_c_delete if x == 0])} {average(s_p_c_delete)} {median(s_p_c_delete)} {s_p_c_delete}')
    print(f'{len(l_p_c_delete)} {len([x for x in l_p_c_delete if x == 0])} {average(l_p_c_delete)} {median(l_p_c_delete)} {l_p_c_delete}')
    box_plot([s_p_c_delete, l_p_c_delete], 'W:\\My Drive\\UniMelb\\Research Project\\Diagrams\\RQ3\\action_delete.png')
    print(f'{s_d_c} {l_d_c}')



    # print(r)

    # print((insert, replace, delete))

        # print(f'{file_name} {}')


def get_x_period_change(x):
    file_dict = dict()
    file_name_dict = get_file_name_dict()
    for file_name in file_name_dict:
        date_time_dict = file_name_dict[file_name]
        date_times = list(date_time_dict.keys())
        date_times.sort()
        previous_date_time = None
        delta_list = []
        for date_time in date_times:
            if previous_date_time is not None:
                delta_list.append((date_time - previous_date_time).days)
            previous_date_time = date_time
        if x == 'short':
            indexes = [i + 1 for i in range(len(delta_list)) if delta_list[i] == 0]
        elif x == 'long':
            indexes = [i + 1 for i in range(len(delta_list)) if delta_list[i] > 0]
        else:
            indexes = [i + 1 for i in range(len(date_times) - 1)]
        for i in indexes:
            date_time = date_times[i]
            actions = date_time_dict[date_time]
            for action in actions:
                if file_name in file_dict:
                    if date_time in file_dict[file_name]:
                        file_date_time_dict = file_dict[file_name]
                        insert_count, replace_count, delete_count = file_date_time_dict[date_time]
                        file_date_time_dict[date_time] = (
                            insert_count + action[1],
                            replace_count + action[2],
                            delete_count + action[3]
                        )
                    else:
                        file_dict[file_name][date_time] = (action[1], action[2], action[3])
                else:
                    file_dict[file_name] = dict()
                    file_dict[file_name][date_time] = (action[1], action[2], action[3])
    return file_dict


def print_common_change_actions():
    insert_count = 0
    replace_count = 0
    delete_count = 0
    file_dict = get_x_period_change('')
    for file_name in file_dict:
        date_time_dict = file_dict[file_name]
        print(file_name, date_time_dict)
        for date_time in date_time_dict:
            x, y, z = date_time_dict[date_time]
            insert_count = insert_count + x
            replace_count = replace_count + y
            delete_count = delete_count + z
    print(f'{len(file_dict)},{insert_count / len(file_dict)},{replace_count / len(file_dict)},{delete_count / len(file_dict)}')


    # total_count = 0
    # total_negative_count = 0
    # for file in file_dict:
    #     date_dict = file_dict[file]
    #     dates = date_dict.keys()
    #     # dates = list(map(lambda x: f'{x}', dates))
    #     date_levenshtein = list(map(lambda x: (f'{x}', date_dict[x][0] - date_dict[x][2]), dates))
    #     negative_count = len([x for x in date_levenshtein if x[1] < 0])
    #     print(f'{file} {negative_count} {len(date_levenshtein)} {date_levenshtein}')
    #     total_count = total_count + len(date_levenshtein)
    #     total_negative_count = total_negative_count + negative_count
    # print(f'{insert_count / change_count} {replace_count / change_count} {delete_count / change_count} {change_count} {total_count} {total_negative_count}')


def deduplicate(list):
    new_list = []
    for item in list:
        if item not in new_list:
            new_list.append(item)
    return new_list


def print_analysis_3():
    file_path_list = get_file_path_list()

    for file_path in file_path_list:
        file_name = file_path[0]
        changes = file_path[1]
        header_list = []
        k = []
        for change in changes:
            content = change[6]
            headers, _ = get_headers_and_paragraphs(content, False)
            headers = deduplicate(headers)
            headers.sort()
            header_list.append((f'{change[3]}', headers))
            k.append(f'{headers}')
        if len(k) > 1 and len(set(k)) > 1:
            print(file_name)
            for x in k:
                print(x)
        # print(len(file_path[1]))



def print_short_period_changes():
    count = 0
    changes = []
    values = []
    for repo, histories, groups in get_repo_histories(True):
        # deleted_list = get_deleted_list(histories)
        # if True in deleted_list:
        #     slices = repo.split('_')
        #     github_repo = f'{slices[0]}/.github'
        #     repo_list = [x[0] for x in histories]
        #     if github_repo in repo_list:
        #         print(f'CHECK AFTER DELETE {repo} {repo_list} {deleted_list}')

        count = count + 1
        delta_list = [x[4].seconds / 3600 for x in histories]
        change = len(histories)
        changes.append(change)
        value = average(delta_list)
        values.append(value)
        print(f'{count},{repo},{change},{groups},{delta_list},{value}')
    print(f'- - - - - - - - - {median(changes)} {average(changes)} {median(values)} {average(values)}')
    box_plot([changes], 'W:\\My Drive\\UniMelb\\Research Project\\Diagrams\\RQ3\\Short Period Changes 1.png')
    box_plot([values], 'W:\\My Drive\\UniMelb\\Research Project\\Diagrams\\RQ3\\Short Period Changes 2.png')


def print_long_period_changes():
    count = 0
    changes = []
    values = []
    for repo, histories, _ in get_repo_histories(False):
        deleted_list = get_deleted_list(histories)

        if True in deleted_list:
            slices = repo.split('_')
            github_repo = f'{slices[0]}/.github'
            repo_list = [x[0] for x in histories]
            if github_repo in repo_list:
                print(f'CHECK AFTER DELETE {repo} {repo_list} {deleted_list}')

        count = count + 1
        delta_list = [x[4].days + x[4].seconds / 3600 / 24 for x in histories]
        change = len(histories)
        changes.append(change)
        value = average(delta_list)
        values.append(value)
        # print(f'{count},{repo},{change},{delta_list},{value}')
    print(f'- - - - - - - - - -  {median(changes)} {average(changes)} {median(values)} {average(values)}')
    box_plot([changes], 'W:\\My Drive\\UniMelb\\Research Project\\Diagrams\\RQ3\\Long Period Changes 1.png')
    box_plot([values], 'W:\\My Drive\\UniMelb\\Research Project\\Diagrams\\RQ3\\Long Period Changes 2.png')


def get_action_distributions(action_dict):
    if 'Insert' in action_dict:
        insert = action_dict['Insert']
    else:
        insert = ''
    if 'Replace' in action_dict:
        replace = action_dict['Replace']
    else:
        replace = ''
    if 'Delete' in action_dict:
        delete = action_dict['Delete']
    else:
        delete = ''
    return insert, replace, delete


def print_steps(repo, a):
    steps = get_steps(a[5], a[6])
    action_dict = dict()
    for i in range(len(steps)):
        action, _, _, _ = steps[i]
        if action in action_dict:
            action_dict[action] = action_dict[action] + 1
        else:
            action_dict[action] = 1
    if 'Insert' in action_dict:
        insert = action_dict['Insert']
    else:
        insert = ''
    if 'Replace' in action_dict:
        replace = action_dict['Replace']
    else:
        replace = ''
    if 'Delete' in action_dict:
        delete = action_dict['Delete']
    else:
        delete = ''
    print(f'{repo},"{a[3]}",{insert},{replace},{delete}')


def print_changes_all_made_within_one_day():
    i = 0
    for repo, histories in get_file_path_list():
        if len(histories) > 1:
            dates = [x[3] for x in histories]
            content_lengths = [len(x[6]) for x in histories]
            distances = [int(x[7]) for x in histories]
            date_diff = max(dates) - min(dates)
            if date_diff.days == 0:
                i = i + 1
                print(f'{i},{repo},{content_lengths},{distances}')
                # for a in histories[1:]:
                #     print_steps(repo, a)



def get_file_path_list():
    file_path_list = []
    directory_path = 'C:\\Files\\security policies\\'
    for file_name in os.listdir(directory_path):
        path_list = []
        contents = get_contents(directory_path, file_name)
        previous_date_time = None
        for repo, path, sha, date_time_string, previous_content, content, d in contents:
            date_time = get_date_time(date_time_string, '%Y-%m-%d %H:%M:%S%z')
            if previous_date_time is None:
                date_time_diff = None
            else:
                date_time_diff = date_time - previous_date_time
            path_list.append((repo, path, sha, date_time, date_time_diff, previous_content, content, d))
            previous_date_time = date_time
        file_path_list.append((file_name, path_list))
    return file_path_list


def print_move_patterns(as_count=True):
    path_dict = get_path_dict()
    for key in path_dict:
        movement = ' -> '.join(eval(key))
        if as_count:
            print(f'"{movement}",{len(path_dict[key])}')
        else:
            print(f'"{movement}",{path_dict[key]}')
    return path_dict


def get_paths(rows):
    paths = []
    previous_path = None
    for row in rows:
        if '.github' in row[0]:
            path = 'parent .github/SECURITY.md'
        else:
            path = row[1]
        content_length = len(row[6])
        if previous_path is None or (path != paths[-1] and content_length > 0):
            paths.append(path)
        previous_path = path
    return paths


def get_path_dict():
    path_dict = dict()
    for l in get_file_path_list():
        paths = get_paths(l[1])
        if len(paths) > 1:
            key = f'{paths}'
            if key in path_dict:
                path_dict[key].append(l)
            else:
                path_dict[key] = [l]
    return path_dict


def get_user_dict(destinations=['.github/SECURITY.md']):
    user_dict = dict()
    path_dict = get_path_dict()
    for key in path_dict:
        key = eval(key)
        if key[-1] in destinations:
            for b in path_dict[f'{key}']:
                user = b[0].split('_')[0]
                if user in user_dict:
                    user_dict[user].append(b[1])
                else:
                    user_dict[user] = [b[1]]
    return user_dict


def get_date_number_from_string(date_time_string, format):
    return int(datetime.strptime(date_time_string, format).strftime('%Y%m%d'))


def get_date(date_number):
    return datetime.strptime(f'{date_number}', '%Y%m%d')


def get_date_time(date_time_string, format):
    return datetime.strptime(date_time_string, format)


def get_parent_github_security_policy_create_date(security_policies):
    a_date = None
    for security_policy in security_policies:
        for row in security_policy:
            if '.github' in row[0]:
                a_date = get_date_number_from_string(row[3], '%Y-%m-%d %H:%M:%S%z')
                break
    return a_date


def security_policies_before():
    directory_path = 'C:\\Files\\Projects\\User Repositories\\'
    user_dict = get_user_dict()

    total = 0
    for user in user_dict:
        a_date = get_parent_github_security_policy_create_date(user_dict[user])
        b_list = []
        my_dict = dict()
        with open(f'{directory_path}{user}.txt', encoding='utf-8') as f:
            lines = f.readlines()
            for a in eval(lines[0]):
                name = a['node']['name']
                date_string = get_date_number_from_string(a['node']['createdAt'], '%Y-%m-%dT%H:%M:%SZ')
                # if date_string >= 20190523:
                if True:
                    if date_string in my_dict:
                        my_dict[date_string].append(name)
                    else:
                        my_dict[date_string] = [name]
        a_count = 0
        count = 0
        for key in my_dict:
            c = len(my_dict[key])
            if key <= a_date:
                a_count = a_count + c
            count = count + c
            b_list.append((key, count))

        total = total + count

        # print('- - - - - - - - - -')
        # print(f'{user},{count}')
        # print(a_date)
        # print(f'{b_list}')
        # print(f'{user},{a_count},{count},{1 - a_count / count}')
        print(f'{user},{a_count},{count}')

    print()
    print(f'TOTAL: {total} {len(user_dict)}')


def get_relevant_repos():
    repos = []
    directory_path = 'C:\\Files\\Projects\\User Repositories\\'
    for user in get_user_dict():
        with open(f'{directory_path}{user}.txt', encoding='utf-8') as f:
            lines = f.readlines()
            for a in eval(lines[0]):
                name = a['node']['name']
                if name != '.github':
                    repos.append(f'{user}/{name}')
    return repos


def get_relevant_repo_contents():
    rows = []
    directory_path = 'C:\\Files\\Projects\\Other Security Policies\\'
    for file_name in os.listdir(directory_path):
        slices = file_name.split('_')
        user = slices[0]
        parent_github_repo_dates = []
        repo_dates = []
        with open(f'{directory_path}{file_name}', encoding='utf-8') as f:
            my_dict = eval(f.readlines()[0])
            for key in my_dict:
                date_list = my_dict[key]
                if date_list is None:
                    date_list = []
                else:
                    # item_removed = True
                    # while item_removed:
                    #     item_removed = False
                    #     for x in date_list:
                    #         file = x['node']['file']
                    #         if file is None:
                    #             date_list.remove(x)
                    #             item_removed = True
                    #             break
                    # date_list = list(filter(lambda x: x['node']['file'] is not None, date_list))
                    date_list = list(map(lambda x: get_date_number_from_string(x['node']['committedDate'], '%Y-%m-%dT%H:%M:%SZ'), date_list))
                if key == '/data/parent/defaultBranchRef/target/root/edges':
                    parent_github_repo_dates.extend(date_list)
                else:
                    repo_dates.extend(date_list)
        if len(repo_dates) > 0:
            row = (user, file_name, get_date(min(parent_github_repo_dates)), get_date(min(repo_dates)))
        else:
            row = (user, file_name, get_date(min(parent_github_repo_dates)), None)
        rows.append(row)
    return rows


def increment(dict, key):
    if key in dict:
        dict[key] = dict[key] + 1
    else:
        dict[key] = 1


def get(dict, key):
    if key in dict:
        value = dict[key]
    else:
        value = 0
    return value


def moving_seurity_policies():
    no_repo_date_dict = dict()
    before_repo_date_dict = dict()
    after_repo_date_dict = dict()
    same_as_repo_date_dict = dict()

    contents = get_relevant_repo_contents()

    for i in range(len(contents)):
        user, _, parent_github_repo_date, repo_date = contents[i]
        if repo_date is None:
            increment(no_repo_date_dict, user)
        elif parent_github_repo_date < repo_date:
            increment(before_repo_date_dict, user)
        elif parent_github_repo_date > repo_date:
            increment(after_repo_date_dict, user)
        else:
            increment(same_as_repo_date_dict, user)

    users = set()
    users.update(no_repo_date_dict)
    users.update(before_repo_date_dict)
    users.update(after_repo_date_dict)
    users.update(same_as_repo_date_dict)
    users = sorted(users, key=str.casefold)

    for user in users:
        a = get(no_repo_date_dict, user)
        b = get(before_repo_date_dict, user)
        c = get(after_repo_date_dict, user)
        d = get(same_as_repo_date_dict, user)
        print(f'{user},{a + b + c + d},{a},{b},{c},{d}')


def get_parent_github_security_policy_commit_sha():
    my_list = []
    user_dict = get_user_dict(['.github/SECURITY.md'])
    for user in user_dict:
        for a in user_dict[user]:
            for b in a:
                repo = b[0]
                # if '.github' in repo:
                if b[5] == 0:
                    my_list.append((repo, b[2]))
    return my_list


def dummy():

    for row in csv_reader('C:\\Users\\Robert Wan\\Desktop\\New Text Document.csv'):
        if '#' in row[4]:
            result = re.search(r'#\d+', row[4])
            if result:
                result = result.group().replace('#', '')
                print(f'https://github.com/{row[0]}/pull/{result}')


def dummy_2(file_name):
    file_path = f'C:\\Files\\security policies\\{file_name}'
    content = get_latest_content(file_path)
    headers, paragraphs = get_headers_and_paragraphs(content)
    for header, paragraph in zip(headers, paragraphs):
        print(header)
        print()
        print(paragraph)
        print()


def get_repo_histories(is_short):
    repo_histories = []
    for repo, histories in get_file_path_list():
        date_diffs = [x[4] for x in histories]
        if is_short:
            indexes = [i for i in range(len(date_diffs)) if date_diffs[i] is not None and date_diffs[i].days == 0]
        else:
            indexes = [i for i in range(len(date_diffs)) if date_diffs[i] is not None and date_diffs[i].days > 0]
        histories = [histories[i] for i in range(len(histories)) if i in indexes]
        if len(histories) > 0:
            groups = []
            group = 0
            previous_date = None
            for history in histories:
                date = history[3]
                if previous_date is not None:
                    date_diff = date - previous_date
                    if date_diff.days != 0:
                        group = group + 1
                groups.append(group)
                previous_date = date
            repo_histories.append((repo, histories, groups))
    return repo_histories


def get_repo_histories_2(target_repo=None):
    repo_histories = []
    for repo, histories in get_file_path_list():
        if target_repo is None or repo == target_repo:
            if len(histories) > 0:
                groups = []
                group = 0
                previous_date = None
                for history in histories:
                    date = history[3]
                    if previous_date is not None:
                        if (date - previous_date).days != 0:
                            group = group + 1
                    groups.append(group)
                    previous_date = date
                repo_histories.append((repo, groups, histories))
    return repo_histories


def get_steps(s1, s2):
    m, n = len(s1), len(s2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(m + 1):
        dp[i][0] = i
    for j in range(n + 1):
        dp[0][j] = j
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            cost = 0 if s1[i - 1] == s2[j - 1] else 1
            dp[i][j] = min(dp[i - 1][j] + 1, dp[i][j - 1] + 1, dp[i - 1][j - 1] + cost)
    steps = []
    i, j = m, n
    while i > 0 and j > 0:
        if s1[i - 1] == s2[j - 1]:
            i, j = i - 1, j - 1
        elif dp[i][j] == dp[i - 1][j] + 1:
            steps.append(('Delete', s1[i - 1], i, None))
            i -= 1
        elif dp[i][j] == dp[i][j - 1] + 1:
            steps.append(('Insert', s2[j - 1], i, None))
            j -= 1
        else:
            steps.append(('Replace', s1[i - 1], i, s2[j - 1]))
            i -= 1
            j -= 1
    while i > 0:
        steps.append(('Delete', s1[i - 1], i, None))
        i -= 1
    while j > 0:
        steps.append(('Insert', s2[j - 1], i + 1, None))
        j -= 1
    return steps


def abc(aaa):
    for repo, histories in get_repo_histories(aaa):
        for a in histories:
            print_steps(repo, a)


def get_groups(a):
    my_dict = dict()
    # for b in a[2]:
    #     print((b[0],b[1],b[5], b[6]))
    # print(len(a[1]),len(a[2]))
    for b, c in zip(a[1], a[2]):
        if b in my_dict:
            my_dict[b].append(c)
        else:
            my_dict[b] = [c]
    return my_dict


def get_short_period_change_groups(my_dict):
    short_period_change_groups = []
    for key in my_dict:
        if my_dict[key] > 1:
            short_period_change_groups.append(key)
    return short_period_change_groups


def print_number_of_short_period_change_groups():
    for a in get_repo_histories_2():
        my_dict = get_groups(a)
        for k in my_dict:
            my_dict[k] = len(my_dict[k])
        changed = len(my_dict) > 1 or my_dict[0] > 1
        if changed:
            b = [int(x[7]) for x in a[2]]
            number_of_short_period_change_groups = len(get_short_period_change_groups(my_dict))
            print(f'{a[0]},{number_of_short_period_change_groups}')


def print_2():
    i = 0
    for a in get_repo_histories_2():
        my_dict = get_groups(a)
        changed = len(my_dict) > 1 or len(my_dict[0]) > 1
        if changed:
            i = i + 1
            print(f'{i}, {a[0]}, |{len(my_dict)}|')
            if a[0][0].lower() not in ['e']:
                continue
            for k in my_dict:
                # if k != 0 and len(my_dict[k]) > 1:
                # print((k, len(my_dict[k]), distance(my_dict[k][0][5], my_dict[k][-1][6])))
                for l in my_dict[k]:
                    steps = get_steps(l[5], l[6])
                    action_dict = dict()
                    for i in range(len(steps)):
                        action, _, _, _ = steps[i]
                        if action in action_dict:
                            action_dict[action] = action_dict[action] + 1
                        else:
                            action_dict[action] = 1
                    print((k, len(my_dict[k]), action_dict))


def get_action_dict(steps):
    action_dict = dict()
    for i in range(len(steps)):
        action, _, _, _ = steps[i]
        if action in action_dict:
            action_dict[action] = action_dict[action] + 1
        else:
            action_dict[action] = 1
    return action_dict


def get_nearest_header(content, k):
    header = []
    for i in reversed(range(0, k)):
        if content[i] == '#' and content[i - 1] in ['#', '\n']:
            print(f'FOUND FOUND {content[i - 1]}')
            for k in range(i + 1, len(content)):
                if content[k] == '\n':
                    break
                header.append(content[k])
            break
    return ''.join(list(filter(lambda x: x is not None, header))).strip()


def find_actual_change(repo=None):
    file_path = 'C:\\Files\\Projects\\actions_2.csv'
    writer = csv_writer(file_path, mode='w')
    repo_histories = get_repo_histories_2(repo)
    for repo_history in repo_histories:
        repo = repo_history[0]
        if repo not in ['laravel_framework.csv', 'webtorrent_webtorrent.csv', 'joomla_joomla-cms.csv', 'osgeo_gdal.csv', 'wintercms_winter.csv', 'spack_spack.csv', 'hedgedoc_hedgedoc.csv', 'sylius_sylius.csv', 'mybb_mybb.csv', 'tensorflow_tensorflow.csv', 'webtorrent_webtorrent-desktop.csv', 'Homebrew_brew.csv', 'blueimp_jQuery-File-Upload.csv', 'netdata_netdata.csv', 'standard_standard.csv', 'vitessio_vitess.csv', 'monkeytypegame_monkeytype.csv', 'vectordotdev_vector.csv', 'envoyproxy_envoy.csv', 'cveproject_cve-services.csv', 'domoticz_domoticz.csv', 'vuejs_router.csv', 'grpc_grpc-java.csv', 'near_nearcore.csv', 'opencontainers_umoci.csv', 'wordpress_wordpress-develop.csv', 'craftcms_cms.csv', 'notaryproject_notary.csv', 'projectcontour_contour.csv', 'uswds_uswds.csv', 'octobercms_october.csv', 'istio_envoy.csv', 'ballerina-platform_ballerina-lang.csv', 'cubefs_cubefs.csv', 'opencontainers_image-spec.csv', 'tinymce_tinymce.csv', 'twangboy_salt.csv', 'growthbook_growthbook.csv', 'LawnchairLauncher_lawnchair.csv', 'authelia_authelia.csv', 'gofiber_fiber.csv', 'rook_rook.csv', 'bytecodealliance_lucet.csv', 'star7th_showdoc.csv', 'saltstack_salt.csv', 'delgan_loguru.csv']:
            continue
        for history in repo_history[2]:
            date_time = history[3]
            old_content = history[5]
            new_content = history[6]
            steps = get_steps(old_content, new_content)
            content = [*old_content]
            offset = 0
            header_step_dict = dict()
            for j in reversed(range(len(steps))):
                action, c_1, k, c_2 = steps[j]
                k = k + offset
                if action == 'Insert':
                    content.insert(k, c_1)
                    offset = offset + 1
                elif action == 'Replace':
                    content[k - 1] = c_2
                elif action == 'Delete':
                    content[k - 1] = None
                header = get_nearest_header(content, k)
                if header in header_step_dict:
                    header_step_dict[header].append(steps[j])
                else:
                    header_step_dict[header] = [steps[j]]
            for header in header_step_dict:
                steps = header_step_dict[header]
                insert, replace, delete = get_action_distributions(get_action_dict(steps))
                row = [repo, date_time, header, insert, replace, delete]
                print(row)
                writer.writerow(row)


def check_changes():
    file_name_dict = dict()
    i = 0
    for row in csv_reader('C:\\Files\\Projects\\actions.csv'):
        i = i + 1
        file_name = row[0]
        date_time_string = row[1]
        header = row[2]
        number_of_inserts = int(row[3]) if len(row[3]) > 0 else 0
        number_of_replaces = int(row[4]) if len(row[4]) > 0 else 0
        number_of_deletes = int(row[5]) if len(row[5]) > 0 else 0
        # if number_of_inserts > number_of_deletes and number_of_inserts > 1:
        t = (i, header, number_of_inserts, number_of_replaces, number_of_deletes)
        if file_name in file_name_dict:
            date_time_string_dict = file_name_dict[file_name]
            if date_time_string in date_time_string_dict:
                date_time_string_dict[date_time_string].append(t)
            else:
                date_time_string_dict[date_time_string] = [t]
        else:
            date_time_string_dict = dict()
            date_time_string_dict[date_time_string] = [t]
            file_name_dict[file_name] = date_time_string_dict
    ccc = 0
    for file_name in file_name_dict:
        # if file_name == 'acheong08_ChatGPT.csv':
        if True:
            l = len(file_name_dict[file_name]) - 1
            ccc = ccc + l
            # if l > 0:
            print(f'{file_name},{l}')
            # date_time_string_dict = file_name_dict[file_name]
            # for date_time_string in date_time_string_dict:
            #     print(date_time_string_dict[date_time_string])
            #     print(f'{file_name} {date_time_string} {len(date_time_string_dict[date_time_string])}')
            #     print(f'- - - - - - - - - -')
            #     changes = file_name_dict[file_name][date_time_string]
            #     for i in range(1, len(changes)):
            #         header, number_of_inserts, number_of_replaces, number_of_deletes = changes[i]
            #         if ((number_of_inserts == 0 and number_of_replaces > 1 and number_of_deletes == 0) or
            #                 (number_of_inserts > 1 and number_of_inserts >= number_of_deletes)):
            #             print(changes[i])
            # aa = my_dict[repo][aaa]
    #         if len(aa) > 1:
    #             print(f'{aaa} {aa}]')
    print(ccc)


def get_file_name_dict():
    file_name_dict = dict()
    for row in csv_reader('C:\\Files\\Projects\\actions_3.csv'):
        file_name = row[0]
        date_time = get_date_time(row[1], '%Y-%m-%d %H:%M:%S%z')
        header = row[2]
        number_of_inserts = int(row[3]) if len(row[3]) > 0 else 0
        number_of_replaces = int(row[4]) if len(row[4]) > 0 else 0
        number_of_deletes = int(row[5]) if len(row[5]) > 0 else 0
        t = (header, number_of_inserts, number_of_replaces, number_of_deletes)
        if file_name in file_name_dict:
            date_time_string_dict = file_name_dict[file_name]
            if date_time in date_time_string_dict:
                date_time_string_dict[date_time].append(t)
            else:
                date_time_string_dict[date_time] = [t]
        else:
            date_time_string_dict = dict()
            date_time_string_dict[date_time] = [t]
            file_name_dict[file_name] = date_time_string_dict
    return file_name_dict


def check_changes():
    l = []
    file_name_dict = get_file_name_dict()
    for file_name in file_name_dict:
        l.append((file_name, len(file_name_dict[file_name]) - 1))
    return l



def aaa():
    l = []
    file_path_list = get_file_path_list()
    for file_name, a in file_path_list:
        l.append((file_name, len(a) - 1))
    return l


def get_reduced_numbers():
    l = check_changes()
    m = aaa()
    s = 0
    for file_name_1, count_1 in m:
        for file_name_2, count_2 in l:
            if file_name_1 == file_name_2:
                ans = abs(count_1 - count_2)
                if ans > 0:
                    print(f'{file_name_1},{ans}')
                    s = s + ans
    print(s)


def longest_common_subsequence(str1, str2):
    m, n = len(str1), len(str2)

    # Initialize a 2D array to store the length of LCS
    dp = [[0] * (n + 1) for _ in range(m + 1)]

    # Build the dp table
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if str1[i - 1] == str2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])

    # Reconstruct the LCS
    lcs = []
    i, j = m, n
    while i > 0 and j > 0:
        if str1[i - 1] == str2[j - 1]:
            lcs.append(str1[i - 1])
            i -= 1
            j -= 1
        elif dp[i - 1][j] > dp[i][j - 1]:
            i -= 1
        else:
            j -= 1

    # Reverse the LCS and convert it to a string
    lcs.reverse()

    return ''.join(lcs)


def get_repo_header_changes(file_name_dict, target_file_name=None):
    repo_header_changes = []
    for file_name in file_name_dict:
        my_dict = dict()
        if target_file_name is None or file_name == target_file_name:
            # apache_storm.csv
        # if file_name == 'zzzeek_sqlalchemy.csv':
            date_time_string_dict = file_name_dict[file_name]
            if len(date_time_string_dict) > 1:
                for date_time_string in date_time_string_dict:
                    actions = date_time_string_dict[date_time_string]
                    for action in actions:
                        header = fix_header(file_name, date_time_string, action[0].lower())
                        number_of_inserts = action[1]
                        number_of_replaces = action[2]
                        number_of_deletes = action[3]
                        if number_of_inserts >= number_of_deletes:
                            if header in my_dict:
                                my_dict[header].add(date_time_string)
                            else:
                                my_dict[header] = {date_time_string}
            previous_a = None
            for a in my_dict:
                if a != '' and len(my_dict[a]) > 1:
                    # if previous_a is not None and  a[:len(previous_a)] != previous_a:
                    if previous_a is not None and longest_common_subsequence(previous_a, a) != previous_a:
                        repo_header_changes.append((file_name, previous_a, list(my_dict[previous_a])))
                    # print(f'{file_name} {a} {my_dict[a]}')
                    previous_a = a
            if previous_a is not None:
                repo_header_changes.append((file_name, previous_a, list(my_dict[previous_a])))
    return repo_header_changes


def fix_header(file_name, date_time_string, header):
    # if len(a[1]) > 1:
    # if (')' in header and '(' not in header) or (')' not in header and '(' in header):
    #     print(f'{file_name} {date_time_string} {header}')
    #     if file_name == 'vectordotdev_vector.csv' and date_time_string in ['2020-02-01 23:29:30+00:00', '2021-07-31 16:19:32+00:00', '2020-12-12 03:30:29+00:00']:
    #         header = 'security policy'

    return header


def group_stuff():
    file_name_dict = get_file_name_dict()
    repo_header_changes = get_repo_header_changes(file_name_dict)
    my_dict = dict()
    for a in repo_header_changes:
        file_name = a[0]
        header = a[1]
        date_time_list = list(map(lambda x: get_date_time(x, '%Y-%m-%d %H:%M:%S%z'), a[2]))
        date_time_list.sort()
        previous_date_time = None
        date_delta_list = []
        for date_time in date_time_list:
            if previous_date_time is not None:
                date_delta = date_time - previous_date_time
                date_delta_list.append(date_delta.days)
            previous_date_time = date_time
        contain_long_period_changes = False
        contain_short_period_changes = False
        for a in date_delta_list:
            if a != 0:
                contain_long_period_changes = True
            if a == 0:
                contain_short_period_changes = True
        if contain_long_period_changes and contain_short_period_changes:
            # print(f'{file_name} {header} {date_delta_list}')
            if header in my_dict:
                my_dict[header].add(file_name)
            else:
                my_dict[header] = {file_name}
    for a in my_dict:
        print(f'{a} {my_dict[a]}')
    # for a in my_dict:
    #     my_dict[a] = len(my_dict[a])
    # total = 0
    # for a in sort_by_descending_values(my_dict):
    #     total = total + my_dict[a]
    #     print(f'"{a}",{my_dict[a]}')
    # print(total)


def merge_actions():
    replaced_repos = ['laravel_framework.csv', 'webtorrent_webtorrent.csv', 'joomla_joomla-cms.csv', 'osgeo_gdal.csv',
                    'wintercms_winter.csv', 'spack_spack.csv', 'hedgedoc_hedgedoc.csv', 'sylius_sylius.csv',
                    'mybb_mybb.csv', 'tensorflow_tensorflow.csv', 'webtorrent_webtorrent-desktop.csv',
                    'Homebrew_brew.csv', 'blueimp_jQuery-File-Upload.csv', 'netdata_netdata.csv',
                    'standard_standard.csv', 'vitessio_vitess.csv', 'monkeytypegame_monkeytype.csv',
                    'vectordotdev_vector.csv', 'envoyproxy_envoy.csv', 'cveproject_cve-services.csv',
                    'domoticz_domoticz.csv', 'vuejs_router.csv', 'grpc_grpc-java.csv', 'near_nearcore.csv',
                    'opencontainers_umoci.csv', 'wordpress_wordpress-develop.csv', 'craftcms_cms.csv',
                    'notaryproject_notary.csv', 'projectcontour_contour.csv', 'uswds_uswds.csv',
                    'octobercms_october.csv', 'istio_envoy.csv', 'ballerina-platform_ballerina-lang.csv',
                    'cubefs_cubefs.csv', 'opencontainers_image-spec.csv', 'tinymce_tinymce.csv', 'twangboy_salt.csv',
                    'growthbook_growthbook.csv', 'LawnchairLauncher_lawnchair.csv', 'authelia_authelia.csv',
                    'gofiber_fiber.csv', 'rook_rook.csv', 'bytecodealliance_lucet.csv', 'star7th_showdoc.csv',
                    'saltstack_salt.csv', 'delgan_loguru.csv']

    writer = csv_writer('C:\\Files\\Projects\\actions_3.csv', mode='w')
    for row in csv_reader('C:\\Files\\Projects\\actions.csv'):
        file_name = row[0]
        if file_name not in replaced_repos:
            writer.writerow(row)
    for row in csv_reader('C:\\Files\\Projects\\actions_2.csv'):
        writer.writerow(row)


def get_header_categorisation_that_is_empty():
    header_categories = dict()
    for row in csv_reader('C:\\Files\\Projects\\Header Categorisation.csv'):
        categories = list(filter(lambda x: len(x) > 0, row[2].split(',')))
        header_categories[row[0]] = categories

    file_name_dict = get_file_name_dict()
    repo_header_changes = get_repo_header_changes(file_name_dict)
    my_set = set()
    header_dict = dict()
    for a in repo_header_changes:
        k = a[1]
        if len(k) > 1:
            if k in header_categories:
                if header_categories[k] == []:
                    if k in header_dict:
                        header_dict[k].append(a[0])
                    else:
                        header_dict[k] = [a[0]]
            else:
                if k in header_dict:
                    header_dict[k].append(a[0])
                else:
                    header_dict[k] = [a[0]]
    for header in header_dict:
        print(f'"{header}","{header_dict[header]}",')


def get_nearest_header_categories():
    nearest_header_categories = []
    nearest_dict = dict()
    header_categories = dict()
    for row in csv_reader('C:\\Files\\Projects\\Header Categorisation.csv'):
        categories = list(filter(lambda x: len(x) > 0, row[2].split(',')))
        header_categories[row[0]] = categories
    for row in csv_reader('C:\\Files\\Projects\\Additional Header Categorisation.csv'):
        categories = list(filter(lambda x: len(x) > 0, row[1].split(',')))
        header_categories[row[0]] = categories
    for a in get_repo_header_changes(get_file_name_dict()):
        header = a[1]
        if len(header) > 1:
            file_name = a[0]
            categories = header_categories[header]
            date_time_list = a[2]
            date_time_list.sort()
            for i in range(1, len(date_time_list)):
                t = (date_time_list[i], categories)
                if file_name in nearest_dict:
                    nearest_dict[file_name].append(t)
                else:
                    nearest_dict[file_name] = [t]
    for file_name in nearest_dict:
        my_list = nearest_dict[file_name]
        my_list.sort(key=lambda x: x[0])
        for date_time, category in my_list:
            nearest_header_categories.append((file_name, date_time, category))
    return nearest_header_categories


def get_file_dict():
    file_dict = dict()
    header_categories = dict()
    for row in csv_reader('C:\\Files\\Projects\\Header Categorisation.csv'):
        categories = list(filter(lambda x: len(x) > 0, row[2].split(',')))
        header_categories[row[0]] = categories
    for row in csv_reader('C:\\Files\\Projects\\Additional Header Categorisation.csv'):
        categories = list(filter(lambda x: len(x) > 0, row[1].split(',')))
        header_categories[row[0]] = categories
    my_set = set()
    for a in get_repo_header_changes(get_file_name_dict()):
        header = a[1]
        if len(header) > 1:
            my_set.add(a[0])
            file_name = a[0]
            categories = header_categories[header]
            date_time_list = list(map(lambda x: get_date_time(x, '%Y-%m-%d %H:%M:%S%z'), a[2]))
            date_time_list.sort()
            for i in range(1, len(date_time_list)):
                key = date_time_list[i]
                values = (categories, header)
                if file_name in file_dict:
                    _, date_time_dict = file_dict[file_name]
                    if key in date_time_dict:
                        date_time_dict[key].append(values)
                    else:
                        date_time_dict[key] = [values]
                else:
                    date_time_dict = dict()
                    date_time_dict[key] = [values]
                    file_dict[file_name] = (date_time_list[0], date_time_dict)
    return file_dict


def section_categories():
    global_category_dict = dict()
    index = 0
    file_dict = get_file_dict()
    for file_name in file_dict:
        previous_date_time, date_time_dict = file_dict[file_name]
        date_time_list = list(date_time_dict.keys())
        date_time_list.sort()
        # print(file_name)
        # print(previous_date_time)
        for date_time in date_time_list:
            index = index + 1
            category_dict = dict()
            for categories, header in date_time_dict[date_time]:
                for category in categories:
                    if category in category_dict:
                        category_dict[category].append(header)
                    else:
                        category_dict[category] = [header]
            delta = (date_time - previous_date_time).days
            # print(f'{index} {date_time} {delta} {category_dict}')
            for category in category_dict:
                if category in global_category_dict:
                    for header in category_dict[category]:
                        global_category_dict[category].append((header, date_time, delta, file_name))
                else:
                    a = []
                    for header in category_dict[category]:
                        a.append((header, date_time, delta, file_name))
                    global_category_dict[category] = a
            previous_date_time = date_time
    for category in global_category_dict:
        count_dict = dict()
        # for header in global_category_dict[category]:
        #     if header in count_dict:
        #         count_dict[header] = count_dict[header] + 1
        #     else:
        #         count_dict[header] = 1
        # count_dict = sort_by_descending_values(count_dict)
        # # print(f'{category} {len(global_category_dict[category])} {count_dict}')
        changes = global_category_dict[category]
        for change in changes:
            print(change)
        # s_p_changes = [(x[0], x[3]) for x in changes if x[2] == 0]
        # l_p_changes = [x for x in changes if x[2] > 0]

        # print(f'"{category}",{len(lll)},{len(short_period_changes)},{len(short_period_changes)/len(lll)}')
        # print(f'"{category}",{len(changes)},{len(l_p_changes)},{len(l_p_changes) / len(changes)}')
        # print(f'"{category}",{s_p_changes}')
    return global_category_dict



def get_changes(file_name, date_time, title):
    file_path = f'C:\\Files\\security policies\\{file_name}'
    print(f'{file_path}')
    print(f'{date_time}')
    print(f'{title}')
    for row in csv_reader(file_path):
        if f'{date_time}' == row[3]:
            s = ''
            steps = get_steps(row[4], row[5])
            for i in reversed(range(len(steps))):
                s = s + steps[i][1]
            s = s.strip()
            print(f'STRING: {s}')
    print()

def section_categories_2():
    # category_dict = section_categories()
    # for category in category_dict:
    #     changes = category_dict[category]
    #     s_p_changes = [x for x in changes if x[2] == 0]
    #     l_p_changes = [x for x in changes if x[2] > 0]
    #     print(f'{category}')
    #     for aaa in s_p_changes:
    #         get_changes(aaa[3], aaa[1], aaa[0])
    #     break

    original_string = "Hello, this is a common substring, my friend."
    lcs = " common substring"

    substrings = original_string.split(lcs)
    # Join the substrings to create a new string without the LCS
    result = ''.join(substrings)
    print(f'AAAAA {result}')


def get_tf_list(sentences):
    tf_list = []
    for sentence in sentences:
        words = sentence.split(' ')
        tf = dict()
        for word in words:
            if word in tf:
                tf[word] = tf[word] + 1
            else:
                tf[word] = 1
        for word in tf:
            tf[word] = tf[word] / len(words)
        tf_list.append(tf)
    return tf_list


def get_idf_dict(sentences):
    idf_dict = dict()
    words = set()
    for sentence in sentences:
        words.update(sentence.split(' '))
    number_of_sentences = len(sentences)
    for word in words:
        count = 0
        for sentence in sentences:
            if word in sentence:
                count = count + 1
        idf_dict[word] = math.log10(number_of_sentences / count)
    return idf_dict


lemmatizer = WordNetLemmatizer()
stemmer = PorterStemmer()
stop_words = set(stopwords.words('english'))


def get_tf_idf_keywords(size, threshold):
    directory_path = 'C:\\Files\\security policies\\'
    file_dict = dict()
    word_dict = dict()
    for file_name in os.listdir(directory_path):
        contents = get_contents(directory_path, file_name)
        for i in range(0, len(contents)):
            date_time_string = contents[i][3]
            content = cccc(file_name, contents[i][5])
            t = (file_name, date_time_string, content)
            if file_name in file_dict:
                file_dict[file_name].append(t)
            else:
                file_dict[file_name] = [t]
    for file_name in file_dict:
        # if 'react' in file_name:
            print_td_idf(file_dict[file_name], word_dict)
    count_word_dict = dict()
    for word in word_dict:
        count = 0
        for key in word_dict[word]:
            count = count + len(word_dict[word][key])
        if count in count_word_dict:
            count_word_dict[count].append(word)
        else:
            count_word_dict[count] = [word]
    my_set = list(count_word_dict.keys())
    my_set.sort(reverse=True)
    my_set = my_set[:size]
    # print(my_set)
    keywords = []
    for count in my_set:
        for word in word_dict:
            if word in count_word_dict[count]:
                file_dict = word_dict[word]
                s_p_c_count = 0
                l_p_c_count = 0
                for file_name in file_dict:
                    date_time_string_list = file_dict[file_name]
                    date_times = list(map(lambda x: get_date_time(x, '%Y-%m-%d %H:%M:%S%z'), date_time_string_list))
                    date_times.sort()
                    date_time_delta_list = []
                    previous_date_time = None
                    for date_time in date_times:
                        if previous_date_time is not None:
                            date_time_delta = date_time - previous_date_time
                            date_time_delta_list.append(date_time_delta.days)
                        previous_date_time = date_time
                    # print(f'{word} {file_name} {date_time_string_list} {date_time_delta_list}')
                    s_p_c_count = s_p_c_count + len([x for x in date_time_delta_list if x == 0])
                    l_p_c_count = l_p_c_count + len([x for x in date_time_delta_list if x > 0])
                if count >= threshold:
                    # print((word, count, s_p_c_count, l_p_c_count))
                    keywords.append(word)
    # print(keywords)
    return keywords


def cccc(file_name, content):
    repo = file_name.replace('.csv', '').replace('_', '/', 1)
    slices = repo.split('/')
    user = slices[0]
    project = slices[1]
    content = re.sub(r'<!--(.*?)-->', '', content, flags=re.DOTALL)
    content = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b', '', content)
    content = re.sub(r'(https?://\S+|www\.\S+|\b\w+\.\w{2,6}\S*)', '', content)
    content = content.lower()
    content = content.replace(user, '')
    content = content.replace(project, '')
    content = re.sub(r'[\u4e00-\u9fff]+', '', content)
    content = re.sub(r'\W+', ' ', content)
    content = re.sub(r'\d+', '', content)
    content = content.split()
    content = [x for x in content if x not in stop_words]
    content = [x for x in content if len(x) > 2]
    # content = list(map(lambda x: lemmatizer.lemmatize(x, 'v'), content))
    content = list(map(lambda x: stemmer.stem(x), content))
    content = ' '.join(content).strip()
    return content


def print_td_idf(changes, word_dict):
    sentences = [x[2] for x in changes]
    tf_list = get_tf_list(sentences)
    idf_dict = get_idf_dict(sentences)
    for i in range(len(changes)):
        word_list = [(word, tf_list[i][word] * idf_dict[word]) for word in tf_list[i]]
        word_list = list(filter(lambda x: len(x[0]) > 1 and x[1] > 0, word_list))
        word_list.sort(key=lambda x: x[1], reverse=True)
        # print((i, changes[i][0], changes[i][1], len(word_list), word_list))

        for word in word_list:
            file_name = changes[i][0]
            # t = get_date_time(changes[i][1], '%Y-%m-%d %H:%M:%S%z')
            t = changes[i][1]
            if word[0] in word_dict:
                if file_name in word_dict[word[0]]:
                    word_dict[word[0]][file_name].append(t)
                else:
                    word_dict[word[0]][file_name] = [t]
            else:
                file_dict = dict()
                file_dict[file_name] = [t]
                word_dict[word[0]] = file_dict


def keyword_search():
    # keywords = ['vulner', 'possibl', 'email', 'version', 'issu', 'use', 'see', 'time', 'bug', 'public', 'pleas', 'report', 'secur', 'depend', 'polici', 'includ', 'fix', 'follow', 'affect', 'take', 'make', 'help', 'request', 'relat', 'work', 'releas', 'project', 'support', 'respons', 'open', 'access', 'inform', 'disclosur', 'code', 'send', 'find']
    # keywords = ['vulner', 'possibl', 'email', 'version', 'issu', 'use', 'see', 'time', 'bug', 'public', 'pleas', 'report', 'secur', 'depend', 'polici', 'includ', 'fix', 'follow', 'affect', 'take', 'make', 'help', 'request', 'relat', 'work', 'releas', 'project', 'support', 'respons', 'open', 'access', 'inform', 'disclosur', 'code', 'send', 'find', 'attack', 'github', 'user', 'file', 'within', 'sourc', 'impact', 'found', 'maintain', 'via', 'get', 'avail', 'current', 'requir', 'process', 'scope', 'repositori', 'discov', 'receiv', 'exploit', 'team', 'develop', 'sever', 'document', 'updat', 'address', 'ensur', 'detail', 'instead', 'manag', 'one', 'privat', 'softwar', 'submit', 'step', 'limit', 'commun', 'way', 'patch', 'serious', 'white_check_mark', 'valid', 'provid', 'also', 'us', 'triag', 'keep', 'like', 'reproduc', 'necessari', 'well', 'may', 'gener', 'note', 'potenti', 'program', 'first', 'case', 'key', 'everi', 'quickli', 'configur', 'resolv', 'directli', 'publicli', 'advisori', 'believ', 'servic', 'appropri', 'data', 'need', 'latest', 'creat', 'much', 'non', 'inject', 'featur', 'howev', 'bounti', 'exampl', 'contact', 'list', 'coordin', 'import', 'page', 'platform', 'mitig', 'allow', 'thank', 'type', 'contain', 'local', 'safe', 'discuss', 'without', 'day', 'commit']

    keywords = get_tf_idf_keywords(300, 100)

    results = []

    directory_path = 'C:\\Files\\security policies\\'
    for file_name in os.listdir(directory_path):
        contents = get_contents(directory_path, file_name)
        used_keywords = set()
        for i in range(0, len(contents)):
            content = cccc(file_name, contents[i][5])
            matched_keywords = []
            for keyword in keywords:
                if keyword in content:
                    matched_keywords.append(keyword)
            if len(matched_keywords) > 0:
                current_keywords = []
                for keyword in matched_keywords:
                    if keyword not in used_keywords:
                        current_keywords.append(keyword)
                if i > 0:
                    # print(f'{file_name} {contents[i][3]} {current_keywords}')
                    if len(current_keywords) > 0:
                        current_keywords.sort()
                        results.append(current_keywords)
            used_keywords.update(matched_keywords)
    return results


def print_nearest_header_categories():
    for a in get_nearest_header_categories():
        print(a)



def get_keywords():
    changes = []
    csv_file_path = 'C:\\Files\\preprocess_4.csv'
    for file_name, sha, date_time_string, tf_idf_list in csv_reader(csv_file_path):
        tf_idf_list = eval(tf_idf_list)
        date_time = get_date_time(date_time_string, '%Y-%m-%d %H:%M:%S%z')
        changes.append((file_name, sha, date_time, tf_idf_list))
    return changes


def print_category_keywords():
    nearest_header_categories = get_nearest_header_categories()
    keywords = get_keywords()
    category_dict = dict()
    for n in nearest_header_categories:
        file_name_1 = n[0]
        date_time_1 = n[1]
        categories = n[2]
        terms = []
        for keyword in keywords:
            file_name_2 = keyword[0]
            date_time_2 = keyword[2]
            tf_idf_list = keyword[3]
            if file_name_1 == file_name_2 and date_time_1 == date_time_2:
                for term in tf_idf_list:
                    terms.append(term[0])
        # print((file_name_1, categories, terms))
        for category in categories:
            if category in category_dict:
                category_dict[category].extend(terms)
            else:
                term_list = []
                term_list.extend(terms)
                category_dict[category] = term_list

    for category in category_names:
        keywords = Counter(category_dict[category]).most_common(10)
        keywords = [f'{x[0]}' for x in keywords]
        keywords = ', '.join(keywords)
        print(f'{category},"{keywords}"')


def print_search_results():
    a = get_nearest_header_categories()

    repo_dict = dict()

    for b in a:
        repo = b[0]
        if 'Scope' in b[2]:
            date_time_string = f'{b[1]}'
            if repo in repo_dict:
                repo_dict[repo].append(date_time_string)
            else:
                repo_dict[repo] = [date_time_string]
    my_set = set()
    owasp = [
        'broken access control',
        'broken authentication and session management',
        'cross-site scripting',
        'xss',
        'cryptographic failures',
        'identification and authentication failures',
        'injection',
        'insecure deserialization',
        'insecure design',
        'insufficient logging & monitoring',
        'security logging and monitoring failures',
        'security misconfiguration',
        'sensitive data exposure',
        'server-side request forgery',
        'ssrf',
        'software and data integrity failures',
        'using components with known vulnerabilities',
        'vulnerable and outdated components',
        'xml external entities',
        'xxe'
    ]

    # cve_pattern = r'cve-\d{4}-\d{5}'
    #
    for repo in repo_dict:
        date_time_strings = repo_dict[repo]
        for row in csv_reader(f'C:\\Files\\security policies\\{repo}'):
            date_time_string = row[3]
            content = row[5].lower()
            if date_time_string in date_time_strings:
                if 'cve' in content:
                    my_set.add(repo)

                # cve_matches = re.findall(cve_pattern, content)
                # # if len(cve_matches) > 0:
                # #     print(repo)
                # for cve in cve_matches:
                #     print(cve)


                # if 'time' in content:
                #     print(f'{repo} {date_time_string}')

                # if 'cwe' in content:
                #     my_set.add(repo)
                # for ioc in owasp:
                #     if ioc in content:
                #         my_set.add(repo)


    for repo in repo_dict:
        print(f'{repo} {repo_dict[repo]}')

    print(len(repo_dict))

        # if len(date_time_strings) != len(list):
        #     print(f'{repo} {len(date_time_strings)} {len(list)} {date_time_strings}')
        # print(f'{repo} {repo_dict[repo]}')


def print_scope():
    a = get_nearest_header_categories()
    repo_dict = dict()
    for b in a:
        repo = b[0]
        if 'Scope' in b[2]:
            date_time_string = f'{b[1]}'
            if repo in repo_dict:
                repo_dict[repo].append(date_time_string)
            else:
                repo_dict[repo] = [date_time_string]
    my_set = set()
    for repo in repo_dict:
        date_time_strings = repo_dict[repo]
        for row in csv_reader(f'C:\\Files\\security policies\\{repo}'):
            date_time_string = row[3]
            content = row[5].lower()
            if date_time_string in date_time_strings:
                if 'out of scope' in content or 'out-of-scope' in content:
                    my_set.add(repo)
                    print((repo, date_time_string))



    print(len(my_set))



def get_user_repository_count_dict():
    user_repository_count_dict = dict()
    directory_paths = [
        'C:\\Files\\Projects\\User repositories\\',
        'C:\\Files\\Projects\\User repositories 2\\'
    ]
    for directory_path in directory_paths:
        for file_name in os.listdir(directory_path):
            user = file_name.replace('.txt', '').lower()
            with open(f'{directory_path}{file_name}') as f:
                lines = f.readlines()
                count = len(eval(lines[0]))
                if count == 0:
                    count = 1
                user_repository_count_dict[user] = count
    return user_repository_count_dict
#
def get_parent_github_users():
    user_set = set()
    directory_path = 'C:\\Files\\security policies\\'
    for file_name in os.listdir(f'{directory_path}'):
        repo = file_name.replace('.csv', '').replace('_', '/', 1)
        slices = repo.split('/')
        user = slices[0]
        contents = []
        i = 0
        for row in csv_reader(f'{directory_path}{file_name}'):
            if i > 0:
                contents.append((row[0], len(row[5])))
            i = i + 1
        for i in reversed(range(len(contents))):
            path, content_length = contents[i]
            if path == f'{user}/.github' and content_length > 0:
                user_set.add(user.lower())
                break
    user_set.add('julialang')
    return user_set


def get_moved_to_parent_github_users():
    user_set = set()
    directory_path = 'C:\\Files\\Projects\\User repositories\\'
    for file_name in os.listdir(directory_path):
        user_set.add(file_name.replace('.txt', '').lower())
    return user_set


def print_user_repositories_after():
    counts = []
    directory_path = 'C:\\Files\\Projects\\User repositories 2\\'
    for file_name in os.listdir(directory_path):
        with open(f'{directory_path}{file_name}') as f:
            lines = f.readlines()
            counts.append(len(eval(lines[0])))
    return counts


def my_mann_users():
    user_repository_count_dict = get_user_repository_count_dict()
    counts = []
    for key in user_repository_count_dict:
        counts.append(user_repository_count_dict[key])


    # counts.sort()
    # counts = counts[:int(len(counts)*0.8)]

    print(len([x for x in counts if x > 1]))

    print(len(counts))
    print(counts)
    print(sum(counts))
    print(min(counts))
    print(average(counts))
    print(median(counts))
    print(max(counts))
    box_plot([counts], 'W:\\My Drive\\UniMelb\\Research Project\\Diagrams\\User repositories.png')



def my_mann():
    user_repository_count_dict = get_user_repository_count_dict()
    users = set(user_repository_count_dict.keys())
    parent_github_users = get_parent_github_users()
    moved_to_parent_github_users = get_moved_to_parent_github_users()
    user_counts = []
    for user in users - parent_github_users - moved_to_parent_github_users:
        user_counts.append(user_repository_count_dict[user])
    parent_github_user_counts = []
    for user in parent_github_users - moved_to_parent_github_users:
        parent_github_user_counts.append(user_repository_count_dict[user])
    moved_to_parent_github_user_counts = []
    for user in moved_to_parent_github_users:
        moved_to_parent_github_user_counts.append(user_repository_count_dict[user])
    print((len(user_counts), len(parent_github_user_counts), len(moved_to_parent_github_user_counts)))
    print()
    print(stats.mannwhitneyu(user_counts, parent_github_user_counts))
    print(compute_mann_whitney_effect_size(user_counts, parent_github_user_counts))
    print()
    print(stats.mannwhitneyu(user_counts, moved_to_parent_github_user_counts))
    print(compute_mann_whitney_effect_size(user_counts, moved_to_parent_github_user_counts))
    print()
    print(stats.mannwhitneyu(parent_github_user_counts, moved_to_parent_github_user_counts))
    print(compute_mann_whitney_effect_size(parent_github_user_counts, moved_to_parent_github_user_counts))


def search_my_keywords():

    repo_histories = get_repo_histories(True)

    i = 0
    file_name_set = set()
    for file_name, histories, _ in repo_histories:
        file_name_set.add(file_name)
        # for history in histories:
        #     content = history[6]
        #     cve_pattern = r'CVE-\d{4}-\d{4,7}'
        #     cve_numbers = re.findall(cve_pattern, content)
        #     if len(cve_numbers) > 0:
        #         i = i + 1
        #         for cve in cve_numbers:
        #             print(f'{i} {repo} {cve}')
        #             repo_set.add(repo)

    cve_set = set()
    directory_path = 'C:\\Files\\security policies\\'
    cve_pattern = r'CVE-\d{4}-\d{4,7}'
    for file_name in file_name_set:
        contents = get_contents(directory_path, file_name)
        if file_name in file_name_set:
            for i in range(0, len(contents)):
                cve_numbers = re.findall(cve_pattern, contents[i][5])
                if len(cve_numbers) > 0:
                    for cve in cve_numbers:
                        cve_set.add(cve)
    print(list(cve_set))
    # for cve in cve_set:
    #     print(cve)


def print_cve_mappings():
    cve_list = ['CVE-2018-18444', 'CVE-2008-5619', 'CVE-2022-29577', 'CVE-2020-36326', 'CVE-2010-0005', 'CVE-2002-0771', 'CVE-2017-7555', 'CVE-2008-1292', 'CVE-2016-10045', 'CVE-2022-21476', 'CVE-2021-3479', 'CVE-2021-45942', 'CVE-2004-1062', 'CVE-2017-9112', 'CVE-2005-1807', 'CVE-2017-11464', 'CVE-2012-4533', 'CVE-2018-19296', 'CVE-2022-24725', 'CVE-2020-15304', 'CVE-2008-1290', 'CVE-2009-5024', 'CVE-2010-4914', 'CVE-2017-15026', 'CVE-2020-35906', 'CVE-2019-15551', 'CVE-2006-5442', 'CVE-2020-14621', 'CVE-2019-20446', 'CVE-2009-3618', 'CVE-2020-16588', 'CVE-2022-31180', 'CVE-2021-34551', 'CVE-2020-16587', 'CVE-2017-12596', 'CVE-2020-11763', 'CVE-2020-11765', 'CVE-2020-15272', 'CVE-2016-7099', 'CVE-2010-0004', 'CVE-2013-5960', 'CVE-2009-3619', 'CVE-2012-3356', 'CVE-2022-25918', 'CVE-2022-36064', 'CVE-2020-15305', 'CVE-2020-13625', 'CVE-2017-11503', 'CVE-2020-11764', 'CVE-2009-1720', 'CVE-2021-20296', 'CVE-2020-11761', 'CVE-2010-0132', 'CVE-2009-1721', 'CVE-2020-11759', 'CVE-2021-3476', 'CVE-2021-3603', 'CVE-2020-11758', 'CVE-2021-3478', 'CVE-2016-4630', 'CVE-2016-2216', 'CVE-2022-28367', 'CVE-2017-14988', 'CVE-2021-3474', 'CVE-2022-21449', 'CVE-2021-3475', 'CVE-2012-3357', 'CVE-2017-5223', 'CVE-2016-2074', 'CVE-2021-3477', 'CVE-2020-11760', 'CVE-2020-1887', 'CVE-2019-17571', 'CVE-2019-15554', 'CVE-2006-2277', 'CVE-2011-3747', 'CVE-2008-1291', 'CVE-2017-14735', 'CVE-2020-16589', 'CVE-2018-1000827', 'CVE-2017-9111', 'CVE-2017-12852', 'CVE-2022-36049', 'CVE-2018-20991', 'CVE-2017-9114', 'CVE-2008-4325', 'CVE-2022-31179', 'CVE-2022-24877', 'CVE-2021-35043', 'CVE-2021-41254', 'CVE-2021-25900', 'CVE-2020-15306', 'CVE-2021-42550', 'CVE-2015-8476', 'CVE-2016-10033', 'CVE-2007-3215', 'CVE-2017-15028', 'CVE-2021-21384', 'CVE-2004-0915', 'CVE-2021-34433', 'CVE-2022-2576', 'CVE-2017-9113', 'CVE-2006-5734', 'CVE-2017-9116', 'CVE-2022-28366', 'CVE-2022-36035', 'CVE-2013-5679', 'CVE-2022-25647', 'CVE-2022-24878', 'CVE-2022-39368', 'CVE-2010-0736', 'CVE-2017-9115', 'CVE-2017-9110', 'CVE-2005-4831', 'CVE-2020-11762', 'CVE-2020-27222', 'CVE-2016-10006', 'CVE-2020-29311', 'CVE-2016-4629', 'CVE-2022-29546', 'CVE-2012-0796', 'CVE-2023-26119', 'CVE-2022-24817', 'CVE-2005-4830', 'CVE-2020-35905', 'CVE-2018-18443', 'CVE-2007-2021', 'CVE-2009-1722', 'CVE-2017-15027']
    cve_cwe_dict = dict()
    for a in get_list():
        cve_cwe_dict[a[0]] = eval(a[6])
    owasp_cwe_dict = get_owasp_cwe_dict()
    i = 0
    # 125 CVEs
    # 97 CVEs can map
    # 51 Owasp

    owasp_dict = dict()
    for cve in cve_list:
        if cve in cve_cwe_dict:
            cwe_list = cve_cwe_dict[cve]
            owasp_list = []
            for cwe in cwe_list:
                if cwe in owasp_cwe_dict:
                    owasp_set = owasp_cwe_dict[cwe]
                    # print(owasp_set)
                    owasp_list.append(owasp_set)
                    for owasp in owasp_set:
                        if owasp in owasp_dict:
                            owasp_dict[owasp] = owasp_dict[owasp] + 1
                        else:
                            owasp_dict[owasp] = 1

            if len(cwe_list) > 0 and len(owasp_list) > 0:
                i = i + 1
                print(f'{i} {cve} {cwe_list} {owasp_list}')

    for owasp in owasp_dict:
        print(f'"{owasp}",{owasp_dict[owasp]}')








    # directory_path = 'C:\\Files\\security policies\\'
    # j = 0
    # for file_name in os.listdir(directory_path):
    #     contents = get_contents(directory_path, file_name)
    #     for i in range(0, len(contents)):
    #         # content = cccc(file_name, contents[i][5])
    #         content = contents[i][5]
    #         # if 'cve' in content:
    #         cve_pattern = r'CVE-\d{4}-\d{4,7}'
    #         cve_numbers = re.findall(cve_pattern, content)
    #         j = j + 1
    #         for cve in cve_numbers:
    #             # print('Hello World')
    #             print(f'{j} {file_name} {cve}')



if __name__ == '__main__':
    # print_number_of_changes()
    # print_move_patterns(as_count=True)
    # print_repo_histories()
    # print_changes_all_made_within_one_day()
    # print_insert_replace_delete()
    # print_common_change_actions()
    # print_short_period_changes()
    # print_long_period_changes()
    # abc(False)
    # print_number_of_short_period_change_groups()
    # print_2()
    # find_actual_change()
    # get_reduced_numbers()
    # section_categories()
    # section_categories_2()
    # print_nearest_header_categories()
    # print_category_keywords()
    # print_search_results()
    # print_scope()

    # print_analysis_3()

    # my_mann_users()
    # my_mann()


    # count_dict = dict()
    #
    # results = keyword_search()
    # for result in results:
    #     for word in result:
    #         if word in count_dict:
    #             count_dict[word] = count_dict[word] + 1
    #         else:
    #             count_dict[word] = 1
    #
    # for k in sort_by_descending_values(count_dict):
    #     print(f'{k} {count_dict[k]}')
    #
    # search_my_keywords()
    print_cve_mappings()

    # my_dict = dict()
    # print_td_idf([
    #     ('', '2023-10-16', 'good boy'),
    #     ('tensorflow_tensorflow.csv', '2023-10-13', 'good girl'),
    #     ('tensorflow_tensorflow.csv', '2023-10-14', 'boy girl good'),
    #     ('', '2023-10-14', 'i live in hong kong'),
    #     ('', '2023-10-15', 'i go to school good by bus')
    # ], my_dict)
    # for a in my_dict:
    #     print(f'{a} {my_dict[a]}')

        # header = a[1]
        # if (')' in header and '(' not in header) or (')' not in header and '(' in header):
        #     my_set.add(a[0])
    # print(list(my_set))



    # security_policies_before()
    # moving_seurity_policies()
    # a = get_parent_github_security_policy_commit_sha()
    # for b in a:
    #     print(b)