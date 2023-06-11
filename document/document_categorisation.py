import fasttext
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

from document_utils import get_df_list

train_path = 'C:\\Files\\Projects\\jupyter\\dummy.train'
test_path = 'C:\\Files\\Projects\\jupyter\\dummy.valid'
test_size = 0.1

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
    'desktop.ini'
]

label_prefix = '__label__'

def start_prediction():
    df_list = get_df_list(directory_paths, ignored_file_names)
    dataset = pd.concat(df_list, ignore_index=True).sample(frac=1)
    train, test = train_test_split(dataset, test_size=test_size)
    columns = ['labels', 'paragraph']
    fmt = '%s %s'
    encoding = 'utf-8'
    np.savetxt(train_path, train[columns].values, fmt=fmt, encoding=encoding)
    np.savetxt(test_path, test[columns].values, fmt=fmt, encoding=encoding)

    texts = []
    model = fasttext.train_supervised(input=train_path, lr=0.5, epoch=25, wordNgrams=2, bucket=200000, dim=300, loss='ova')
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
    return texts, actual_labels, predicted_labels, model.labels


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


if __name__ == '__main__':
    texts, true_labels, predicted_labels, all_labels = start_prediction()
    confusion_matrices = np.empty((0, 4))
    for i in range(len(true_labels)):
        confusion_matrix = compute_confusion_matrix(true_labels[i], predicted_labels[i])
        print(f'{i + 1} {true_labels[i]} {predicted_labels[i]} {confusion_matrix}')
        confusion_matrices = np.vstack((confusion_matrices, confusion_matrix))
    label_dict = compute_label_confusion_matrix(true_labels, predicted_labels, all_labels)
    label_max_length = len(max(label_dict.keys(), key=len).replace(label_prefix, ''))
    place_holder_1 = ''.ljust(label_max_length)
    place_holder_2 = ''.ljust(label_max_length, '-')
    print()
    print(f'{place_holder_1} TRUE POSITIVE FALSE POSITIVE FALSE NEGATIVE TRUE NEGATIVE')
    print(f'{place_holder_2} ------------- -------------- -------------- -------------')
    for key in label_dict:
        label = key.replace(label_prefix, '').ljust(label_max_length)
        true_positive, false_positive, false_negative, true_negative = label_dict[key]
        true_positive = f'{true_positive}'.rjust(13)
        false_positive = f'{false_positive}'.rjust(14)
        false_negative = f'{false_negative}'.rjust(14)
        true_negative = f'{true_negative}'.rjust(13)
        print(f'{label} {true_positive} {false_positive} {false_negative} {true_negative}')
    sum = np.sum(confusion_matrices, axis=0)
    true_positive = f'{int(sum[0])}'.rjust(13)
    false_positive = f'{int(sum[1])}'.rjust(14)
    false_negative = f'{int(sum[2])}'.rjust(14)
    true_negative = f'{int(sum[3])}'.rjust(13)
    print(f'{place_holder_2} ------------- -------------- -------------- -------------')
    print(f'{place_holder_1} {true_positive} {false_positive} {false_negative} {true_negative}')
    print()
    print(f'ACTUAL    : {np.sum(true_labels, axis=0)}')
    print(f'PREDICTED : {np.sum(predicted_labels, axis=0)}')
    precision, recall, f1_score = compute_precision_recall_f1_score(np.sum(confusion_matrices, axis=0))
    print()
    print(f'PRECISION : {precision}')
    print(f'RECALL    : {recall}')
    print(f'F1 SCORE  : {f1_score}')
