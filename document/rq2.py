import datetime
import itertools
import math
import os
import statistics
import sys

import pandas as pd
from scipy import stats
from scipy.stats import spearmanr, skew, pointbiserialr, chi2_contingency, chi2, fisher_exact

from dependency import get_package_manager_dict, get_repo_xx
from document.document_categorisation_all import get_repo_categorisation_results
from document.document_utils import category_names
from document.my_statistics import compute_mann_whitney_effect_size, compute_group_sign, compute_spearman_sign
from document.owasp import get_owasp_cwe_dict, get_owasp_description_dict
from security_md import get_number_of_characters_words_headers_paragraphs
from utils import repos, attribute_file_path, csv_reader, expand, get_writer, \
    sort_by_descending_values, get_column_title_and_values, get_grouped_column_title_and_values, \
    get_security_policy_repo, repo_2

ALPHA = 0.05


def a(vertical, horizontal, number_ranges):
    pass
    # if type(horizontal) == int:
        # compute_data_frames((vertical, None, None, None, None, number_ranges), [horizontal])
        # df = get_data_frame((vertical, None, None, None, None, number_ranges), [horizontal])
    # else:
        # df = get_data_frame((vertical, None, None, None, None, number_ranges), [(horizontal[0], None, horizontal[1])])
    # print(df)


def nr(numbers):
    number_ranges = []
    numbers.sort()
    number_length = len(numbers)
    end = None
    for i in range(number_length):
        if i == 0:
            start = 0
            end = numbers[i]
        else:
            start = numbers[i - 1] + 1
            end = numbers[i]
        if start == end:
            number_ranges.append((start, end, f'{start}'))
        else:
            number_ranges.append((start, end, f'{start} - {end}'))
    if end is not None:
        start = end + 1
        end = sys.maxsize
        number_ranges.append((start, end, f'{start} or above'))
    return number_ranges


# def group_contents(contents, groups=[]):
#     content_length = len(contents)
#     if content_length > 0:
#         content_results = [0] * content_length
#         for i in range(content_length):
#             content_results[i] = distance(contents[0][1], contents[i][1])
#         matched_contents = []
#         remaining_contents = []
#         for i in range(content_length):
#             if content_results[i] == 0:
#                 matched_contents.append(contents[i])
#             elif content_results[i] > 0:
#                 remaining_contents.append(contents[i])
#         groups.append(matched_contents)
#         return group_contents(remaining_contents, groups)
#     else:
#         return groups


# def ddd():
    # repos(get_content, my_dict, 0, directory_path)





    #
    #

    # print(total)


    # a_dict = dict()
    # for key in my_dict:
    #     # if key == 'microsoft':
    #         # content_results = []
    #         # base_content = None
    #         # print(my_dict[key])
    #     group_contents_2(my_dict, key, a_dict)
    #
    # for content in a_dict:
    #     user_set = set()
    #     for t in a_dict[content]:
    #         user_set.add(t[0])
    #     if len(user_set) > 1:
    #         print(a_dict[content])

                # print('AAAAAAAAAA')
                # print(list(map(lambda x: x[1], t))[0])
            # for group in group_contents(my_dict[key]):

            #     if len(group) > 0:
                    # if base_content is None:
                    #     base_content = group[0]
                    # d = distance(base_content[1], group[0][1])
                    # print(f'AAAAA {d}')
                    # print(base_content[1])
                    # print('BBBBB')
                    # print(group[0][1])
                    # content_results.append(d)
                # repo_list = list(map(lambda x: x[0], group))
                # print(f'{len(group)}')
            # print(content_results)


def q(x, y, file_path):
    title = ''
    if type(x) == tuple:
        x_title, x_values = get_column_title_and_values(*x)
    else:
        x_title, x_values = get_column_title_and_values(x)
    if type(y) == tuple:
        y_title, y_values = get_column_title_and_values(*y)
    else:
        y_title, y_values = get_column_title_and_values(y)
    new_x_values = []
    new_y_values = []
    for i in range(len(x_values)):
        x_value = x_values[i]
        y_value = y_values[i]
        if type(x_value) == int and type(y_value) == int:
            new_x_values.append(x_value)
            new_y_values.append(y_value)
    x_values = new_x_values
    y_values = new_y_values

    # x_values = list(map(lambda x: 0 if x == 0 else np.log10(x), x_values))
    # y_values = list(map(lambda x: 0 if x == 0 else np.log10(x), y_values))

    # print(f'{len(x_values)} {x_values}')
    # print(f'{len(y_values)} {y_values}')
    # print(f'Chart: {file_path} ({x_title} / {y_title})')
    # print(f'Pearson: {pearsonr(x_values, y_values)}')
    # print(f'Spearman: {spearmanr(x_values, y_values)}')
    # scatter_plot(x_values, y_values, title, x_title, y_title, file_path)
    return spearmanr(x_values, y_values)


def compute_data_normality(x):
    if type(x) == tuple:
        title, values = get_column_title_and_values(*x)
    else:
        title, values = get_column_title_and_values(x)
    values = list(filter(lambda x: type(x) == int, values))
    number_of_values = len(values)
    if number_of_values > 0:
        mean = statistics.mean(values)
        sd = statistics.stdev(values)
        mean_minus_1_sd = mean - sd
        mean_minus_2_sd = mean - sd - sd
        mean_minus_3_sd = mean - sd - sd - sd
        mean_plus_1_sd = mean + sd
        mean_plus_2_sd = mean + sd + sd
        mean_plus_3_sd = mean + sd + sd + sd
        count_68 = 0
        count_95 = 0
        count_99_7 = 0
        for value in values:
            if mean_minus_1_sd <= value <= mean_plus_1_sd:
                count_68 = count_68 + 1
            if mean_minus_2_sd <= value <= mean_plus_2_sd:
                count_95 = count_95 + 1
            if mean_minus_3_sd <= value <= mean_plus_3_sd:
                count_99_7 = count_99_7 + 1
        s = round(skew(values), 2)
        print(f'"{title}",{round(mean,2)},{round(sd,2)},{round(count_68 / number_of_values, 2)},{round(count_95 / number_of_values, 2)},{round(count_99_7 / number_of_values, 2)},{s}')
    else:
        print(f'"{title}",{0},{0},{0},{0},{0},{0}')


