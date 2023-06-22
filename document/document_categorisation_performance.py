import math
from datetime import datetime

import numpy as np
import pandas as pd

from document_utils import get_dataset, get_fasttext_model, test_path, k_fold, model_save_path, label_prefix


def start_prediction(training_set, test_set, save_path):
    texts = []
    model = get_fasttext_model(training_set, test_set, save_path)
    actual_labels = np.empty((0, len(model.labels)))
    predicted_labels = np.empty((0, len(model.labels)))
    with open(test_path, encoding='utf-8') as f:
        for line in f:
            text = []
            labels = np.zeros(len(model.labels))
            for s in line.split(' '):
                if s[:9] == label_prefix:
                    for i in range(len(model.labels)):
                        if model.labels[i] == s:
                            labels[i] = 1
                else:
                    text.append(s)
            text = ' '.join(text[:-1])
            texts.append(text)
            actual_labels = np.vstack((actual_labels, labels))
            labels = np.zeros(len(model.labels))
            prediction = model.predict(text, k=-1, threshold=0.2)
            for label in prediction[0]:
                for i in range(len(model.labels)):
                    if model.labels[i] == label:
                        labels[i] = 1
            predicted_labels = np.vstack((predicted_labels, labels))
    return texts, model.labels, actual_labels, predicted_labels


def compute_f1_score(precision, recall):
    if precision > 0 or recall > 0:
        f1 = (2 * precision * recall) / (precision + recall)
    else:
        f1 = float("NAN")
    return f1


def compute_precision_recall_f1_score(confusion_matrix):
    true_positive, false_positive, false_negative, true_negative = confusion_matrix
    if true_positive > 0 or false_positive > 0:
        precision = true_positive / (true_positive + false_positive)
    else:
        precision = float("NAN")
    if true_positive > 0 or false_negative > 0:
        recall = true_positive / (true_positive + false_negative)
    else:
        recall = float("NAN")
    return precision, recall, compute_f1_score(precision, recall)


def compute_confusion_matrix(true_labels, predicted_labels):
    true_positive = 0
    false_positive = 0
    false_negative = 0
    true_negative = 0
    for i in range(len(predicted_labels)):
        if true_labels[i] == 1 and predicted_labels[i] == 1:
            true_positive = true_positive + 1
        if true_labels[i] == 0 and predicted_labels[i] == 1:
            false_positive = false_positive + 1
        if true_labels[i] == 1 and predicted_labels[i] == 0:
            false_negative = false_negative + 1
        if true_labels[i] == 0 and predicted_labels[i] == 0:
            true_negative = true_negative + 1
    return np.array([true_positive, false_positive, false_negative, true_negative])


def compute_label_confusion_matrix(true_labels, predicted_labels, all_labels):
    label_dict = dict()
    for i in range(len(true_labels)):
        for j in range(len(all_labels)):
            if true_labels[i][j] == 1 and predicted_labels[i][j] == 1:
                true_positive = 1
            else:
                true_positive = 0
            if true_labels[i][j] == 0 and predicted_labels[i][j] == 1:
                false_positive = 1
            else:
                false_positive = 0
            if true_labels[i][j] == 1 and predicted_labels[i][j] == 0:
                false_negative = 1
            else:
                false_negative = 0
            if true_labels[i][j] == 0 and predicted_labels[i][j] == 0:
                true_negative = 1
            else:
                true_negative = 0
            label = all_labels[j]
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
    return label_dict


