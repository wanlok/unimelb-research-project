import os

import fasttext
import numpy as np
import pandas as pd

from document.document_sampling import get_remaining_and_categorised_file_paths, get_latest_content
from document.document_utils import get_fasttext_mappings, get_headers_and_paragraphs, preprocess, get_csv_file_tuple, \
    get_docx_file_tuple, category_names
from utils import sort_by_descending_values, csv_writer, csv_reader

fasttext_mappings = get_fasttext_mappings()
fasttext_model_file_path = 'C:\\Files\\Projects\\jupyter\\models\\2023062223234503.bin'
sample_directory_path = 'C:\\Files\\Projects\\jupyter\\samples\\'
attribute_file_path = 'C:\\Users\\WAN Tung Lok\\Desktop\\Attributes.csv'


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


def get_categorisation_results():
    categorisation_results = []
    _, categorised_file_paths = get_remaining_and_categorised_file_paths()
    for file_path in categorised_file_paths:
        file_name = file_path.split('\\')[-1]
        file_extension = file_name.split('.')[-1]
        repo = file_name.replace('.docx', '').replace('.csv', '').replace('_', '/', 1)
        if file_extension == 'docx':
            file_tuple = get_docx_file_tuple(file_path)
        elif file_extension == 'csv':
            file_tuple = get_csv_file_tuple(file_path)
        category_set = set()
        for categories in file_tuple[2]:
            for category in categories:
                category_set.add(category)
        categorisation_results.append((repo, list(category_set)))
    for file_name in os.listdir(sample_directory_path):
        file_path = f'{sample_directory_path}{file_name}'
        repo = file_name.replace('.docx', '').replace('.csv', '').replace('_', '/', 1)
        category_set = set()
        for row in csv_reader(file_path):
            for category in row[2].split(','):
                category = category.strip()
                if len(category) > 0:
                    category_set.add(category)
        categorisation_results.append((repo, list(category_set)))
    # for file_name in os.listdir('C:\\Files\\a1\\'):
    #     repo = file_name.replace('.docx', '').replace('.csv', '').replace('_', '/', 1)
    #     for r, categories in categorisation_results:
    #         if repo == r:
    #             print(f'"{repo}","{categories}"')
    return categorisation_results

    # prediction_samples = random.sample(predictions, 100)
    # for prediction in prediction_samples:
    #     print(prediction)


def value_function(value, ranges):
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
    rows, distribution_function, min, max, number_ranges = parameters
    # print(f'{len(rows)} {min} {max} {number_ranges}')
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
    return distributions


def compute_number_ranges(values, number_of_segments):
    if values is None:
        number_ranges = None
    else:
        number_ranges = []
        values = sorted(values)
        all_segments = []
        segments = []
        segment_size = int(len(values) / number_of_segments)
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


def get_parameters(column_index, number_of_segments):
    rows = []
    distribution_function = None
    min = None
    max = None
    values = None
    i = 0
    for row in csv_reader(attribute_file_path):
        if i > 1:
            value = row[column_index]
            if value.isdigit():
                value = int(value)
                if distribution_function is None:
                    distribution_function = range_function
                if min is None or value < min:
                    min = value
                if max is None or value > max:
                    max = value
                if values is None:
                    values = []
                values.append(value)
            else:
                if distribution_function is None:
                    distribution_function = value_function
            rows.append((eval(row[1]), value))
        i = i + 1
    return rows, distribution_function, min, max, compute_number_ranges(values, number_of_segments)


def dummy_dummy(column_index, number_of_segments):
    data = dict()
    parameters = get_parameters(column_index, number_of_segments)
    distributions = get_distributions(parameters)
    for distribution in distributions:
        data[distribution] = np.zeros(len(category_names))
        for i in range(len(category_names)):
            category = category_names[i]
            if category in distributions[distribution]:
                data[distribution][i] = distributions[distribution][category]
            else:
                data[distribution][i] = 0
    df = pd.DataFrame(data, index=category_names)
    print(df.to_string())
    print()
    print(df.div(len(parameters[0])).to_string())


if __name__ == '__main__':
    predictions, distributions = get_predictions_and_distributions()
    # print(len(predictions))
    print_distributions(distributions, distinct=True)
    # save_predictions(predictions)
    # categorisation_results = get_categorisation_results()

    dummy_dummy(7, 10)