def compute_all_data_normality():
    compute_data_normality(36)  # Number of words
    compute_data_normality(37)  # Number of headers
    compute_data_normality(38)  # Number of paragraphs
    compute_data_normality((2, True, True))  # Number of categories
    compute_data_normality(3)  # Number of stars
    compute_data_normality(15)  # Number of committers
    compute_data_normality(22)  # Number of issues
    compute_data_normality(29)  # Number of security-related issues
    compute_data_normality((33, True, True))  # Number of CVEs
    compute_data_normality((34, True, True))  # Number of CWEs
    compute_data_normality(35)  # Number of forks
    compute_data_normality(39) # Lines of code


def dummy(column_index):
    directory_path = f'C:\\Files\\RQ2\\{column_index}\\'
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
    a = q(36, column_index, f'{directory_path}number_of_words.png')
    b = q(37, column_index, f'{directory_path}number_of_headers.png')
    c = q(38, column_index, f'{directory_path}number_of_paragraphs.png')
    d = q((2, True, True), column_index, f'{directory_path}number_of_categories.png')

    print(d)


    # print(f'"{round(a[0], 2)}, {round(a[1], 2)}","{round(b[0], 2)}, {round(b[1], 2)}","{round(c[0], 2)}, {round(c[1], 2)}","{round(d[0], 2)}, {round(d[1], 2)}"')
    # print(f'{d[1]}')


def get_first_security_policies():
    first_security_policies = []
    directory_path = 'C:\\Files\\security policies\\'
    for file_name in os.listdir(directory_path):
        file_path = f'{directory_path}{file_name}'
        repo = file_name.replace('.csv', '').replace('_', '/', 1)
        smallest_date_time = None
        smallest_date_time_row = None
        i = 0
        for row in csv_reader(file_path):
            if i > 0:
                date_time = datetime.datetime.strptime(row[3], '%Y-%m-%d %H:%M:%S%z')
                date_time = date_time.replace(tzinfo=None)
                if smallest_date_time is None or date_time < smallest_date_time:
                    smallest_date_time = date_time
                    smallest_date_time_row = row
            i = i + 1
        first_security_policies.append((repo, smallest_date_time, smallest_date_time_row))
    return first_security_policies



def get_number_of_days_since_document_created():
    # start_date_time = datetime.datetime(year=2019, month=5, day=23)
    # start = int(invented_date.strftime('%Y%m%d'))

    y_values = []
    today_date = pd.to_datetime('today').normalize()
    _, values = get_column_title_and_values(50)
    for value in values:
        if len(value) > 0:
            date_time = datetime.datetime.strptime(value, '%Y-%m-%dT%H:%M:%S%z')
            date_time = date_time.replace(tzinfo=None)
            y_values.append(f'{(today_date - date_time).days}')
        else:
            y_values.append(None)
    # first_security_policies = get_first_security_policies()
    # for security_policy in first_security_policies:
    #     print(security_policy)
    # for repo, created_date in security_policy_created_dates:
    #     before_fix.append((today_date - created_date).days)
    #     if created_date < invented_date:
    #         print(f'{repo} {created_date}')
    #         #print(f'BEFORE {(today_date - created_date).days}')
    #         # created_date = invented_date
    #         # print(f'AFTER {(today_date - created_date).days}')
    #     y_values.append((today_date - created_date).days)
    # for row in first_security_policies:
    #     if row[1] < invented_date:
    #         print(f'{row[2][1]} {row[2][0].lower() == row[0].lower()} {row[2][0].lower()}')
    return y_values


def get_owasp_descriptions(owasp_cwe_dict):
    y_values = []
    title, values = get_column_title_and_values(34, True)
    for value in values:
        description_set = None
        if value is not None:
            description_set = set()
            for cwe in value:
                if cwe in owasp_cwe_dict:
                    description_set.update(owasp_cwe_dict[cwe])
        y_values.append(description_set)
    return y_values


def get_number_of_owasp_descriptions(owasp_cwe_dict):
    return [f'{len(x)}' if x is not None else None for x in get_owasp_descriptions(owasp_cwe_dict)]


def get_aaa(owasp_cwe_dict):
    owasp_description_dict = dict()
    owasp_descriptions = get_owasp_descriptions(owasp_cwe_dict)
    for key in get_owasp_description_dict():
        value = []
        for descriptions in owasp_descriptions:
            v = None
            if descriptions is not None:
                if key in descriptions:
                    v = 'Yes'
                else:
                    v = 'No'
            value.append(v)
        owasp_description_dict[key] = value
    return owasp_description_dict




def get_indexes():
    package_manager_dict = get_package_manager_dict()
    owasp_cwe_dict = get_owasp_cwe_dict()
    indexes = []
    indexes.extend([
        ('Number of stars', 3),
        ('Number of committers', 15),
        ('Number of issues', 22),
        ('Number of security-related issues', 29),
        ('Number of security advisories', 77),
        ('Number of CVEs', (33, True, True)),
        ('Number of CWEs', (34, True, True)),
        ('Number of OWASP descriptions', [get_number_of_owasp_descriptions, owasp_cwe_dict]),
        ('Number of CVSS v2 impact score low', 52),
        ('Number of CVSS v2 impact score medium or above', 55),
        ('Number of CVSS v3 impact score low', 61),
        ('Number of CVSS v3 impact score medium or above', 65),
        ('Number of forks', 35),
        ('Number of languages', 45),
        ('Number of days since document created', [get_number_of_days_since_document_created]),
        ('Number of lines of code', 40),
        ('Number of dependencies', [repo_2, get_repo_xx, package_manager_dict])
    ])
    for package_manager in package_manager_dict:
        indexes.append((f'Number of {package_manager} dependencies', [repo_2, get_package_manager_count, package_manager_dict[package_manager]]))
    return indexes


