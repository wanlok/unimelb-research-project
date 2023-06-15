from functools import reduce

import pandas as pd
import statsmodels as statsmodels
from statsmodels.stats.inter_rater import fleiss_kappa

from utils import csv_reader


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


def filter_non_empties(row):
    my_list = row.strip().split(',')
    b_list = set()
    for s in my_list:
        s = s.strip()
        if len(s) > 0:
            b_list.add(s)
    return b_list


def compute_fleiss_kappa(rows, categories):
    numerator = 0
    denominator = 0
    category_dict = dict()
    for row in rows:
        subject = list(map(lambda x: filter_non_empties(x), row))
        raters = []
        for i in range(len(subject)):
            if len(subject[i]) > 0:
                raters.append(i)
        rater_count = len(raters)
        for category in categories:
            agreement = list(map(lambda x: category in x, subject))
            agreement_count = len(list(filter(lambda x: x is True, agreement)))
            key = (rater_count, agreement_count)
            if category in category_dict:
                if key in category_dict[category]:
                    category_dict[category][key] = category_dict[category][key] + 1
                else:
                    category_dict[category][key] = 1
            else:
                occurrence_dict = dict()
                occurrence_dict[key] = 1
                category_dict[category] = occurrence_dict
    max_length = 0
    for category in category_dict:
        length = len(category)
        if length > max_length:
            max_length = length
    for category in category_dict:
        p_o_numerator = 0
        p_o_denominator = 0
        p_e_numerator = 0
        p_e_denominator = 0
        for key in category_dict[category]:
            rater_count, agreement_count = key
            occurrence_count = category_dict[category][key]
            p_o_numerator = p_o_numerator + (occurrence_count * (2 * agreement_count ** 2 - 2 * rater_count * agreement_count + rater_count ** 2 - rater_count))
            p_o_denominator = p_o_denominator + (occurrence_count * (rater_count * (rater_count - 1)))
            p_e_numerator = p_e_numerator + (occurrence_count * agreement_count)
            p_e_denominator = p_e_denominator + (occurrence_count * rater_count)
        p_o = p_o_numerator / p_o_denominator
        p_e = 2 * (p_e_numerator / p_e_denominator) ** 2 - 2 * (p_e_numerator / p_e_denominator) + 1
        denominator_k = 1 - p_e
        if denominator_k > 0:
            k = (p_o - p_e) / denominator_k
        else:
            k = float('nan')
        numerator = numerator + (p_o - p_e)
        denominator = denominator + (1 - p_e)
        # print(f'{category} {p_o:.3f} {p_e:.3f} {(p_o - p_e):.3f} {denominator_k:.3f} {k:.3f}')
        print(f'{category.ljust(max_length)}  {k:.4f}')
    return numerator / denominator


def compute_pooled_cohen_kappa(a_tuple_set, b_tuple_set):
    repositories = set([tuple[0] for tuple in a_tuple_set.union(b_tuple_set)])

    #             a_agreed  a_disagreed
    # b_agreed         [0]          [1]
    # b_disgreed       [2]          [3]

    category_dict = dict()
    for repository in repositories:
        for category in categories:
            tuple = (repository, category)
            if tuple in a_tuple_set and tuple in b_tuple_set:
                matrix = [1, 0, 0, 0]
            elif tuple not in a_tuple_set and tuple in b_tuple_set:
                matrix = [0, 1, 0, 0]
            elif tuple in a_tuple_set and tuple not in b_tuple_set:
                matrix = [0, 0, 1, 0]
            else:
                matrix = [0, 0, 0, 1]
            if category in category_dict:
                category_matrix = category_dict[category]
                category_dict[category] = (
                    category_matrix[0] + matrix[0],
                    category_matrix[1] + matrix[1],
                    category_matrix[2] + matrix[2],
                    category_matrix[3] + matrix[3]
                )
            else:
                category_dict[category] = matrix

    aaa = [0, 0, 0, 0]

    observed_agreement_sum = 0
    chance_agreement_sum = 0
    number_of_categories = len(categories)
    sss = 0
    for category in category_dict:
        category_matrix = category_dict[category]
        total = sum(category_matrix)
        aaa[0] = aaa[0] + category_matrix[0]
        aaa[1] = aaa[1] + category_matrix[1]
        aaa[2] = aaa[2] + category_matrix[2]
        aaa[3] = aaa[3] + category_matrix[3]
        row_1_sum = category_matrix[0] + category_matrix[1]
        row_2_sum = category_matrix[2] + category_matrix[3]
        column_1_sum = category_matrix[0] + category_matrix[2]
        column_2_sum = category_matrix[1] + category_matrix[3]
        observed_agreement= (category_matrix[0] + category_matrix[3]) / total
        observed_agreement_sum = observed_agreement_sum + observed_agreement
        chance_agreement = row_1_sum / total * column_1_sum / total + row_2_sum / total * column_2_sum / total
        chance_agreement_sum = chance_agreement_sum + chance_agreement

        # a_agreed_b_agreed = f'{category_matrix[0]}'.rjust(8)
        # a_disagreed_b_agreed = f'{category_matrix[1]}'.rjust(11)
        # a_agreed_b_disagreed = f'{category_matrix[2]}'.rjust(8)
        # a_disagreed_b_disagreed = f'{category_matrix[3]}'.rjust(11)
        # print(f'{category}')
        # print()
        # print(f'             a_agreed  a_disagreed')
        # print(f'   b_agreed  {a_agreed_b_agreed}  {a_disagreed_b_agreed}')
        # print(f'b_disagreed  {a_agreed_b_disagreed}  {a_disagreed_b_disagreed}')
        # print()
        # print(f'OBSERVED_AGREEMENT : {observed_agreement}')
        # print(f'CHANCE_AGREEMENT   : {chance_agreement}')
        # print()
        # print()

        oa = (category_matrix[0] + category_matrix[3]) / total
        if oa < 1:
            ca = row_1_sum / total * column_1_sum / total + row_2_sum / total * column_2_sum / total
            sss = sss + (oa - ca) / (1 - ca)
        else:
            sss = sss + 1
    print(f'averaged kappa {sss/number_of_categories}')


    ttt = sum(aaa)
    r1s = aaa[0] + aaa[1]
    r2s = aaa[2] + aaa[3]
    c1s = aaa[0] + aaa[2]
    c2s = aaa[1] + aaa[3]

    # print(f'{r1s} {r2s} {c1s} {c2s}')

    oa = (aaa[0] + aaa[3]) / ttt
    ca = r1s / ttt * c1s / ttt + r2s / ttt * c2s / ttt
    # print(f'oa {oa} ca {ca}')
    print(f'matrix sum: {(oa - ca) / (1 - ca)} {aaa}')


    observed_agreement_average = observed_agreement_sum / number_of_categories
    chance_agreement_average = chance_agreement_sum / number_of_categories
    return (observed_agreement_average - chance_agreement_average) / (1 - chance_agreement_average)


