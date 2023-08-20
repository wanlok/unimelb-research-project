import ast
import os
from functools import reduce

import fasttext
import numpy as np
import pandas as pd
from scipy.stats import spearmanr

from document.document_sampling import get_remaining_and_categorised_file_paths
from document.document_utils import get_fasttext_mappings, get_headers_and_paragraphs, preprocess, get_csv_file_tuple, get_docx_file_tuple, category_names
from repository import package_manager_languages
from utils import sort_by_descending_values, csv_writer, csv_reader, expand, contain_string, attribute_file_path, \
    get_latest_content, repos, is_contain_alphanumeric

fasttext_mappings = get_fasttext_mappings()
fasttext_model_file_path = 'C:\\Files\\Projects\\jupyter\\models\\2023062223234503.bin'
sample_directory_path = 'C:\\Files\\Projects\\jupyter\\samples\\'


def print_distributions(distributions, distinct=False):
    distribution_counts = dict()
    max_length = 0
    for category in distributions:
        if distinct:
            distribution_counts[category] = len(set(distributions[category]))
        else:
            distribution_counts[category] = len(distributions[category])
        category = fasttext_mappings[category]
        if len(category) > max_length:
            max_length = len(category)
    for category in sort_by_descending_values(distribution_counts):
        category_name = fasttext_mappings[category].ljust(max_length)
        if distinct:
            print(f'{category_name}  {len(set(distributions[category]))}')
        else:
            print(f'{category_name}  {len(distributions[category])}')
    print()


def get_predictions_and_distributions():
    predictions = dict()
    distributions = dict()
    remaining_file_paths, categorised_file_paths = get_remaining_and_categorised_file_paths()
    model = fasttext.load_model(fasttext_model_file_path)
    for file_path in remaining_file_paths:
        content = get_latest_content(file_path)
        headers, paragraphs = get_headers_and_paragraphs(content, False)
        file_predictions = list()
        for i in range(len(paragraphs)):
            header = headers[i]
            paragraph = paragraphs[i]
            text = preprocess(f'{header} {paragraph}'.strip())
            categories = model.predict(text, k=-1, threshold=0.2)
            file_predictions.append((header, paragraph, categories))
        predictions[file_path] = file_predictions
        for _, _, categories in file_predictions:
            for category in categories[0]:
                if category in distributions:
                    distributions[category].append(file_path)
                else:
                    distributions[category] = [file_path]
    return predictions, distributions


def save_predictions(predictions, required_categories=[]):
    for file_name in os.listdir(sample_directory_path):
        os.remove(f'{sample_directory_path}{file_name}')
    for file_path in predictions:
        file_name = file_path.split('\\')[-1]
        file_predictions = predictions[file_path]
        found = len(required_categories) == 0
        for i in range(len(file_predictions)):
            header, paragraph, categories = file_predictions[i]
            categories = list(map(lambda x: fasttext_mappings[x], categories[0]))
            file_predictions[i] = (header, paragraph, categories)
            for required_category in required_categories:
                if required_category in categories:
                    found = True
                    break
        if found:
            file_csv_writer = csv_writer(f'{sample_directory_path}{file_name}', mode='w')
            for header, paragraph, categories in file_predictions:
                categories = ','.join(categories)
                file_csv_writer.writerow([f'{header}', f'{paragraph}', f'{categories}'])


def count_number_of_words(titles, contents, count_title):
    number_of_word_list = []
    for title, content in zip(titles, contents):
        number_of_words = 0
        title_slices = list(filter(lambda x: is_contain_alphanumeric(x), title.replace('\n', ' ').split(' ')))
        content_slices = list(filter(lambda x: is_contain_alphanumeric(x), content.replace('\n', ' ').split(' ')))
        # print(title_slices)
        # print(content_slices)
        if count_title:
            number_of_words = number_of_words + len(title_slices)
        number_of_words = number_of_words + len(content_slices)
        number_of_word_list.append(number_of_words)
    return number_of_word_list