def get_indexes_2():
    cwe_list = get_column_title_and_values(34, True)[1]
    top_cwes = get_top_25_cwes()
    a_dict = get_aaa(get_owasp_cwe_dict())

    indexes = []
    for top_cwe in top_cwes:
        values = []
        for cwes in cwe_list:
            value = None
            if cwes is not None:
                value = 'Yes' if top_cwe in cwes else 'No'
            values.append(value)
        indexes.append((top_cwe, values))

    language_dict = one_hot_encoding(get_column_title_and_values(46)[1], percentage=0.8)
    for language in language_dict:
        key = f'{language.upper()} language'
        indexes.append((key, language_dict[language]))

    indexes.extend([
        ('Object-oriented language', get_language_values(9)),
        ('Web development language', get_language_values(20)),
        ('Mobile development language', get_language_values(26)),
        ('Backend development language', get_language_values(32))
    ])

    application_domain_dict = one_hot_encoding(get_column_title_and_values(30)[1])
    for application_domain in application_domain_dict:
        indexes.append((application_domain, application_domain_dict[application_domain]))

    indexes.append(('README.md', get_column_title_and_values(48)[1]))

    package_manager_dict = get_package_manager_dict()
    for package_manager in package_manager_dict:
        key = f'{package_manager} dependency'
        indexes.append((key, repo_2(is_package_manager_used, package_manager_dict[package_manager])))

    for a in a_dict:
        indexes.append((a, a_dict[a]))
    return indexes


def get_index_title_and_values(title, index):
    if type(index) == int:
        title, values = get_column_title_and_values(index)
    elif type(index) == tuple:
        title, values = get_column_title_and_values(*index)
    else:
        title, values = title, index[0](*(index[1:] if len(index) > 1 else []))
    return title, values


def get_x_and_y(x_values, name, index):
    y_title, y_values = get_index_title_and_values(name, index)
    remove_invalid_values(x_values, y_values)
    x_values = list(map(lambda x: int(x), x_values))
    y_values = list(map(lambda x: int(x), y_values))
    return x_values, y_title, y_values


def get_grouped_x_and_y(x_values, name, index, location_dict):
    if type(index) == tuple and len(index) == 3:
        temp_index = (index[0], index[1], False)
    else:
        temp_index = index
    y_title, y_values = get_index_title_and_values(name, temp_index)
    _, z_values = get_column_title_and_values(0)
    remove_invalid_values(x_values, y_values, z_values)
    x_values, y_values = group_and_filter_values(x_values, y_values, z_values, location_dict, index)
    return x_values, y_title, y_values


def insert_in_descending_order(row, column_index, rows):
    if len(rows) == 0:
        rows.append(row)
    else:
        inserted = False
        for i in range(len(rows)):
            if row[column_index] > rows[i][column_index]:
                rows.insert(i, row)
                inserted = True
                break
        if not inserted:
            rows.append(row)


def compute_spearman_level_1():
    table_1_rows = []
    table_2_rows = []
    table_3_rows = []
    headers = ['Number of characters', 'Number of words', 'Number of paragraphs']
    x_indexes = [36, 37, 39]
    y_indexes = get_indexes()
    number_of_tests = (len(x_indexes) * len(y_indexes))
    corrected_alpha = ALPHA / number_of_tests
    ordered_rows = []
    for y_custom_title, y_index in y_indexes:
        p_values = []
        p_value_rejections = []
        rhos = []
        for x_index in x_indexes:
            x_title, x_values = get_column_title_and_values(x_index)
            x_values, y_title, y_values = get_x_and_y(x_values, y_custom_title, y_index)
            rho, p_value = spearmanr(x_values, y_values)
            sign = compute_spearman_sign(rho)
            p_values.append(f'{p_value}')
            if p_value < corrected_alpha:
                p_value_rejection = 'Y'
                row = [y_custom_title, x_title, sign, len(y_values), p_value, rho]
                insert_in_descending_order(row, 5, ordered_rows)
            else:
                p_value_rejection = 'N'
            p_value_rejections.append(f'"{p_value_rejection},{sign}"')
            rhos.append(f'{rho}')
            print(f'x_values: {len(x_values)} {x_values}')
            print(f'y_values: {len(y_values)} {y_values}')
        table_1_row = ','.join(p_values)
        table_2_row = ','.join(p_value_rejections)
        table_3_row = ','.join(rhos)
        table_1_rows.append(f',"{y_custom_title}",{table_1_row}')
        table_2_rows.append(f',"{y_custom_title}",{table_2_row}')
        table_3_rows.append(f',"{y_custom_title}",{table_3_row}')
    print_tables(table_1_rows, table_2_rows, table_3_rows, headers)
    title_row = ['Repository Characteristic', 'Security Policy Category', 'Sign', 'Size', 'p-value', 'rho']
    print_ordered_rows(ordered_rows, number_of_tests, title_row)


def get_category_counts(category_set_list, category_name):
    counts = []
    for category_set in category_set_list:
        if category_name in category_set:
            counts.append(f'{category_set[category_name]}')
        else:
            counts.append('0')
    return counts


def compute_spearman_level_2():
    table_1_rows = []
    table_2_rows = []
    table_3_rows = []
    table_4_rows = []
    indexes = get_indexes()
    number_of_tests = len(indexes) * len(category_names)
    corrected_alpha = ALPHA / number_of_tests
    _, category_set_list = get_column_title_and_values(2, True)
    for y_custom_title, y_index in indexes:
        p_values = []
        p_value_rejections = []
        rhos = []
        for category_name in category_names:
            x_values, y_title, y_values = get_x_and_y(get_category_counts(category_set_list, category_name), y_custom_title, y_index)
            rho, p_value = spearmanr(x_values, y_values)
            sign = compute_spearman_sign(rho)
            p_values.append(f'{p_value}')
            if p_value < corrected_alpha:
                p_value_rejection = 'Y'
                row = [y_custom_title, category_name, sign, len(y_values), p_value, rho]
                insert_in_descending_order(row, 5, table_4_rows)
            else:
                p_value_rejection = 'N'
            p_value_rejections.append(f'"{p_value_rejection},{sign}"')
            rhos.append(f'{rho}')
            print(f'"{category_name}","{y_title}","{y_custom_title}",{p_value},{p_value_rejection}')
            print(f'x_values: {len(x_values)} {x_values}')
            print(f'y_values: {len(y_values)} {y_values}')
        table_1_row = ','.join(p_values)
        table_2_row = ','.join(p_value_rejections)
        table_3_row = ','.join(rhos)
        table_1_rows.append(f',"{y_custom_title}",{table_1_row}')
        table_2_rows.append(f',"{y_custom_title}",{table_2_row}')
        table_3_rows.append(f',"{y_custom_title}",{table_3_row}')
    print_tables(table_1_rows, table_2_rows, table_3_rows)
    title_row = ['Repository Characteristic', 'Security Policy Category', 'Sign', 'Size', 'p-value', 'rho']
    print_ordered_rows(table_4_rows, number_of_tests, title_row)


