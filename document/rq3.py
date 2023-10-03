import difflib
import os
import re
from datetime import datetime

from Levenshtein import distance
from numpy import average, median, ceil

from chart import scatter_plot, box_plot
from document.document_categorisation_all import get_repo_categorisation_results, get_repo_header_paragraph_categories
from document.document_utils import get_headers_and_paragraphs
from utils import csv_reader, sort_by_descending_values, get_latest_content


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
    for key in keys:
        count = len(content_dict[key])
        total = total + count
        print(f'{key},{count},{content_dict[key]}')
    print(total)


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


def print_repo_histories_all_made_within_one_day():
    file_path_list = get_file_path_list()
    i = 0
    for repo, histories in file_path_list:
        if len(histories) > 1:
            dates = [x[3] for x in histories]
            content_lengths = [len(x[5]) for x in histories]
            distances = [x[6] for x in histories]
            date_diff = max(dates) - min(dates)
            if date_diff.days == 0:
                i = i + 1
                print(f'{i},{repo},{content_lengths},{distances}')


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


def print_long_period_changes():
    count = 0
    changes = []
    values = []
    for repo, histories in get_repo_histories(False):
        count = count + 1
        delta_list = [x[4].days + x[4].seconds / 3600 / 24 for x in histories]
        change = len(histories)
        changes.append(change)
        value = average(delta_list)
        values.append(value)
        print(f'{count},{repo},{change},{delta_list},{value}')
    print(f'- - - - - - - - - -  {median(changes)} {average(changes)} {median(values)} {average(values)}')
    box_plot([changes], 'W:\\My Drive\\UniMelb\\Research Project\\Diagrams\\RQ3\\Long Period Changes 1.png')
    box_plot([values], 'W:\\My Drive\\UniMelb\\Research Project\\Diagrams\\RQ3\\Long Period Changes 2.png')


def print_short_period_changes():
    count = 0
    changes = []
    values = []
    for repo, histories in get_repo_histories(True):
        count = count + 1
        delta_list = [x[4].seconds / 3600 for x in histories]
        change = len(histories)
        changes.append(change)
        value = average(delta_list)
        values.append(value)
        print(f'{count},{repo},{change},{delta_list},{value}')
    print(f'- - - - - - - - - {median(changes)} {average(changes)} {median(values)} {average(values)}')
    box_plot([changes], 'W:\\My Drive\\UniMelb\\Research Project\\Diagrams\\RQ3\\Short Period Changes 1.png')
    box_plot([values], 'W:\\My Drive\\UniMelb\\Research Project\\Diagrams\\RQ3\\Short Period Changes 2.png')


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
            repo_histories.append((repo, histories))
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


if __name__ == '__main__':
    # print_number_of_changes()
    # print_move_patterns(as_count=True)
    # print_repo_histories_all_made_within_one_day()
    # print_repo_histories()
    # print_short_period_changes()
    # print_long_period_changes()

    count = 0
    for repo, histories in get_repo_histories(True):
        count = count + 1
        # print('- - - - - - - - - -')
        # print(count)
        print(f'C:\\Files\\security policies\\{repo}')
        if repo == 'apache_storm.csv':
            continue
        for a in histories:
            steps = get_steps(a[5], a[6])
            action_dict = dict()
            for i in range(len(steps)):
                action, _, _, _ = steps[i]
                if action in action_dict:
                    action_dict[action] = action_dict[action] + 1
                else:
                    action_dict[action] = 1
            print(f'{action_dict} {(a[0],a[1],a[2],a[3],a[4],len(a[5]),len(a[6]))}')




    # dummy_2('activerecord-hackery_ransack.csv')

    # repo_categorisation_results = get_repo_header_paragraph_categories()
    #
    # for result in repo_categorisation_results:
    #     print(result)


    # security_policies_before()
    # moving_seurity_policies()
    # a = get_parent_github_security_policy_commit_sha()
    # for b in a:
    #     print(b)