def update_repo_category_dict_1(repo, category_list, word_counts, repo_dict):
    category_dict = dict()
    for categories, word_count in zip(category_list, word_counts):
        for category in categories:
            if len(category) > 0:
                if category in category_dict:
                    category_dict[category] = category_dict[category] + word_count
                else:
                    category_dict[category] = word_count
    repo_dict[repo] = category_dict


def update_repo_category_dict_2(repo, category_list, repo_dict):
    category_dict = dict()
    for categories in category_list:
        for category in categories:
            if category in category_dict:
                category_dict[category] = category_dict[category] + 1
            else:
                category_dict[category] = 1
    repo_dict[repo] = category_dict


def get_repo_categorisation_results():
    repo_dict = dict()
    _, categorised_file_paths = get_remaining_and_categorised_file_paths()
    for file_path in categorised_file_paths:
        file_name = file_path.split('\\')[-1]
        file_extension = file_name.split('.')[-1]
        repo = file_name.replace('.docx', '').replace('.csv', '').replace('_', '/', 1)
        if file_extension == 'docx':
            file_tuple = get_docx_file_tuple(file_path)
        elif file_extension == 'csv':
            file_tuple = get_csv_file_tuple(file_path)
        # update_repo_category_dict_1(repo, file_tuple[2], count_number_of_words(file_tuple[0], file_tuple[1], False), repo_dict)
        update_repo_category_dict_2(repo, file_tuple[2], repo_dict)
    for file_name in os.listdir(sample_directory_path):
        file_path = f'{sample_directory_path}{file_name}'
        repo = file_name.replace('.docx', '').replace('.csv', '').replace('_', '/', 1)
        titles = []
        contents = []
        categories = []
        for row in csv_reader(file_path):
            titles.append(row[0])
            contents.append(row[1])
            categories.append(row[2].split(','))
        # update_repo_category_dict_1(repo, categories, count_number_of_words(titles, contents, True), repo_dict)
        update_repo_category_dict_2(repo, categories, repo_dict)
    return repo_dict


def value_function(value, ranges):
    return value


def list_function(value, ranges):
    return value


def range_function(value, ranges):
    if value == 'None':
        range_label = ranges[0][2]
    else:
        for start, end, r_l in ranges:
            if start <= value <= end:
                range_label = r_l
    return range_label


def get_distributions(parameters):
    distributions = dict()
    rows, distribution_function, number_ranges, title, sub_title = parameters
    for row in rows:
        categories, value = row
        distribution = distribution_function(value, number_ranges)
        if distribution in distributions:
            for category in categories:
                if category in distributions[distribution]:
                    distributions[distribution][category] = distributions[distribution][category] + 1
                else:
                    distributions[distribution][category] = 1
        else:
            distributions[distribution] = dict()
            for category in categories:
                distributions[distribution][category] = 1
    return distributions, title, sub_title


def compute_number_ranges(values, number_of_segments):
    if values is None or number_of_segments is None:
        number_ranges = None
    elif len(values) == 1:
        number_ranges = [(values[0], values[0], f'{values[0]} - {values[0]}')]
    else:
        number_ranges = []
        values = sorted(values)
        all_segments = []
        segments = []
        if len(values) < number_of_segments:
            segment_size = len(values)
        else:
            segment_size = int(len(values) / number_of_segments)
        # print(f'SEGMENT_SIZE: {segment_size}')
        for value in values:
            if len(segments) < segment_size:
                segments.append(value)
            elif segments[-1] == value:
                segments.append(value)
            else:
                all_segments.append(segments)
                segments = [value]
        if len(segments) > 0:
            if len(segments) < segment_size * 1 / 10:
                all_segments[-1].extend(segments)
            else:
                all_segments.append(segments)
        all_segment_length = len(all_segments)
        for i in range(all_segment_length):
            start = all_segments[i][0]
            end = all_segments[i][-1]
            if i == all_segment_length - 1:
                number_ranges.append((start, end, f'{start} or above'))
            else:
                number_ranges.append((start, end, f'{start} - {end}'))
    return number_ranges


