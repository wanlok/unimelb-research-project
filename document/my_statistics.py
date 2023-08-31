import math

import numpy as np


def compute_mann_whitney_u(group1, group2):
    n1 = len(group1)
    n2 = len(group2)
    total_rank = np.concatenate([group1, group2]).argsort()
    rank_group1 = np.array([r for r, idx in enumerate(total_rank) if idx < n1])
    U1 = n1 * n2 + (n1 * (n1 + 1)) / 2 - rank_group1.sum()
    U2 = n1 * n2 - U1
    return U1, U2


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


# if __name__ == '__main__':
