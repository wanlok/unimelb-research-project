import random

from document.document_utils import get_segments, get_dataset, get_training_and_test_set, k_fold


if __name__ == '__main__':
    segments = get_segments(get_dataset())
    training_set, test_set = get_training_and_test_set(segments, random.randrange(k_fold))