def get_parameters(column_index, as_count, number_of_segments):
    rows = []
    distribution_function = None
    values = None
    title = None
    sub_title = None
    i = 0
    for row in csv_reader(attribute_file_path):
        if i == 0:
            title = expand(row)[column_index]
        elif i == 1:
            sub_title = row[column_index]
        else:
            value = row[column_index]
            if as_count:
                value = f'{len(value)}'
            if value.isdigit():
                if distribution_function is None:
                    distribution_function = range_function
                value = int(value)
                if values is None:
                    values = []
                values.append(value)
            else:
                if distribution_function is None:
                    distribution_function = value_function
            rows.append((eval(row[1]), value))
        i = i + 1
    return rows, distribution_function, compute_number_ranges(values, number_of_segments), title, sub_title


def get_distributions_if_list(distributions, keys):
    if_list = False
    item_list = []
    item_set = set()
    for key in keys:
        if key[0] == '[':
            if_list = True
            key_items = eval(key)
            if type(key_items) == list and len(key_items) > 0:
                for key_item in key_items:
                    item_set.add(key_item)
                counts = np.zeros(len(category_names))
                for i in range(len(category_names)):
                    if category_names[i] in distributions[key]:
                        counts[i] = distributions[key][category_names[i]]
                item_dict = dict()
                for key_item in key_items:
                    item_dict.update({key_item: counts})
                item_list.append(item_dict)
    new_distributions = dict()
    for key_item in item_set:
        counts = []
        for item in item_list:
            if key_item in item:
                counts.append(item[key_item])
        results = pd.DataFrame(counts).sum().tolist()
        new_distributions[key_item] = dict()
        for i in range(len(category_names)):
            if results[i] > 0:
                new_distributions[key_item][category_names[i]] = results[i]
    return if_list, new_distributions


def dummy_dummy(column_index, as_count=False, number_of_segments=None, filter_keys=[]):
    data = dict()
    parameters = get_parameters(column_index, as_count, number_of_segments)
    distributions, title, sub_title = get_distributions(parameters)
    if parameters[2] is None:
        keys = sorted(distributions.keys(), key=str.casefold)
        if_list, new_distributions = get_distributions_if_list(distributions, keys)
        if if_list:
            distributions = new_distributions
            keys = sorted(distributions.keys(), key=str.casefold)
    else:
        keys = list(map(lambda x: x[2], parameters[2]))
    for key in keys:
        valid = len(filter_keys) == 0
        for filter_key in filter_keys:
            if filter_key.lower() == key.lower():
                valid = True
                break
        if valid:
            data[key] = np.zeros(len(category_names))
            for i in range(len(category_names)):
                category = category_names[i]
                if category in distributions[key]:
                    data[key][i] = distributions[key][category]
                else:
                    data[key][i] = 0
    df = pd.DataFrame(data, index=category_names)
    if len(sub_title) > 0:
        print(f'{title} - {sub_title}')
    else:
        print(f'{title}')
    print(df.to_string())
    print()


def parse_node(node):
    number_of_segments = None
    column_as_count = None
    filter_list = None
    assigned_type = None
    number_ranges = None
    if type(node) == int:
        column_index = node
    else:
        length = len(node)
        if length == 1:
            column_index = node
        elif length == 2:
            column_index, number_of_segments = node
        elif length == 3:
            column_index, number_of_segments, column_as_count = node
        elif length == 4:
            column_index, number_of_segments, column_as_count, filter_list = node
        elif length == 5:
            column_index, number_of_segments, column_as_count, filter_list, assigned_type = node
        else:
            column_index, number_of_segments, column_as_count, filter_list, assigned_type, number_ranges = node
    return column_index, number_of_segments, column_as_count, filter_list, assigned_type, number_ranges