def group_and_filter_values(x_values, y_values, z_values, location_dict, index):
    as_list = index[1] if type(index) == tuple and len(index) >= 2 else False
    as_list_count = index[2] if type(index) == tuple and len(index) >= 3 else False
    z_values = list(map(lambda x: location_dict[x], z_values))
    my_dict = dict()
    for x, y, z in zip(x_values, y_values, z_values):
        if z in my_dict:
            grouped_x_values, grouped_y_values = my_dict[z]
            grouped_x_values.append(int(x))
            if as_list:
                grouped_y_values.update(y)
            else:
                grouped_y_values.append(int(y))
        else:
            if as_list:
                my_dict[z] = ([int(x)], set(y))
            else:
                my_dict[z] = ([int(x)], [int(y)])
    new_x_values = []
    new_y_values = []
    for a in my_dict:
        # new_x_values.append(my_dict[a][0][0])
        new_x_values.append(sum(my_dict[a][0]))
        if as_list_count:
            new_y_values.append(len(my_dict[a][1]))
        else:
            new_y_values.append(sum(my_dict[a][1]))
    return new_x_values, new_y_values


def set_location_dict(repo, location_dict):
    location_dict[repo] = get_security_policy_repo(repo)


def get_df(x_title, x_values, y_title, y_values):
    value_dict = dict()
    value_dict[('Yes', 'Yes')] = 0
    value_dict[('Yes', 'No')] = 0
    value_dict[('No', 'Yes')] = 0
    value_dict[('No', 'No')] = 0
    if len(x_values) == len(y_values):
        for i in range(len(x_values)):
            key = x_values[i], y_values[i]
            value_dict[key] = value_dict[key] + 1
    return pd.DataFrame({
        f'{x_title} yes': [value_dict[('Yes', 'Yes')], value_dict[('Yes', 'No')]],
        f'{x_title} no': [value_dict[('No', 'Yes')], value_dict[('No', 'No')]]
    }, index=pd.Index([f'{y_title} yes', f'{y_title} no']))


def compute_odds_ratio_and_sign(df, x_title, y_title):
    a = df[f'{x_title} yes'][f'{y_title} yes']
    b = df[f'{x_title} no'][f'{y_title} yes']
    c = df[f'{x_title} yes'][f'{y_title} no']
    d = df[f'{x_title} no'][f'{y_title} no']
    odds_ratio = (a * d) / (b * c)
    if odds_ratio > 1:
        sign = '+'
    elif odds_ratio < 1:
        sign = '-'
    else:
        sign = '='
    return odds_ratio, sign


def compute_mann_whitney():
    table_1_rows = []
    table_2_rows = []
    table_3_rows = []
    table_4_rows = []
    indexes = get_indexes()
    number_of_tests = len(indexes) * len(category_names)
    corrected_alpha = ALPHA / number_of_tests
    for name, index in indexes:
        p_values = []
        p_value_rejections = []
        effect_sizes = []
        for category_name in category_names:
            _, x_values = get_column_title_and_values(2, True)
            x_values = list(map(lambda x: list(x.keys()), x_values))
            y_title, y_values = get_index_title_and_values(name, index)
            remove_invalid_values(x_values, y_values)
            y_values = list(map(lambda x: int(x), y_values))
            y_group = []
            n_group = []
            for i in range(len(x_values)):
                if category_name in x_values[i]:
                    y_group.append(y_values[i])
                else:
                    n_group.append(y_values[i])
            p_value = stats.mannwhitneyu(y_group, n_group).pvalue
            sign = compute_group_sign(ALPHA, y_group, n_group)
            effect_size = compute_mann_whitney_effect_size(y_group, n_group)
            p_values.append(f'{p_value}')
            if p_value < corrected_alpha:
                p_value_rejection = 'Y'
                row = [name, category_name, sign, len(y_values), p_value, effect_size]
                insert_in_descending_order(row, 5, table_4_rows)
            else:
                p_value_rejection = 'N'
            p_value_rejections.append(f'"{p_value_rejection},{sign}"')
            effect_sizes.append(f'{effect_size}')
            print(f'"{category_name}","{y_title}",{p_value},{p_value_rejection}')
            print(f'YES: {len(y_group)} {y_group}')
            print(f'NO: {len(n_group)} {n_group}')
        table_1_row = ','.join(p_values)
        table_2_row = ','.join(p_value_rejections)
        table_3_row = ','.join(effect_sizes)
        table_1_rows.append(f',"{name}",{table_1_row}')
        table_2_rows.append(f',"{name}",{table_2_row}')
        table_3_rows.append(f',"{name}",{table_3_row}')
    print_tables(table_1_rows, table_2_rows, table_3_rows)
    title_row = ['Repository characteristic', 'Security policy category', 'Sign', 'Size', 'p-value', 'Effect size']
    print_ordered_rows(table_4_rows, number_of_tests, title_row)


