import math
import statistics
from itertools import groupby

import numpy as np


def get_ranks(group_1, group_2):
    ranks = []
    group = group_1 + group_2
    group.sort()
    groups = groupby(group)
    for _, group in groups:
        group = list(group)
        group_size = len(group)
        i = len(ranks) + 1
        if group_size > 1:
            j = i + len(group) - 1
            i = (i + j) / 2
        for value in group:
            ranks.append((i, value))
    return ranks


def get_group_ranks(group, values):
    ranks = []
    for i in group:
        for rank, value in values:
            if i == value:
                ranks.append(rank)
                break
    return ranks


def compute_mann_whitney_u(group_1, group_2):
    group_ranks = get_ranks(group_1, group_2)
    group_1_size = len(group_1)
    group_1_rank_sum = sum(get_group_ranks(group_1, group_ranks))
    group_1_u = group_1_rank_sum - (group_1_size * (group_1_size + 1)) / 2
    group_2_size = len(group_2)
    group_2_rank_sum = sum(get_group_ranks(group_2, group_ranks))
    group_2_u = group_2_rank_sum - (group_2_size * (group_2_size + 1)) / 2
    return group_1_u, group_2_u


def compute_mann_whitney_z(group_1, group_2, u_1, u_2):
    n_1 = len(group_1)
    n_2 = len(group_2)
    u = min(u_1, u_2)
    u_expected = n_1 * n_2 / 2
    u_standard_error = math.sqrt(n_1 * n_2 * (n_1 + n_2 + 1) / 12)
    z = (u - u_expected) / u_standard_error
    return z


def compute_mann_whitney_effect_size(group_1, group_2):
    u_1, u_2 = compute_mann_whitney_u(group_1, group_2)
    z = compute_mann_whitney_z(group_1, group_2, u_1, u_2)
    return abs(z) / math.sqrt(len(group_1) + len(group_2))


def compute_chi_square_value(counts, expected_counts, corrected):
    print('compute_chi_square_value')
    chi_square_value = 0
    for i in range(len(counts)):
        for j in range(len(counts.iloc[i])):
            count = counts.iloc[i][j]
            expected_count = expected_counts[i][j]
            if corrected:
                value = math.pow(math.fabs(count - expected_count) - 0.5, 2) / expected_count
            else:
                value = math.pow(count - expected_count, 2) / expected_count
            chi_square_value = chi_square_value + value
    print(chi_square_value)


def compute_group_sign(alpha, group_1, group_2):
    if len(group_1) > 0 and len(group_2) > 0:
        group_1_mean = statistics.mean(group_1)
        group_2_mean = statistics.mean(group_2)
        absolute_difference = abs(group_1_mean - group_2_mean)
        if group_1_mean > 0 and group_2_mean > 0:
            if absolute_difference / group_1_mean <= alpha and absolute_difference / group_2_mean <= alpha:
                sign = '='
            elif group_1_mean > group_2_mean:
                sign = '+'
            else:
                sign = '-'
        else:
            sign = ''
    else:
        sign = ''
    return sign


def compute_spearman_sign(rho):
    if rho == 0:
        sign = '='
    elif rho > 0:
        sign = '+'
    else:
        sign = '-'
    return sign


# if __name__ == '__main__':
