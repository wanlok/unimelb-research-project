import random

from document.document_utils import get_segments, get_dataset, get_training_and_test_set, k_fold, get_directory_paths

if __name__ == '__main__':
    # print(get_directory_paths())

    print(get_dataset())

    # segments = get_segments(get_dataset())

    # dataset = pd.concat(get_df_list(directory_paths), ignore_index=True)
    # if random:
    #     dataset = dataset.sample(frac=1)
    # return dataset

    # for segment in segments:
    #     print(segment.to_string())

    # training_set, test_set = get_training_and_test_set(segments, random.randrange(k_fold))