def compute_chi_squared():
    table_1_rows = []
    table_2_rows = []
    table_3_rows = []
    table_4_rows = []
    indexes = get_indexes_2()
    number_of_tests = len(indexes) * len(category_names)
    corrected_alpha = ALPHA / number_of_tests
    ccc = 0

    for name, values in indexes:
        p_values = []
        p_value_rejections = []
        effect_sizes = []
        for x_title in category_names:
            _, x_values = get_column_title_and_values(2, True)
            x_values = list(map(lambda x: 'Yes' if x_title in x else 'No', list(map(lambda x: list(x.keys()), x_values))))
            y_title = name
            y_values = [] + values
            remove_invalid_values(x_values, y_values)
            table = pd.crosstab(x_values, y_values)

            chi2_value, p_value, degrees_of_freedom, expected_frequencies = chi2_contingency(table, correction=True)
    #         # print(f'{category_name}')
    #         # if category_name == 'Reporting procedure':
    #         # print(expected_frequencies)
    #         # print(compute_chi_square_value(table, expected_frequencies, True))
            if table.shape == (2,2):
                a = table['Yes']['Yes']
                b = table['Yes']['No']
                c = table['No']['Yes']
                d = table['No']['No']
                odds_ratio = (a * d) / (b * c)
                if odds_ratio > 1:
                    sign = '+'
                elif odds_ratio < 1:
                    sign = '-'
                else:
                    sign = '='
            else:
                sign = ''
            critical_value = chi2.ppf(1 - ALPHA, degrees_of_freedom)
    #         # print(chi2_value)
            cramer_v = math.sqrt(chi2_value / (table.sum().sum() * (min(table.shape) - 1)))
            # expected_count_percentage = get_expected_count_greater_than_or_equals_five_percentage(expected_frequencies)
            # chi2_rejection = 'Y' if chi2_value >= critical_value else 'N'
            # print(f',{category_name},{name},{chi2_value},{cramer_v},{p_value},{chi2_rejection},{p_value_rejection},{degrees_of_freedom},{expected_count_percentage}')
    #         print(table.to_string())
    #         if expected_count_percentage < 0.8:
    #             ccc = ccc + 1
            p_values.append(f'{p_value}')
            if p_value < corrected_alpha:
                p_value_rejection = 'Y'
                row = [y_title, x_title, sign, len(y_values), p_value, cramer_v]
                insert_in_descending_order(row, 5, table_4_rows)
            else:
                p_value_rejection = 'N'
            p_value_rejections.append(f'"{p_value_rejection},{sign}"')
            effect_sizes.append(f'{cramer_v}')
            print(f'{x_title} {y_title}')
            # print(table)
            print(f'{len(x_values)} {x_values}')
            print(f'{len(y_values)} {y_values}')
        table_1_row = ','.join(p_values)
        table_2_row = ','.join(p_value_rejections)
        table_3_row = ','.join(effect_sizes)
        table_1_rows.append(f',"{name}",{table_1_row}')
        table_2_rows.append(f',"{name}",{table_2_row}')
        table_3_rows.append(f',"{name}",{table_3_row}')
    print_tables(table_1_rows, table_2_rows, table_3_rows)
    title_row = ['Repository characteristic', 'Security policy category', 'Sign', 'Size', 'p-value', 'Cramer\'s V']
    print_ordered_rows(table_4_rows, number_of_tests, title_row)
    # print(ccc)


def compute_fisher_exact():
    table_1_rows = []
    table_2_rows = []
    table_3_rows = []
    table_4_rows = []
    indexes = get_indexes_2()
    number_of_tests = len(indexes) * len(category_names)
    corrected_alpha = ALPHA / number_of_tests
    for name, values in indexes:
        p_values = []
        p_value_rejections = []
        effect_sizes = []
        for x_title in category_names:
            _, x_values = get_column_title_and_values(2, True)
            x_values = list(map(lambda x: 'Yes' if x_title in x else 'No', list(map(lambda x: list(x.keys()), x_values))))
            y_title = name
            y_values = [] + values
            remove_invalid_values(x_values, y_values)
            df = get_df(x_title, x_values, y_title, y_values)
            odds_ratio, sign = compute_odds_ratio_and_sign(df, x_title, y_title)
            p_value = fisher_exact(df.to_numpy()).pvalue
            p_values.append(f'{p_value}')
            if p_value < corrected_alpha:
                p_value_rejection = 'Y'
                row = [y_title, x_title, sign, len(y_values), p_value, odds_ratio]
                insert_in_descending_order(row, 5, table_4_rows)
            else:
                p_value_rejection = 'N'
            p_value_rejections.append(f'"{p_value_rejection},{sign}"')
            effect_sizes.append(f'{odds_ratio}')
            # print(f'{x_title} {y_title}')
            # print(f'{len(x_values)} {x_values}')
            # print(f'{len(y_values)} {y_values}')
            print(df)
        table_1_row = ','.join(p_values)
        table_2_row = ','.join(p_value_rejections)
        table_3_row = ','.join(effect_sizes)
        table_1_rows.append(f',"{name}",{table_1_row}')
        table_2_rows.append(f',"{name}",{table_2_row}')
        table_3_rows.append(f',"{name}",{table_3_row}')
    print_tables(table_1_rows, table_2_rows, table_3_rows)
    title_row = ['Repository characteristic', 'Security policy category', 'Sign', 'Size', 'p-value', 'Odds ratio']
    print_ordered_rows(table_4_rows, number_of_tests, title_row)


def print_tables(table_1_rows, table_2_rows, table_3_rows, headers=category_names):
    header_line = ','.join(map(lambda x: f'"{x}"', headers))
    header_line = f',,{header_line}'
    print()
    print(header_line)
    for line in table_1_rows:
        print(line)
    print()
    print(header_line)
    for line in table_2_rows:
        print(line)
    print()
    print(header_line)
    for line in table_3_rows:
        print(line)


def abcde(value):
    ccc = []
    decimal_index = -1
    non_zero_started = False
    non_zero_count = 0
    count = 0
    aaa = '{:f}'.format(value)
    for i in range(len(aaa)):
        c = aaa[i]
        if decimal_index > -1:
            ccc.append(c)
        if c == '.':
            decimal_index = i
        elif decimal_index > -1 and c != '0':
            non_zero_started = True
        if non_zero_started:
            count = count + 1
            if c != '0':
                non_zero_count = non_zero_count + 1
                if count >= 3:
                    break
    if non_zero_count < 2:
        if 'e-' in f'{value}':
            slices = f'{value}'.split('e-')
            ccc = f'{slices[0][:5]}e-{slices[1]}'
        else:
            ccc = f'{value}'
    else:
        count = 0
        for c in reversed(ccc):
            if c == '0':
                count = count + 1
            else:
                break
        if count > 0:
            ccc = ccc[:-count]
        ccc = f''.join(ccc)
        before_decimal = aaa[:decimal_index]
        if before_decimal == '0':
            ccc = f'.{ccc}'
        else:
            ccc = f'{before_decimal}.{ccc}'
    return ccc