def get_rater_repositories(rater_list):
    return reduce(lambda a, b: a.union(b), (map(lambda x: set(map(lambda y: y[0], x)), rater_list)))


def categorisation_by_repository():
    rows = []
    i = 0
    my_dict = dict()
    for row in csv_reader(csv_file_path, encoding='utf-8'):
        if i > 0:
            repository = row[0]
            rates = [row[3], row[5]]
            if repository in my_dict:
                for i in range(len(rates)):
                    my_dict[repository][i].append(rates[i])
            else:
                my_dict[repository] = [[] for _ in range(len(rates))]
        i = i + 1
    for repository in my_dict:
        rates = my_dict[repository]
        for i in range(len(rates)):
            rates[i] = ','.join(filter_non_empties(','.join(rates[i])))
        print(f'{repository} {rates} {list(map(lambda x: len(x), rates))}')
        rows.append(rates)
    return rows


if __name__ == '__main__':

    #               1    2    3    4    5    6    7    8    9    10   11   12   13   14   15   16   17   18   19   20
    # categories = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't']
    #
    # csv_file_path = 'C:\\Users\\WAN Tung Lok\\Desktop\\dummy.csv'
    # rows = []
    # i = 1
    # for row in csv_reader(csv_file_path, encoding='utf-8'):
    #     if i > 0:
    #         rows.append(row)
    #     i = i + 1


    csv_file_path = 'C:\\Users\\WAN Tung Lok\\Desktop\\Round 2 Combined.csv'

    categories = [
        'Introduction',
        'Threat model',
        'Scope',
        'Reporting procedure',
        'Handling procedure',
        'Secure communication',
        'Bug bounty program',
        'FAQ',
        'Known vulnerabilities',
        'Guideline',
        'Empty'
    ]

    rows = []
    i = 0
    my_dict = dict()
    for row in csv_reader(csv_file_path, encoding='utf-8'):
        if i > 0:
            # repository = row[0]
            rates = [row[3], row[5]]
            # reduce(map(lambda x: len(x), rates))
            a = len(set(map(lambda x: len(x), rates)))
            if a > 1:
                print(f'{i + 1} {rates} {a}')
            rows.append(rates)
            # if repository in my_dict:
            #     for i in range(len(rates)):
            #         my_dict[repository][i].append(rates[i])
            # else:
            #     my_dict[repository] = [[] for _ in range(len(rates))]
        i = i + 1
    print()

    # for row in rows:
    #     print(f'ROW: {row} {list(map(lambda x: len(x), row))}')

    kappa = compute_fleiss_kappa(rows, categories)
    print()
    print(kappa)


    # dr_treude_categories = get_distinct_categories(3)
    # robert_categories = get_distinct_categories(5)


    # print(dr_treude_categories)
    # print(robert_categories)




    # categories = [1]
    #
    # rater_1 = {(1, 0), (2, 0), (3, 1), (4, 1), (5, 0), (6, 1), (7, 0)}
    # rater_2 = {(1, 0), (2, 1), (3, 1), (4, 0), (5, 0), (6, 1), (7, 0)}
    # rater_3 = {(1, 0), (2, 0), (3, 1), (4, 0), (5, 0), (6, 0), (7, 1)}

    # print(f'pooled kappa: {compute_pooled_cohen_kappa(dr_treude_categories, robert_categories)}')
    # print(f'fleiss kappa: {compute_fleiss_kappa([dr_treude_categories, robert_categories])}')
    # print(f'fleiss kappa: {compute_fleiss_kappa([rater_1, rater_2, rater_3])}')

    # aaa = [
    #     [0, 3],
    #     [1, 2],
    #     [3, 0],
    #     [1, 2],
    #     [0, 3],
    #     [2, 1],
    #     [1, 2]
    # ]
    #
    # print(fleiss_kappa(aaa))
    #




