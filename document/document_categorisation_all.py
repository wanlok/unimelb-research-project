import random

import fasttext

from document.document_sampling import get_remaining_and_categorised_file_paths, get_latest_content
from document.document_utils import dummy123, get_fasttext_mappings
from utils import sort_by_descending_values

if __name__ == '__main__':
    remaining_file_paths, categorised_file_paths = get_remaining_and_categorised_file_paths()
    print(f'{len(remaining_file_paths)} {len(categorised_file_paths)}')

    model = fasttext.load_model('C:\\Files\\Projects\\jupyter\\models\\2023061514051507.bin')

    my_dict = dict()

    data = []

    fasttext_mappings = get_fasttext_mappings()

    for file_path in remaining_file_paths:
        headers, paragraphs = dummy123(get_latest_content(file_path))
        header_length = len(headers)
        paragraph_length = len(paragraphs)
        if header_length == paragraph_length and header_length > 0:
            categories = set()
            for i in range(len(headers)):
                prediction = model.predict(f'{headers[i]} {paragraphs[i]}', k=-1, threshold=0.2)
                for category in prediction[0]:
                    categories.add(category)
            data.append((file_path, categories))
            for category in categories:
                if category in my_dict:
                    my_dict[category] = my_dict[category] + 1
                else:
                    my_dict[category] = 1
    max_length = 0
    for category in my_dict:
        category = fasttext_mappings[category]
        if len(category) > max_length:
            max_length = len(category)
    for category in sort_by_descending_values(my_dict):
        aaa = fasttext_mappings[category].ljust(max_length)
        print(f'{aaa}  {my_dict[category]}')
    print()
    samples = random.sample(data, 10)
    max_length = 0
    for file_path, _ in samples:
        if len(file_path) > max_length:
            max_length = len(file_path)
    file_path = 'FILE_PATH'.ljust(max_length)
    print(f'{file_path}  CATEGORIES')
    for file_path, categories in samples:
        file_path = file_path.ljust(max_length)
        categories = ','.join(map(lambda category: fasttext_mappings[category], categories))
        print(f'{file_path}  {categories}')