def print_ordered_rows(ordered_rows, number_of_tests, title_row=None):
    print()
    print(f'{len(ordered_rows)} {number_of_tests}')
    print()
    if title_row is not None:
        title_row = list(map(lambda x: f'"{x}"', title_row))
        title_row = ','.join(title_row)
        print(f',"#",{title_row}')
    count = 0
    for i in range(len(ordered_rows)):
        category = ordered_rows[i][1].lower()
        if category != '':
            values = ','.join([
                f'"{ordered_rows[i][0]}"',
                f'"{ordered_rows[i][1]}"',
                f'"{ordered_rows[i][2]}"',
                f'"{ordered_rows[i][3]}"',
                f'"{abcde(ordered_rows[i][4])}"',
                f'"{abcde(ordered_rows[i][5])}"'
            ])
            count = count + 1
            print(f',"{count}",{values}')
            # if count == 10:
            #     break


def filter_invalid_repos(repo, value):
    invalid_repos = ['iofinnet/tss-lib', 'iofinnet,root,0']
    return None if repo in invalid_repos else value


def get_dict_value(repo, repo_dict, key):
    value = f'0'
    category_dict = repo_dict[repo]
    if key in category_dict:
        value = f'{category_dict[key]}'
    return filter_invalid_repos(repo, value)


def get_name_vector(names):
    number_of_categories = len(category_names)
    vector = [0] * number_of_categories
    for name in names:
        for i in range(number_of_categories):
            if name == category_names[i]:
                vector[i] = 1
    return vector


def compute_point_biserial_correlation(x_title, x_values, y, writer):
    if type(y) == tuple:
        y_title, y_values = get_column_title_and_values(*y)
    else:
        y_title, y_values = get_column_title_and_values(y)
    new_x_values = []
    new_y_values = []
    for i in range(len(x_values)):
        x_value = x_values[i]
        y_value = y_values[i]
        if type(x_value) == int and type(y_value) == int:
            new_x_values.append(x_value)
            new_y_values.append(y_value)
    x_values = new_x_values
    y_values = new_y_values
    aaa = pointbiserialr(x_values, y_values)
    # if aaa[0] >= 0.1:
    row = f'"{x_title}","{y_title}",{len(list(filter(lambda x: x, x_values)))},{aaa[0]},{aaa[1]}'
    print(row)
    # writer.write(f'{row}\n')
        # scatter_plot(x_values, y_values, '', x_title, y_title, f'C:\\Files\\RQ2\\aaa\\{aaa[0]}.png')




def dummy_dummy():
    number_of_categories = len(category_names)
    title, values = get_column_title_and_values(2, True)
    values = list(map(lambda x: get_name_vector(x), values))
    writer = get_writer('C:\\Files\\RQ2\\results.csv')
    for i in range(1, number_of_categories + 1):
        for names in itertools.combinations(category_names, i):
            names = list(names)
            vector = get_name_vector(names)
            x_values = list(map(lambda x: 1 if x == vector else 0, values))
            compute_point_biserial_correlation(f'{names}', x_values, 3, writer)
            compute_point_biserial_correlation(f'{names}', x_values, 15, writer)
            compute_point_biserial_correlation(f'{names}', x_values, 22, writer)
            compute_point_biserial_correlation(f'{names}', x_values, 29, writer)
            compute_point_biserial_correlation(f'{names}', x_values, (33, True, True), writer)
            compute_point_biserial_correlation(f'{names}', x_values, (34, True, True), writer)
            compute_point_biserial_correlation(f'{names}', x_values, 35, writer)
            compute_point_biserial_correlation(f'{names}', x_values, 39, writer)


def dummy_dummy_2(category_name, y):
    x_title, x_values = get_column_title_and_values(2, True)
    if type(y) == tuple:
        y_title, y_values = get_column_title_and_values(*y)
    else:
        y_title, y_values = get_column_title_and_values(y)
    if y == 39:
        new_x_values = []
        new_y_values = []
        for i in range(len(x_values)):
            x_value = x_values[i]
            y_value = y_values[i]
            if len(f"{y_value}") > 0 and type(y_value) == int:
                new_x_values.append(x_value)
                new_y_values.append(y_value)
        x_values = new_x_values
        y_values = new_y_values



    x_values = list(map(lambda x: 1 if category_name in x else 0, x_values))
    y_values = list(map(lambda x: 1 if x > 0 else 0, y_values))
    a = pd.crosstab(x_values, y_values)
    # print(a)
    # a = [[6, 13, 16, 8], [7, 16, 15, 11]]
    # a = [[30,14,34,45,57,20]]
    chi2_value, p_value, degrees_of_freedom, expected = chi2_contingency(a)
    # print(f'Chi-Square Test Statistic: {chi2_value}')
    # print(f'p_value: {p_value}')
    # print("Degrees of Freedom:", degrees_of_freedom)
    # print("Expected Frequencies:")
    # print(pd.DataFrame(expected))
    threshold = 0.05
    critical_value = chi2.ppf(1 - threshold, degrees_of_freedom)
    # print(f'Critical value: {critical_value}')
    # print(f'{chi2_value} < {critical_value} {chi2_value < critical_value}')
    # print(f'{p_value}')

    return 'Y' if chi2_value >= critical_value and p_value < threshold else 'N'

    # if chi2_value < critical_value:
    #     # print(f'"{category_name}","{y_title}","N"')
    #     print(f'N {"Y" if p_value < threshold else "N"}')
    #     # print('Null hypothesis is not rejected')
    # else:
    #     # print(f'"{category_name}","{y_title}","Y"')
    #     print(f'Y {"Y" if p_value < threshold else "N"}')
    #     # print('Null hypothesis is rejected')


def transpose(rows):
    w = 0
    h = len(rows)
    for row in rows:
        w = len(row)
        break
    new_rows = []
    for i in range(w):
        row = []
        for j in range(h):
            row.append(rows[j][i])
        new_rows.append(row)
    return new_rows


test_datasets = [
    3, # Number of stars
    15, # Number of committers
    22, # Number of issues
    29, # Number of security-related issues
    (33, True, True), # Number of CVEs
    (34, True, True), # Number of CWEs
    35, # Number of forks
    39, # Lines of code
]