def get_values(node, rows):
    title = None
    sub_title = None
    values = []
    unique_values = set()
    distribution_function = None
    column_index, number_of_segments, column_as_count, filter_list, assigned_type, number_ranges = parse_node(node)
    i = 0
    for row in rows:
        if i == 0:
            title = expand(row)[column_index]
        elif i == 1:
            sub_title = row[column_index]
        else:
            value = row[column_index]
            if len(value) > 0 and value[0] == '[' and value[-1] == ']':
                value = eval(value)
            if column_as_count:
                value = f'{len(value)}'
            if type(value) == list:
                unique_values.update(value)
                if distribution_function is None:
                    distribution_function = value_function
            elif assigned_type is not str and value.isdigit():
                value = int(value)
                unique_values.add(value)
                if distribution_function is None:
                    distribution_function = range_function
            else:
                unique_values.add(value)
                if distribution_function is None:
                    distribution_function = value_function
            values.append(value)
        i = i + 1
    unique_values = sorted(list(unique_values))
    if number_ranges is None:
        number_ranges = compute_number_ranges(values, number_of_segments)
    if number_ranges is None:
        keys = unique_values
    else:
        keys = number_ranges
    return title, sub_title, values, unique_values, number_ranges, keys, distribution_function, filter_list


def get_rows():
    rows = []
    for row in csv_reader(attribute_file_path):
        rows.append(row)
    return rows


def get_matching_index_set(value, data):
    indexes = set()
    values = data[2]
    number_ranges = data[4]
    distribution_function = data[6]
    for i in range(len(values)):
        if number_ranges is None:
            if type(values[i]) == list:
                for j in range(len(values[i])):
                    if value == values[i][j]:
                        indexes.add(i)
                        break
            elif value == values[i]:
                indexes.add(i)
        elif value[2] == distribution_function(values[i], number_ranges):
            indexes.add(i)
    return indexes


def is_filtered(filter_list, key):
    return filter_list is None or len(filter_list) == 0 or key in filter_list


def get_df_and_match_rows(vertical_node, horizontal_node, rows):
    data = dict()
    vertical = get_values(vertical_node, rows)
    vertical_dict = dict()
    vertical_count_dict = dict()
    horizontal = get_values(horizontal_node, rows)
    horizontal_dict = dict()
    horizontal_count_dict = dict()
    for horizontal_key in horizontal[5]:
        horizontal_indexes = get_matching_index_set(horizontal_key, horizontal)
        horizontal_count_dict[horizontal_key] = len(horizontal_indexes)
        counts = []
        for vertical_key in vertical[5]:
            vertical_indexes = get_matching_index_set(vertical_key, vertical)
            vertical_count_dict[vertical_key] = len(vertical_indexes)
            match_rows = [rows[2:][i] for i in horizontal_indexes.intersection(vertical_indexes)]
            counts.append(len(match_rows))
            if is_filtered(vertical[7], vertical_key):
                if vertical_key in vertical_dict:
                    vertical_dict[vertical_key].append(match_rows)
                else:
                    vertical_dict[vertical_key] = [match_rows]
            if is_filtered(horizontal[7], horizontal_key):
                if horizontal_key in horizontal_dict:
                    horizontal_dict[horizontal_key].append(match_rows)
                else:
                    horizontal_dict[horizontal_key] = [match_rows]
        if is_filtered(horizontal[7], horizontal_key):
            if horizontal[4] is None:
                data[horizontal_key] = counts
            else:
                data[horizontal_key[2]] = counts
    if vertical[4] is None:
        df = pd.DataFrame(data, index=vertical[3])
    else:
        df = pd.DataFrame(data, index=map(lambda x: x[2], vertical[4]))
    vertical_dict = combine_rows(vertical_dict, rows[:2])
    horizontal_dict = combine_rows(horizontal_dict, rows[:2])
    return vertical[0], vertical[1], horizontal[0], horizontal[1], df, vertical_dict, horizontal_dict, vertical_count_dict, horizontal_count_dict


