import random

import fasttext

from document.document_sampling import get_remaining_and_categorised_file_paths, get_latest_content
from document.document_utils import get_fasttext_mappings, get_headers_and_paragraphs, preprocess
from utils import sort_by_descending_values, csv_writer

fasttext_mappings = get_fasttext_mappings()


def get_predictions():
    predictions = dict()
    statistic_dict = dict()
    remaining_file_paths, categorised_file_paths = get_remaining_and_categorised_file_paths()
    print(f'{len(remaining_file_paths)} {len(categorised_file_paths)}')
    model = fasttext.load_model('C:\\Files\\Projects\\jupyter\\models\\2023062216294307.bin')
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
                if category in statistic_dict:
                    statistic_dict[category] = statistic_dict[category] + 1
                else:
                    statistic_dict[category] = 1
    max_length = 0
    for category in statistic_dict:
        category = fasttext_mappings[category]
        if len(category) > max_length:
            max_length = len(category)
    for category in sort_by_descending_values(statistic_dict):
        category_name = fasttext_mappings[category].ljust(max_length)
        print(f'{category_name}  {statistic_dict[category]}')
    # print()
    return predictions

if __name__ == '__main__':
    predictions = get_predictions()
    directory_path = 'C:\Files\Projects\jupyter\samples\\'
    for file_path in predictions:
        file_name = file_path.split('\\')[-1]
        file_predictions = predictions[file_path]
        file_csv_writer = csv_writer(f'{directory_path}{file_name}', mode='w')
        for header, paragraph, categories in file_predictions:
            categories = ','.join(list(map(lambda x: fasttext_mappings[x], categories[0])))
            file_csv_writer.writerow([f'{header}', f'{paragraph}', f'{categories}'])



    # prediction_samples = random.sample(predictions, 100)
    # for prediction in prediction_samples:
    #     print(prediction)



    # max_length = 0
    # for file_path, _ in samples:
    #     if len(file_path) > max_length:
    #         max_length = len(file_path)
    # file_path = 'FILE_PATH'.ljust(max_length)
    # print(f'{file_path}  CATEGORIES')
    # for file_path, categories in samples:
    #     file_path = file_path.ljust(max_length)
    #     categories = ','.join(map(lambda category: fasttext_mappings[category], categories))
    #     print(f'{file_path}  {categories}')



