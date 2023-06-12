from utils import csv_reader

csv_file_path = 'C:\\Users\\WAN Tung Lok\\Desktop\\Round 2.csv'

def get_distinct_categories(column_index):
    my_dict = dict()
    i = 0
    for row in csv_reader(csv_file_path, encoding='utf-8'):
        if i > 0:
            categories = list(map(lambda x: x.strip(), row[column_index].split(',')))
            for category in categories:
                key = (row[0], category)
                if key not in my_dict:
                    my_dict[key] = 1
        i = i + 1
    return set(my_dict.keys())


def get_categories_and_agreed_percentage(a_tuple_list, b_tuple_list):
    all_tuple_list = a_tuple_list.union(b_tuple_list)
    all_tuple_list = sorted(all_tuple_list, key=lambda x: x[0])
    agreed_count = 0
    categories = set()
    for key in all_tuple_list:
        categories.add(key[1])
        a_contains_key = False
        if key in a_tuple_list:
            a_contains_key = True
        b_contains_key = False
        if key in b_tuple_list:
            b_contains_key = True
        if a_contains_key and b_contains_key:
            agreed_count = agreed_count + 1
    return categories, agreed_count / len(all_tuple_list)


if __name__ == '__main__':
    dr_treude_categories = get_distinct_categories(3)
    robert_categories = get_distinct_categories(5)
    print(get_categories_and_agreed_percentage(dr_treude_categories, robert_categories))