def combine_rows(my_dict, title_rows):
    my_new_dict = dict()
    for key in my_dict:
        rows = []
        repo_dict = dict()
        for r in my_dict[key]:
            for row in r:
                repo = row[0]
                if repo not in repo_dict:
                    repo_dict[repo] = 1
                    rows.append(row)
        my_new_dict[key] = title_rows + rows
    return my_new_dict


def get_data_frame_title(titles):
    s = ''
    for i in range(len(titles)):
        title = titles[i]
        if i > 0:
            s = s + f' / '
        if title[1] is None:
            s = s + f'{title[0]}'
        else:
            if type(title[1]) is tuple:
                s = s + f'{title[0]} ({title[1][2]})'
            else:
                s = s + f'{title[0]} ({title[1]})'
    return s


def compute_data_frames_recur(leaf_node, nodes, titles, index, horizontal_dict):
    if index < len(nodes):
        first = True
        for key in horizontal_dict:
            _, _, horizontal_title, horizontal_sub_title, df, _, next_horizontal_dict, vertical_count_dict, horizontal_count_dict = get_df_and_match_rows(leaf_node, nodes[index], horizontal_dict[key])
            if first:
                titles.append((f'{horizontal_title} {horizontal_sub_title}'.strip(), None))
                first = False
            titles[index + 1] = (titles[index + 1][0], key)
            print(get_data_frame_title(titles))
            print()
            sum = df.sum().sum()
            df = df / sum
            print(df.to_string())
            print()
            print(f'{sum} {df.sum().sum()}')
            print()
            compute_data_frames_recur(leaf_node, nodes, titles.copy(), index + 1, next_horizontal_dict)


def get_count_list(df, count_dict):
    counts = []
    for i in df.index.tolist():
        value = 0
        for j in count_dict:
            _, _, k = j
            if i == k:
                value = count_dict[j]
        counts.append(value)
    return counts


def compute_data_frames(leaf_node, nodes):
    vertical_title, vertical_sub_title, horizontal_title, horizontal_sub_title, df, vertical_dict, horizontal_dict, vertical_count_dict, horizontal_count_dict = get_df_and_match_rows(leaf_node, nodes.pop(0), get_rows())
    vertical_counts = get_count_list(df, vertical_count_dict)
    # print(vertical_counts)
    titles = [
        (f'{vertical_title} {vertical_sub_title}'.strip(), None),
        (f'{horizontal_title} {horizontal_sub_title}'.strip(), None)
    ]
    # divide by the corresponding language
    print(get_data_frame_title(titles))
    print()
    # print(df.to_string())
    print(df.div(vertical_counts, axis=0).to_string())
    print()
    print(f'{vertical_counts} {df.sum().sum()}')
    print()
    # print('Hello World')
    # print(spearmanr(df))
    compute_data_frames_recur(leaf_node, nodes, titles.copy(), 0, horizontal_dict)


def get_data_frame(leaf_node, nodes):
    vertical_title, vertical_sub_title, horizontal_title, horizontal_sub_title, df, vertical_dict, horizontal_dict, vertical_count_dict, horizontal_count_dict = get_df_and_match_rows(
        leaf_node, nodes.pop(0), get_rows())
    return df


def show_categorisation(repo, repo_dict):
    category_dict = repo_dict[repo]
    counts = []
    for category in category_names:
        if category in category_dict:
            counts.append(category_dict[category])
        else:
            counts.append(0)
    print(f'{repo},{counts},{category_dict}')