def compute_chi2(x_value, y_index, y_as_list, y_value, threshold=0.05):
    x_title, x_values = get_column_title_and_values(2, True)
    y_title, y_values = get_column_title_and_values(y_index, y_as_list)
    x_values = list(map(lambda x: 1 if x is not None and x_value in x else 0, x_values))
    if y_as_list:
        y_values = list(map(lambda x: 1 if x is not None and y_value in x else 0, y_values))
    x_length = len([x for x in x_values if x == 1])
    y_length = len([x for x in y_values if x == 1])
    a = pd.crosstab(x_values, y_values)
    print(f'{x_value} {y_value}')
    print(a.to_string())
    # if x_length == 0 and y_length == 0:
    #     print(f'{x_value} {y_value}')
    #     print(a)
    chi2_value, p_value, degrees_of_freedom, expected_frequencies = chi2_contingency(a)

    # print(chi2_value)
    # print(p_value)
    # print(degrees_of_freedom)
    # print(expected_frequencies)
    critical_value = chi2.ppf(1 - threshold, degrees_of_freedom)
    # print(f'{x_value} {y_value} {chi2_value} {p_value} {degrees_of_freedom} {critical_value} {chi2.ppf(7.1, 30)}')
    # return 'Y' if chi2_value >= critical_value and p_value < threshold else 'N'
    # return 'Y' if chi2_value >= critical_value else 'N'
    return f'{chi2_value}'


def get_value_dict(column_index, as_list=False):
    value_dict = dict()
    total = 0
    title, values = get_column_title_and_values(column_index, as_list)
    for value in values:
        if value is not None and value != 'None':
            if as_list:
                for v in value:
                    if v in value_dict:
                        value_dict[v] = value_dict[v] + 1
                    else:
                        value_dict[v] = 1
                    total = total + 1
            else:
                if value in value_dict:
                    value_dict[value] = value_dict[value] + 1
                else:
                    value_dict[value] = 1
                total = total + 1
    return sort_by_descending_values(value_dict), total


def print_results(titles, rows):
    rows = transpose(rows)
    title = ','.join(category_names)
    print(f',{title}')
    for i in range(len(rows)):
        values = ','.join(rows[i])
        print(f'{titles[i]},{values}')


def get_results(y_column_index, y_as_list, y_values):
    rows = []
    for category_name in category_names:
        row = []
        for y_value in y_values:
            row.append(compute_chi2(category_name, y_column_index, y_as_list, y_value))
        rows.append(row)
    return rows


def get_expected_count_greater_than_or_equals_five_percentage(expected_counts):
    total = 0
    count = 0
    for i in range(len(expected_counts)):
        for j in range(len(expected_counts[i])):
            total = total + 1
            if expected_counts[i][j] >= 5:
                count = count + 1
    return count / total


def get_invalid_index(x_values, y_values):
    x_invalid_indexes = {i for i in range(len(x_values)) if x_values[i] is None or (type(x_values[i]) != list and len(x_values[i]) == 0)}
    y_invalid_indexes = {i for i in range(len(y_values)) if y_values[i] is None or (type(y_values[i]) != list and len(y_values[i]) == 0)}
    invalid_indexes = list(x_invalid_indexes.union(y_invalid_indexes))
    if len(invalid_indexes) > 0:
        return invalid_indexes[0]
    else:
        return None


def remove_invalid_values(x_values, y_values, z_values=None):
    invalid_index = get_invalid_index(x_values, y_values)
    while invalid_index is not None:
        print(f'invalid index {invalid_index}')
        del x_values[invalid_index]
        del y_values[invalid_index]
        if z_values is not None:
            del z_values[invalid_index]
        invalid_index = get_invalid_index(x_values, y_values)


def get_top_25_cwes():
    top_25_cwes = set()
    for column_index in range(1,5):
        i = 0
        for row in csv_reader('/Users/wanlok/Desktop/CWE Rankings.csv'):
            if i > 0:
                top_25_cwes.add(row[column_index])
            i = i + 1
    return top_25_cwes


def get_columns(item_list):
    item_set = set()
    for items in item_list:
        if items is not None:
            item_set.update(items)
    return item_set


def one_hot_encoding(item_list, as_list=False, percentage=1):
    column_dict = dict()
    if as_list:
        for i in range(len(item_list)):
            if len(item_list[i]) > 0:
                item_list[i] = eval(item_list[i])
        values = list(itertools.chain.from_iterable(item_list))
    else:
        values = item_list
    columns = list(filter(lambda x: x is not None and len(x) > 0, get_values(values, percentage=percentage)))
    for column in columns:
        values = []
        for items in item_list:
            if len(items) > 0:
                if column in items:
                    values.append('Yes')
                else:
                    values.append('No')
            else:
                values.append(None)
        column_dict[column] = values
    return column_dict


def get_language_values(column_index):
    values = []
    value_dict = dict()
    i = 0
    file_path = '/Users/wanlok/Desktop/language_paradigm.csv'
    for row in csv_reader(file_path):
        if i > 0:
            language = row[0].lower()
            value = True if row[column_index] == 'Y' else False
            value_dict[language] = value
        i = i + 1
    _, languages = get_column_title_and_values(46, False)
    for language in languages:
        language = language.lower()
        if language in value_dict:
            if value_dict[language]:
                values.append('Yes')
            else:
                values.append('No')
        else:
            values.append(None)
    return values


def ans_1_2():
    titles = ['Stars', 'Committers', 'Issues', 'Security-related issues', 'CVEs', 'CWEs', 'Forks', 'Lines of code']
    rows = []
    for category_name in category_names:
        row = []
        for dataset in test_datasets:
            row.append(dummy_dummy_2(category_name, dataset))
        rows.append(row)
    print_results(titles, rows)


def ans_1_3():
    column_index = 43
    as_list = False
    value_dict, _ = get_value_dict(column_index, as_list)
    values = [x for x in value_dict]
    print_results(values, get_results(column_index, as_list, values))


def get_values(v, percentage=0.8, with_count=False):
    values = []
    total = 0
    count = 0
    distribution_dict = dict()
    for value in v:
        total = total + 1
        if value in distribution_dict:
            distribution_dict[value] = distribution_dict[value] + 1
        else:
            distribution_dict[value] = 1
    for value in sort_by_descending_values(distribution_dict):
        count = count + distribution_dict[value]
        # print(f'{value} {count / total}')
        if with_count:
            values.append((value, distribution_dict[value]))
        else:
            values.append(value)
        if count / total >= percentage:
            break
    return values


