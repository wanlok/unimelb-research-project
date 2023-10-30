import numpy as np
import pandas
from matplotlib import pyplot as plt
from numpy import float64

import nvdcve
from utils import csv_reader, repos

main_file_path = 'M:\\我的雲端硬碟\\UniMelb\\Research Project\\Open Coding\\security-related issues\\main.csv'
cve_cwe_file_path = 'M:\\我的雲端硬碟\\UniMelb\\Research Project\\Open Coding\\security-related issues\\cve_cwe.csv'

years = ['2018', '2019', '2020', '2021', '2022', '2023']
months = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']


def get_issue_dict(file_path):
    repo_dict = dict()
    for row in csv_reader(file_path):
        repo = row[0]
        if repo in repo_dict:
            repo_dict[repo].append(row)
        else:
            repo_dict[repo] = [row]
    #     year_month = row[1]
    #     year = int(year_month[:4])
    #     # month = year_month[4:]
    #     number_of_issues = int(row[2])
    #     number_of_security_issues = int(row[3])
    #     if repo in repo_dict:
    #         year_dict = repo_dict[repo]
    #         if year in year_dict:
    #             number_of_issues_in_year, number_of_security_issues_in_year = year_dict[year]
    #             year_dict[year] = (number_of_issues_in_year + number_of_issues, number_of_security_issues_in_year + number_of_security_issues)
    #         else:
    #             year_dict[year] = (number_of_issues, number_of_security_issues)
    #     else:
    #         repo_dict[repo] = dict()
    #         repo_dict[repo][year] = (number_of_issues, number_of_security_issues)

    return repo_dict


def get_issues(issues, issue_type=0):
    y = []
    for year in years:
        for month in months:
            year_month = f'{year}{month}'
            for issue in issues:
                if issue[1] == year_month:
                    if issue_type == 0:
                        y.append(int(issue[2]))
                    else:
                        y.append(int(issue[3]))
    return np.array([i + 1 for i in range(len(y))]), np.array(y)


def get_issue_slope(repo, repo_dict, issue_type=0):
    slope = None
    if repo in repo_dict:
        x, y = get_issues(repo_dict[repo], issue_type)
        if len(x) > 1 and len(y) > 1: # need two points
            A = np.vstack([x, np.ones(len(x))]).T
            y = y[:, np.newaxis]
            alpha = np.dot((np.dot(np.linalg.inv(np.dot(A.T, A)), A.T)), y)
            m = alpha[0]
            slope = m[0]
            b = alpha[1]
            print(repo)
            print(m[0])
            plt.figure(figsize=(10,8))
            plt.plot(x, y, 'b.')
            plt.plot(x, m * x + b, 'r')
            plt.xlabel('x')
            plt.ylabel('y')
            plt.show()
    return slope


# def get_cve_slope(repo, repo_dict):
#     slope = None
#     if repo in repo_dict:
#         x, y =


def get_counts(slopes):
    counts = [0, 0, 0]
    for slope in slopes:
        if type(slope) == float64:
            if slope < 0:
                counts[0] = counts[0] + 1
            elif slope > 0:
                counts[2] = counts[2] + 1
            else:
                counts[1] = counts[1] + 1
        else:
            counts[1] = counts[1] + 1
    return counts


def get_issue_trends(file_path, issue_type=0):
    # print(get_counts(repos(get_issue_slope, get_issue_dict(file_path), issue_type)))
    rows = repos(get_issue_slope, get_issue_dict(file_path), issue_type)
    # print(len(rows))
    for slope in rows:
        if type(slope) == float64:
            if slope < 0:
                print('Decrease')
            elif slope > 0:
                print('No')
            else:
                print('Increase')
        else:
            print('No')


def get_repo_cve_trend(repo):
    print(repo)

    for row in csv_reader(nvdcve.cve_cwe_path):
        if row[0] == repo:
            print(row)


if __name__ == '__main__':

    # nvdcve.write_dummy()

    # repos(get_repo_cve_trend)


    # get_cve_trends()

    # get_issue_trends(cve_cwe_file_path, 0)
    # get_issue_trends(cve_cwe_file_path, 1)
    # get_issue_trends(main_file_path, 0)
    get_issue_trends(main_file_path, 1)




