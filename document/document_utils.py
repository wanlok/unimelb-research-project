import math
import os
import re

import fasttext
import numpy as np
import pandas as pd
from docx import Document

train_path = 'C:\\Files\\Projects\\jupyter\\dummy.train'
test_path = 'C:\\Files\\Projects\\jupyter\\dummy.valid'
k_fold = 10

directory_paths = [
    'M:\\我的雲端硬碟\\UniMelb\\Research Project\\Open Coding\\20230522\\',  # 50
    'M:\\我的雲端硬碟\\UniMelb\\Research Project\\Open Coding\\20230601\\',  # 10
    'M:\\我的雲端硬碟\\UniMelb\\Research Project\\Open Coding\\20230606\\',  # 50
    'M:\\我的雲端硬碟\\UniMelb\\Research Project\\Open Coding\\20230607\\',  # 50
    'M:\\我的雲端硬碟\\UniMelb\\Research Project\\Open Coding\\20230608\\',  # 50
    'M:\\我的雲端硬碟\\UniMelb\\Research Project\\Open Coding\\20230609\\',  # 50
    'M:\\我的雲端硬碟\\UniMelb\\Research Project\\Open Coding\\20230610\\',  # 50
]

ignored_file_names = [
    'desktop.ini',
    'Completed'
]


def get_lines(table, column_index):
    lines = None
    cells = table.columns[column_index].cells
    if len(cells) == 1:
        lines = cells[0].text
    return lines


def get_type_1_header(line, dummy, found):
    header = None
    if len(set([*line])) == 1 and ('-' in line[:4] or '=' in line[:4]):
        found = not found
        if found:
            header = ' '.join(dummy)
    return found, header


def get_type_2_header(line):
    header = None
    if line[:6] == '######':
        header = line[6:]
    elif line[:5] == '#####':
        header = line[5:]
    elif line[:4] == '####':
        header = line[4:]
    elif line[:3] == '###':
        header = line[3:]
    elif line[:2] == '##':
        header = line[2:]
    elif line[:1] == '#':
        header = line[1:]
    if header is not None:
        header = header.strip()
    return header


def preprocess(s):
    s = re.sub('[^\w\d ]', '', s)
    s = re.sub(' +', ' ', s)
    s = s.strip()
    s = s.lower()
    return s


def df_dummy(directory_path, file_name, file_headers, file_paragraphs, file_categories):
    # print(paragraph_categories)
    # if len(file_categories) != len(file_paragraphs):

    data = []

    # print(f'{directory_path}{file_name}')

    for i in range(len(file_categories)):
       # if len(file_headers[i]) > 0:
        #     lines.append(' '.join(labels) + ' ' + headers[i] + ' ' + paragraphs[i])
        # else:
        #     lines.append(' '.join(labels) + ' ' + paragraphs[i])


        paragraph = preprocess(file_paragraphs[i])
        labels = map(lambda x: x.lower().replace(' ', '-'), file_categories[i])
        labels = map(lambda x: f'__label__{x}', labels)
        labels = ' '.join(labels)

        # print()
        # print(f'FILE_NAME           : {directory_path}{file_name}')
        # print(f'HEADER              : {file_headers[i]}')
        # print(f'PARAGRAPH           : {file_paragraphs[i]}')
        # print(f'CATEGORIES          : {file_categories[i]}')

        data.append({
            'name': file_name,
            'headers': file_headers[i],
            'paragraph': paragraph,
            'labels': labels
        })

    return pd.DataFrame(data)


def get_df_list(directory_paths):
    df_list = []
    for directory_path in directory_paths:
        file_names = os.listdir(directory_path)
        for file_name in file_names:
            if file_name in ignored_file_names:
                continue
            file = open(f'{directory_path}{file_name}', 'rb')
            tables = Document(file).tables
            if len(tables) == 1:
                table = tables[0]

                file_headers = []
                file_paragraphs = []
                file_categories = []

                categories = []
                for line in get_lines(table, 0).split('\n'):
                    if len(line) > 0:
                        categories.append(line)
                    elif len(categories) > 0:
                        file_categories.append(categories)
                        categories = []

                header_lines = []
                previous_header = ''
                paragraph = []
                found = False
                for line in get_lines(table, 1).split('\n'):
                    line = line.strip()
                    found, header = get_type_1_header(line, header_lines, found)
                    if header is not None:
                        header_lines.clear()
                        paragraph.clear()
                    else:
                        header_lines.append(line)
                        header = get_type_2_header(line)
                    if len(line) == 0:
                        found = False
                        header_lines.clear()
                    if header is None:
                        if len(line) > 0:
                            paragraph.append(line)
                        elif len(paragraph) > 0:
                            file_paragraph = ' '.join(map(lambda x: x.strip(), paragraph)).strip()
                            file_paragraph = f'{previous_header} {file_paragraph}'.strip()
                            file_headers.append(previous_header)
                            file_paragraphs.append(file_paragraph)
                            paragraph = []
                    if header is not None:
                        previous_header = header

                df_list.append(df_dummy(directory_path, file_name, file_headers, file_paragraphs, file_categories))
            file.close()
    return df_list


def get_dataset(random=True):
    dataset = pd.concat(get_df_list(directory_paths), ignore_index=True)
    if random:
        dataset = dataset.sample(frac=1)
    return dataset


def get_segments(dataset):
    segments = []
    dataset_size = len(dataset)
    segment_size = math.ceil(dataset_size / k_fold)
    for i in range(k_fold):
        start = i * segment_size
        if dataset_size - start >= segment_size:
            end = start + segment_size
        else:
            end = dataset_size
        segments.append(dataset[start:end])
    return segments


def get_training_and_test_set(segments, k_fold):
    training_set = None
    test_set = None
    training_set_segments = []
    for i in range(len(segments)):
        if i == k_fold:
            test_set = segments[i]
        else:
            training_set_segments.append(segments[i])
    if len(training_set_segments) > 0:
        training_set = pd.concat(training_set_segments, ignore_index=True)
    return training_set, test_set


def get_fasttext_model(training_set, test_set):
    columns = ['labels', 'paragraph']
    fmt = '%s %s'
    encoding = 'utf-8'
    np.savetxt(train_path, training_set[columns].values, fmt=fmt, encoding=encoding)
    np.savetxt(test_path, test_set[columns].values, fmt=fmt, encoding=encoding)
    return fasttext.train_supervised(input=train_path, lr=0.5, epoch=25, wordNgrams=2, bucket=200000, dim=300, loss='ova')



# if __name__ == '__main__':