def output(start, end, all_labels, true_labels, predicted_labels, predicted_results, save_path):
    confusion_matrices = np.empty((0, 4))
    for i in range(len(true_labels)):
        confusion_matrix = compute_confusion_matrix(true_labels[i], predicted_labels[i])
        # print(f'{i + 1} {true_labels[i]} {predicted_labels[i]} {confusion_matrix}')
        confusion_matrices = np.vstack((confusion_matrices, confusion_matrix))
    label_dict = compute_label_confusion_matrix(true_labels, predicted_labels, all_labels)
    label_max_length = len(max(label_dict.keys(), key=len).replace(label_prefix, ''))
    label_place_holder = 'LABEL'.ljust(label_max_length)
    total_place_hodler = 'TOTAL'.ljust(label_max_length)
    hyphen_place_holder = ''.ljust(label_max_length, '-')
    print()
    print(f'{label_place_holder}  TRUE POSITIVE  FALSE POSITIVE  FALSE NEGATIVE  TRUE NEGATIVE')
    print(f'{hyphen_place_holder}  -------------  --------------  --------------  -------------')
    for key in label_dict:
        label = key.replace(label_prefix, '').ljust(label_max_length)
        true_positive, false_positive, false_negative, true_negative = label_dict[key]
        true_positive = f'{true_positive}'.rjust(13)
        false_positive = f'{false_positive}'.rjust(14)
        false_negative = f'{false_negative}'.rjust(14)
        true_negative = f'{true_negative}'.rjust(13)
        print(f'{label}  {true_positive}  {false_positive}  {false_negative}  {true_negative}')
    sum = np.sum(confusion_matrices, axis=0)
    true_positive = f'{int(sum[0])}'.rjust(13)
    false_positive = f'{int(sum[1])}'.rjust(14)
    false_negative = f'{int(sum[2])}'.rjust(14)
    true_negative = f'{int(sum[3])}'.rjust(13)
    print(f'{hyphen_place_holder}  -------------  --------------  --------------  -------------')
    print(f'{total_place_hodler}  {true_positive}  {false_positive}  {false_negative}  {true_negative}')
    print()
    # print(f'RANGE     : {start} - {end}')
    # print(f'ACTUAL    : {np.sum(true_labels, axis=0)}')
    # print(f'PREDICTED : {np.sum(predicted_labels, axis=0)}')
    precision, recall, f1_score = compute_precision_recall_f1_score(np.sum(confusion_matrices, axis=0))
    # print(f'PRECISION : {precision}')
    # print(f'RECALL    : {recall}')
    # print(f'F1 SCORE  : {f1_score}')
    # print()
    predicted_results.append((start, end, precision, recall, f1_score, save_path))


def output_2(predicted_results):
    precision_sum = 0
    recall_sum = 0
    f1_score_sum = 0
    print(f'#        RANGE        PRECISION           RECALL              F1 SCORE            FILE NAME       ')
    print(f'-------  -----------  ------------------  ------------------  ------------------  ----------------')
    i = 0
    for start, end, precision, recall, f1_score, save_path in predicted_results:
        i = i + 1
        j = f'{i}'.rjust(7)
        range = f'{start} - {end - 1}'.rjust(11)
        precision_sum = precision_sum + precision
        precision = f'{precision}'.rjust(18)
        recall_sum = recall_sum + recall
        recall = f'{recall}'.rjust(18)
        f1_score_sum = f1_score_sum + f1_score
        f1_score = f'{f1_score}'.rjust(18)
        file_name = save_path.split('\\')[-1][:-4]
        print(f'{j}  {range}  {precision}  {recall}  {f1_score}  {file_name}')
    precision_avg = f'{precision_sum / k_fold}'.rjust(18)
    recall_avg = f'{recall_sum / k_fold}'.rjust(18)
    f1_score_avg = f'{f1_score_sum / k_fold}'.rjust(18)
    print(f'-------  -----------  ------------------  ------------------  ------------------  ----------------')
    print(f'AVERAGE               {precision_avg}  {recall_avg}  {f1_score_avg}')


if __name__ == '__main__':
    dataset = get_dataset()
    dataset_size = len(dataset)
    segment_size = math.ceil(dataset_size / k_fold)
    predicted_results = []
    current_date_time = datetime.now().strftime("%Y%m%d%H%M%S")
    for i in range(k_fold):
        start = i * segment_size
        if dataset_size - start >= segment_size:
            end = start + segment_size
        else:
            end = dataset_size
        training_set = pd.concat([dataset[:start], dataset[end:]], ignore_index=True)
        test_set = dataset[start:end]
        save_path = f'{i + 1}'.rjust(2, '0')
        save_path = f'{model_save_path}{current_date_time}{save_path}.bin'
        _, all_labels, true_labels, predicted_labels = start_prediction(training_set, test_set, save_path)
        output(start, end, all_labels, true_labels, predicted_labels, predicted_results, save_path)
    output_2(predicted_results)