def validation():
    # _, w_values = get_column_title_and_values(0)
    # _, x_values = get_column_title_and_values(31)
    # _, y_values = get_column_title_and_values(46)
    # for w, x, y in zip(w_values, x_values, y_values):
    #     if len(x) > 0 and len(y) > 0:
    #         x_set = set(eval(x))
    #         y_set = set(eval(y).keys())
    #         if x_set != y_set:
    #             print(f'{w} {x_set} {y_set}')

    # primary_languages = get_column_title_and_values(45, False)[1]
    # top_languages = get_values(primary_languages)
    #
    # for language in top_languages:
    #     l = list(map(lambda x: 'Yes' if x == language else 'No', primary_languages))
    #     print(f'{language} {l}')

    # print(top_languages)
    #
    # a = []
    # for v in get_column_title_and_values(46)[1]:
    #     if len(v) > 0:
    #         v = set(eval(v).keys())
    #         if len(v.intersection(top_languages)) > 0:
    #             a.append(f'{v.intersection(top_languages)}')
    #
    # sum = 0
    # for x in get_values(a, with_count=True):
    #     sum = sum + x[1]
    #     print(x)
    # print(sum)

    # indexs = []
    # my_dict = get_owasp_dict()
    # for a in my_dict:
    #     print(f'{a} {xmy_dict[a]}')


    print('Hello World')


def is_package_manager_used(repo, b):
    value = 'No'
    for bb in b:
        if bb[0] == repo:
            value = 'Yes'
            break
    return filter_invalid_repos(repo, value)


def get_package_manager_count(repo, b):
    value = f'0'
    for bb in b:
        if bb[0] == repo:
            value = f'{len(bb[1])}'
            break
    return filter_invalid_repos(repo, value)


def extract_top():
    l = [
        ('Spearman', '/Users/wanlok/Desktop/20230914/Completed/Spearman.csv'),
        ('Spearman', '/Users/wanlok/Desktop/20230914/Completed/Spearman Grouped.csv'),
        ('Mann', '/Users/wanlok/Desktop/20230914/Completed/Mann.csv'),
        ('Mann', '/Users/wanlok/Desktop/20230914/Completed/Mann Grouped.csv'),
        ('Chi', '/Users/wanlok/Desktop/20230914/Completed/Chi.csv'),
        ('Chi', '/Users/wanlok/Desktop/20230914/Completed/Chi Grouped.csv'),
        ('Fisher', '/Users/wanlok/Desktop/20230914/Completed/Fisher.csv'),
        ('Fisher', '/Users/wanlok/Desktop/20230914/Completed/Fisher Grouped.csv')
    ]
    for category_name in category_names:
        for test_name, csv_file_path in l:
            for row in csv_reader(csv_file_path):
                if len(row) >= 4 and row[3] == category_name and row[3].lower() != 'empty':
                    line = ','.join(row[4:])
                    print(f'{test_name},{row[2]},{row[3]},{line}')
        # print()


if __name__ == '__main__':
    # programming_languages = list(package_manager_languages) + ['ASP.NET', 'Classic ASP', 'F#', 'Visual Basic .NET', 'Visual Basic 6.0']

    # a(3, 2, nr([5000, 10000, 50000, 100000])) # Number of stars / Categories
    # c(29, 2, nr([1000, 2000, 3000, 4000, 5000, 6000, 7000, 8000, 9000])) # Number of forks / Categories
    # c(30, 2, nr([200, 400, 600, 800, 1000, 1200, 1400, 1600, 1800, 2000])) # Number of words / Categories
    # c(31, 2, nr([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10])) # Number of headers / Categories
    # c(32, 2, nr([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10])) # Number of paragraphs / Categories
    # c(13, 2, nr([10, 20, 30, 40, 50, 60, 70, 80, 90, 100])) # Number of committers 2022 / Categories
    # c(13, 2, nr([5, 10, 20, 30, 40, 90]))  # Number of committers 2022 / Categories

    # a(3, (2, True), nr([5000, 10000, 50000, 100000])) # Number of stars / Categories

    # q((2, True, True), 3, '1') # Categories / Star
    # q((2, True, True), 29, '2') # Categories / Forks
    # q(30, 3, '3') # Words / Star
    # q(31, 3, '4') #
    # q((2, True, True), 32, '5')
    # q((2, True, True), 9, '6')
    # q((2, True, True), 10, '7')
    # q((2, True, True), 11, '8')
    # q((2, True, True), 12, '9')
    # q((2, True, True), 13, '10')
    # q((2, True, True), 18, '11')
    # q((2, True, True), )

    # compute_all_data_normality()
    # compute_spearman_level_1()
    # compute_spearman_level_2()
    # compute_mann_whitney()
    # compute_chi_squared()
    # compute_fisher_exact()

    # validation()

    extract_top()

    # list = []
    # row_1 = [3, 1, 4, 6]
    # row_2 = [2, 8, 2, 2]
    # row_3 = [1, 2, 6, 7]
    # row_4 = [7, 4, 3, 8]
    # row_5 = [6, 8, 9, 8]
    # column_index = 0
    # insert_in_descending_order(row_1, column_index, list)
    # insert_in_descending_order(row_2, column_index, list)
    # insert_in_descending_order(row_3, column_index, list)
    # insert_in_descending_order(row_4, column_index, list)
    # insert_in_descending_order(row_5, column_index, list)
    # for item in list:
    #     print(item)




    # dummy_dummy()
    # dummy()

    # ans_1_2()
    # ans_1_3()

    # a(29, (2, True), nr([1000, 2000, 3000, 4000, 5000, 6000, 7000, 8000, 9000])) # Number of forks / Categories
    # a(30, (2, True), nr([200, 400, 600, 800, 1000, 1200, 1400, 1600, 1800, 2000])) # Number of words / Categories
    # a(31, (2, True), nr([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10])) # Number of headers / Categories
    # a(32, (2, True), nr([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10])) # Number of paragraphs / Categories
    # a(13, (2, True), nr([10, 20, 30, 40, 50, 60, 70, 80, 90, 100])) # Number of committers 2022 / Categories
    # a(13, (2, True), nr([5, 10, 20, 30, 40, 90]))  # Number of committers 2022 / Categories