if __name__ == '__main__':
    # predictions, distributions = get_predictions_and_distributions()
    # # print(len(predictions))
    # print_distributions(distributions, distinct=True)
    # # save_predictions(predictions)

    repos(show_categorisation, get_repo_categorisation_results())

    #
    # dummy_dummy(7, number_of_segments=5)
    # dummy_dummy(12, number_of_segments=5)
    # dummy_dummy(17, number_of_segments=5)
    # dummy_dummy(22, number_of_segments=5)
    # dummy_dummy(23)

    # {'Groovy', 'Kotlin', 'Python', 'C#', 'Go', 'JavaScript', 'C', '.NET', 'TypeScript', 'Java', 'Ruby', 'Scala', 'C++', 'PHP'}
    # print(contain_string('Kotlin123', package_manager_languages, True))


    # languages = list(package_manager_languages) + ['ASP.NET', 'Classic ASP', 'F#', 'Visual Basic .NET', 'Visual Basic 6.0']
    # dummy_dummy(23)
    # dummy_dummy(25)
    # dummy_dummy(24)
    # dummy_dummy(27, as_count=True, number_of_segments=5)


    # programming_languages = list(package_manager_languages) + ['ASP.NET', 'Classic ASP', 'F#', 'Visual Basic .NET', 'Visual Basic 6.0']

    # compute_data_frames((1, None, None), [(7, None, 5), (12, None, 5), (17, None, 5)])
    # compute_data_frames((2, None, None, None), [(24, None, None, None), (25, None, None, programming_languages), (1, None, None, None, str)])
    # compute_data_frames(24, [24])

    # compute_data_frames(2, [(8, 5)])
    # compute_data_frames(2, [24, (25, None, None, programming_languages)])

    # compute_data_frames(2, [(29, 10)])

    # number_ranges = [
    #     (0, 1000, f'0 - 1000'),
    #     (1001, 10000, f'1001 - 10000'),
    #     (10001, 20000, f'10001 - 20000'),
    #     (20001, 30000, f'20001 - 30000'),
    #     (30001, 40000, f'30001 - 40000'),
    #     (40001, 50000, f'40001 - 50000'),
    #     (50001, 60000, f'50001 - 60000'),
    #     (60001, 70000, f'60001 - 70000'),
    #     (70001, 80000, f'70001 - 80000'),
    #     (80001, 90000, f'80001 - 90000'),
    #     (90001, 100000, f'90001 - 100000'),
    #     (100001, 999999999, f'100001 or above')
    # ]

    # number_ranges.append((0, 1000, f'0 - 1000'))
    # number_ranges.append((1001, 2000, f'1001 - 2000'))
    # number_ranges.append((2001, 3000, f'2001 - 3000'))
    # number_ranges.append((3001, 4000, f'3001 - 4000'))
    # number_ranges.append((4001, 5000, f'4001 - 5000'))
    # number_ranges.append((5001, 6000, f'5001 - 6000'))
    # number_ranges.append((6001, 7000, f'6001 - 7000'))
    # number_ranges.append((7001, 8000, f'7001 - 8000'))
    # number_ranges.append((8001, 9000, f'8001 - 9000'))
    # number_ranges.append((9001, 10000, f'9001 - 10000'))
    # number_ranges.append((10001, 999999999, f'10001 or above'))

    # compute_data_frames((29, 10, None, None, None, number_ranges), [(3, 5)])
    # compute_data_frames((29, None, None, None, None, number_ranges), [2])
    # compute_data_frames((30, None, None, None, None, number_ranges), [2])
    # compute_data_frames((31, None, None, None, None, number_ranges), [2])
    # compute_data_frames((32, None, None, None, None, number_ranges), [2])
    # compute_data_frames((3, None, None, None, None, number_ranges), [2])


    # compute_data_frames(2, [(3, 2)])
    # compute_data_frames((8, 5), [24])
    # compute_data_frames((2), [(25, None, None, programming_languages), (3, 3)])
    # compute_data_frames(2, [24, (25, None, None, programming_languages)])
    # compute_data_frames((2, None, None, None), [(1, None, None, None, str), (25, None, None, programming_languages)])
    # compute_data_frames((23, None, None, None), [(23, None, None, None)])

