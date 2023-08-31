from chart import scatter_plot
from document.document_categorisation_all import compute_number_ranges
from utils import csv_reader, attribute_file_path, repos


def get_attribute_dict():
    attribute_dict = dict()
    for row in csv_reader(attribute_file_path):
        attribute_dict[row[0]] = row
    return attribute_dict


def aaa(repo, attribute_dict):
    attributes = attribute_dict[repo]
    return [len(eval(attributes[2])), int(attributes[3])]


if __name__ == '__main__':
    attribute_dict = get_attribute_dict()
    number_of_categories, number_of_stars = zip(*repos(aaa, attribute_dict))

    # def compute_number_ranges(values, number_of_segments):
    aaa = compute_number_ranges(number_of_stars, 5)

    print(aaa)


    # def scatter_plot(x_values, y_values, title, x_title, y_title, file_path):
    scatter_plot(number_of_categories, number_of_stars, '', 'Number of Categories', 'Number of Stars', 'C:\\Files\\aaa.png')