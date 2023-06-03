import os
import re

import fasttext
import numpy as np
import pandas as pd
from docx import Document
from sklearn.model_selection import train_test_split

from document_utils import get_lines, get_type_1_header, get_type_2_header


def preprocess(s):
    s = re.sub('[^\w\d ]', '', s)
    s = re.sub(' +', ' ', s)
    s = s.strip()
    s = s.lower()
    return s


def df_dummy(file_name, file_headers, file_paragraphs, file_categories):
    # print(paragraph_categories)
    # if len(file_categories) != len(file_paragraphs):

    data = []

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
        # print(f'FILE_NAME           : {file_name}')
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


def get_document_contents(test_size, train_path, test_path):
    dfs = []
    directory_path = 'C:\\Files\\c\\Completed\\'
    file_names = os.listdir(directory_path)
    # print(f'LENGTH: {len(file_names)}')
    for file_name in file_names:
        f = open(f'{directory_path}{file_name}', 'rb')
        tables = Document(f).tables
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
            for line in get_lines(table, 1).split('\n'):
                header = get_type_1_header(line, header_lines)
                if header is not None:
                    header_lines.clear()
                    paragraph.clear()
                else:
                    header_lines.append(line)
                    header = get_type_2_header(line)
                if len(line) == 0:
                    header_lines.clear()
                if header is None:
                    if len(line) > 0:
                        paragraph.append(line)
                    elif len(paragraph) > 0:
                        file_headers.append(previous_header)
                        file_paragraphs.append(' '.join(map(lambda x: x.strip(), paragraph)))
                        paragraph = []
                if header is not None:
                    previous_header = header

            dfs.append(df_dummy(file_name, file_headers, file_paragraphs, file_categories))
        f.close()
    train, test = train_test_split(pd.concat(dfs, ignore_index=True), test_size=test_size)
    columns = ['labels', 'paragraph']
    fmt = '%s %s'
    encoding = 'utf-8'
    np.savetxt(train_path, train[columns].values, fmt=fmt, encoding=encoding)
    np.savetxt(test_path, test[columns].values, fmt=fmt, encoding=encoding)


def evaluate_categorisation_performance():
    train_path = 'C:\\Files\\Projects\\jupyter\\dummy.train'
    test_path = 'C:\\Files\\Projects\\jupyter\\dummy.valid'
    list_i = []
    for i in range(0, 1):
        list_j = []
        for j in range(0, 10):
            get_document_contents(0.1, train_path, test_path)
            model = fasttext.train_supervised(input=train_path, lr=0.5, epoch=25, wordNgrams=2, bucket=200000, dim=300,
                                              loss='ova')
            list_j.append(model.test(test_path))

        sum_precision = 0
        sum_recall = 0
        sum_f1 = 0
        for row in list_j:
            number_of_samples = row[0]
            precision = row[1]
            recall = row[2]
            f1 = (2 * precision * recall) / (precision + recall)
            sum_precision = sum_precision + precision
            sum_recall = sum_recall + recall
            sum_f1 = sum_f1 + f1
            print(f'NUMBER_OF_SAMPLES: {number_of_samples}, PRECISION: {precision}, RECALL: {recall}, F1: {f1}')
        # print()
        # print(f'PRECISION: {sum_precision / len(list_j)}, RECALL: {sum_recall / len(list_j)}')
        length_j = len(list_j)
        list_i.append((sum_precision / length_j, sum_recall / length_j, sum_f1 / length_j))
    for avg_preision, avg_recall, avg_f1 in list_i:
        print(f'AVG_PRECISION: {avg_preision}, AVG_RECALL: {avg_recall}, AVG_F1: {avg_f1}')


def get_data(file_path):
    data = []
    with open(file_path, encoding='utf-8') as f:
        for line in f:
            text = []
            labels = []
            for s in line.split(' '):
                if s[:9] == '__label__':
                    labels.append(s)
                else:
                    text.append(s)
            data.append((' '.join(text[:-1]), labels))
    return data


if __name__ == '__main__':
    train_path = 'C:\\Files\\Projects\\jupyter\\dummy.train'
    test_path = 'C:\\Files\\Projects\\jupyter\\dummy.valid'
    get_document_contents(0.1, train_path, test_path)
    test_data = get_data(test_path)
    model = fasttext.train_supervised(input=train_path, lr=0.5, epoch=25, wordNgrams=2, bucket=200000, dim=300,
                                      loss='ova')
    number_of_samples, precision, recall = model.test(test_path)
    f1 = (2 * precision * recall) / (precision + recall)
    print(f'NUMBER_OF_SAMPLES: {number_of_samples}, PRECISION: {precision}, RECALL: {recall}, F1: {f1}')
    all_labels = set()
    label_dict = dict()
    for i in range(len(test_data)):
        text, true_labels = test_data[i]
        predicted_labels = list(model.predict(text, k=len(true_labels))[0])
        true_labels.sort()
        predicted_labels.sort()
        all_labels.update(true_labels)
        all_labels.update(predicted_labels)
        test_data[i] = (text, true_labels, predicted_labels)
    for text, true_labels, predicted_labels in test_data:

        for label in all_labels:
            if label in true_labels and label in predicted_labels:
                true_positive = 1
            else:
                true_positive = 0
            if label not in true_labels and label in predicted_labels:
                false_positive = 1
            else:
                false_positive = 0
            if label in true_labels and label not in predicted_labels:
                false_negative = 1
            else:
                false_negative = 0
            if label not in true_labels and label not in predicted_labels:
                true_negative = 1
            else:
                true_negative = 0
            if label in label_dict:
                true_positive_sum, false_positive_sum, false_negative_sum, true_negative_sum = label_dict[label]
                label_dict[label] = (
                    true_positive_sum + true_positive,
                    false_positive_sum + false_positive,
                    false_negative_sum + false_negative,
                    true_negative_sum + true_negative
                )
            else:
                label_dict[label] = (true_positive, false_positive, false_negative, true_negative)
    precision_sum = 0
    for label in label_dict:
        true_positive_sum, false_positive_sum, false_negative_sum, true_negative_sum = label_dict[label]
        if true_positive_sum > 0 or false_positive_sum > 0:
            precision = true_positive_sum / (true_positive_sum + false_positive_sum)
        else:
            precision = 0
        if true_positive_sum > 0 or false_negative_sum > 0:
            recall = true_positive_sum / (true_positive_sum + false_negative_sum)
        else:
            recall = 0
        print(f'LABEL: {label} PRECISION: {precision}, RECALL: {recall}')
