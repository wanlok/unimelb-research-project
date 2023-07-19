import os
import shutil
import sys

from Levenshtein import distance

from document.document_categorisation_all import compute_data_frames
from document.document_utils import write_content_to_file_path, get_docx_content
from dummy import get_number_of_words_headers_paragraphs, get_project_dict
from utils import repos, get_latest_content


def a(vertical, horizontal, number_ranges):
    if type(horizontal) == int:
        compute_data_frames((vertical, None, None, None, None, number_ranges), [horizontal])
    else:
        compute_data_frames((vertical, None, None, None, None, number_ranges), [(horizontal[0], None, horizontal[1])])


def nr(numbers):
    number_ranges = []
    numbers.sort()
    number_length = len(numbers)
    end = None
    for i in range(number_length):
        if i == 0:
            start = 0
            end = numbers[i]
        else:
            start = numbers[i - 1] + 1
            end = numbers[i]
        if start == end:
            number_ranges.append((start, end, f'{start}'))
        else:
            number_ranges.append((start, end, f'{start} - {end}'))
    if end is not None:
        start = end + 1
        end = sys.maxsize
        number_ranges.append((start, end, f'{start} or above'))
    return number_ranges


# def group_contents(contents, groups=[]):
#     content_length = len(contents)
#     if content_length > 0:
#         content_results = [0] * content_length
#         for i in range(content_length):
#             content_results[i] = distance(contents[0][1], contents[i][1])
#         matched_contents = []
#         remaining_contents = []
#         for i in range(content_length):
#             if content_results[i] == 0:
#                 matched_contents.append(contents[i])
#             elif content_results[i] > 0:
#                 remaining_contents.append(contents[i])
#         groups.append(matched_contents)
#         return group_contents(remaining_contents, groups)
#     else:
#         return groups










def ddd():
    # repos(get_content, my_dict, 0, directory_path)





    #
    #
        #     user_set = set()
        #     for repo in aaa:
        #         user_set.add(repo.split('/')[0])
        #     if len(user_set) > 1:
        #         print(f'{len(aaa)} {aaa}')
    # print(total)


    # a_dict = dict()
    # for key in my_dict:
    #     # if key == 'microsoft':
    #         # content_results = []
    #         # base_content = None
    #         # print(my_dict[key])
    #     group_contents_2(my_dict, key, a_dict)
    #
    # for content in a_dict:
    #     user_set = set()
    #     for t in a_dict[content]:
    #         user_set.add(t[0])
    #     if len(user_set) > 1:
    #         print(a_dict[content])

                # print('AAAAAAAAAA')
                # print(list(map(lambda x: x[1], t))[0])
            # for group in group_contents(my_dict[key]):

            #     if len(group) > 0:
                    # if base_content is None:
                    #     base_content = group[0]
                    # d = distance(base_content[1], group[0][1])
                    # print(f'AAAAA {d}')
                    # print(base_content[1])
                    # print('BBBBB')
                    # print(group[0][1])
                    # content_results.append(d)
                # repo_list = list(map(lambda x: x[0], group))
                # print(f'{len(group)}')
            # print(content_results)


if __name__ == '__main__':
    # programming_languages = list(package_manager_languages) + ['ASP.NET', 'Classic ASP', 'F#', 'Visual Basic .NET', 'Visual Basic 6.0']

    # c(3, 2, nr([5000, 10000, 50000, 100000])) # Number of stars / Categories
    # c(29, 2, nr([1000, 2000, 3000, 4000, 5000, 6000, 7000, 8000, 9000])) # Number of forks / Categories
    # c(30, 2, nr([200, 400, 600, 800, 1000, 1200, 1400, 1600, 1800, 2000])) # Number of words / Categories
    # c(31, 2, nr([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10])) # Number of headers / Categories
    # c(32, 2, nr([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10])) # Number of paragraphs / Categories
    # c(13, 2, nr([10, 20, 30, 40, 50, 60, 70, 80, 90, 100])) # Number of committers 2022 / Categories
    # c(13, 2, nr([5, 10, 20, 30, 40, 90]))  # Number of committers 2022 / Categories

    # a(3, (2, True), nr([5000, 10000, 50000, 100000])) # Number of stars / Categories
    # a(29, (2, True), nr([1000, 2000, 3000, 4000, 5000, 6000, 7000, 8000, 9000])) # Number of forks / Categories
    # a(30, (2, True), nr([200, 400, 600, 800, 1000, 1200, 1400, 1600, 1800, 2000])) # Number of words / Categories
    # a(31, (2, True), nr([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10])) # Number of headers / Categories
    # a(32, (2, True), nr([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10])) # Number of paragraphs / Categories
    # a(13, (2, True), nr([10, 20, 30, 40, 50, 60, 70, 80, 90, 100])) # Number of committers 2022 / Categories
    # a(13, (2, True), nr([5, 10, 20, 30, 40, 90]))  # Number of committers 2022 / Categories

    ddd()
