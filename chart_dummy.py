import os
from datetime import datetime

from dateutil.relativedelta import relativedelta

import chart
import nvdcve
import repository
from security_md import get_date_statistics, directory_path, get_date_statistics_2
from utils import get_start_and_end_date_string, csv_reader


def get_repositories_by_language(target_language):
    repos = set()
    for row in csv_reader('C:\\Users\\WAN Tung Lok\\Desktop\\NVD Repositories with SECURITY.md.csv'):
        exists = False
        for language in eval(row[3]):
            if language.lower() == target_language.lower():
                exists = True
                break
        if exists:
            repo = row[0]
            file_name = '_'.join(repo.split('/'))
            file_path = f'C:\\Files\\a\\{file_name}.csv'
            if os.path.exists(file_path):
                repos.add(repo)
    for row in csv_reader('C:\\Users\\WAN Tung Lok\\Desktop\\Random Repositories.csv'):
        exists = False
        for language in eval(row[3]):
            if language.lower() == target_language.lower():
                exists = True
                break
        if exists:
            repo = row[0]
            file_name = '_'.join(row[0].split('/'))
            file_path = f'C:\\Files\\a\\{file_name}.csv'
            if os.path.exists(file_path):
                repos.add(repo)
    return list(repos)



if __name__ == '__main__':
    start_date = 20210101
    end_date = 20211231
    title = 'Number of java repositories with SECURITY.md updates per day in 2023'
    file_path = f'C:\\Files\\Projects\\wanlok.github.io\\research\\charts\\2023.png'
    repos = get_repositories_by_language('java')
    # repos = repository.get_list_by_keywords(keywords=['java'], not_keywords=['javascript'])
    # repos = repository.get_list_by_keywords(keywords=['python'])
    chart.dummy(repos, start_date, end_date, title, file_path)

    # print(repos)

    # for year in range(2010, 2024):
    #     repository.download_yearly_issue_counts(repos, year)
    # issue_count = repository.get_issue_count('looly/hutool')

    # for repo in repos:
    #     for row in repository.get_issue_count_rows(repo, start_date, end_date):
    #         print(row)


    # repo = 'chatopera/cskefu'
    # # for month in range(1, 12):
    # #     month = '{:02d}'.format(month)
    # #     start_date, end_date = get_start_and_end_date_string(f'2020{month}01')
    # #     # number_of_cves = len(nvdcve.get_list(repo, start_date, end_date))
    # #     number_of_issues = repository.get_issue_count_rows(repo, start_date, end_date)[0][2]
    # #     print(f'{start_date} {end_date} {number_of_issues}')
    # print(nvdcve.get_list(repo))
    # for month in range(1, 10):
    #     month = '{:02d}'.format(month)
    #     start_date, end_date = get_start_and_end_date_string(f'2021{month}01')
    #     number = len(nvdcve.get_list(repo, start_date, end_date))
    #     # number = repository.get_issue_count_rows(repo, start_date, end_date)[0][2]
    #     print(f'{2021}{month} {number}')

    # nvdcve.get_list()


    # for repo in repos:
    #     repo_file_name = '_'.join(repo.split('/'))
    #     repo_file_path = f'{directory_path}{repo_file_name}.csv'
    #     _, date_dict = get_date_statistics_2(repo_file_path, start_date, end_date)
    #     if len(date_dict) > 0:
    #         print(f'{repo}')
    #         for date in date_dict:
    #             print(date)
    #             for bcompare in date_dict[date]:
    #                 print(bcompare)



    # year = 2022
    # for month in range(1, 13):
    #     month = '{:02d}'.format(month)
    #     start_date, end_date = get_start_and_end_date_string(f'{year}{month}01')
    #     # start_date = 20220302
    #     # end_date = 20220302
    #     # print(f'{year}{month} {get_repo_statistics(start_date, end_date)}')
    #     print(f'{year}{month} {len(get_repo_statistics(start_date, end_date))}')