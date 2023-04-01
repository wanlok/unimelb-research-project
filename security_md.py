import os.path
import sys
from datetime import datetime

import commit_history
import repository
from utils import csv_reader

directory_path = '.\\data\\securities\\'

lower_case_paths = [['security.md', '.github/security.md', 'docs/security.md'], ['security.md']]
upper_case_paths = [['SECURITY.md', '.github/SECURITY.md', 'docs/SECURITY.md'], ['SECURITY.md']]


def get_non_empty_file_names():
    file_names = []
    for file_name in os.listdir(directory_path):
        slices = file_name.split('.')
        if slices[len(slices) - 1] == 'csv':
            number_of_rows = 0
            for _ in csv_reader(f'{directory_path}{file_name}'):
                number_of_rows = number_of_rows + 1
                if number_of_rows > 1:
                    file_names.append(file_name)
                    break
    return file_names


def security_md_changed_file_names():
    my_dict = dict()
    for file_name in os.listdir(directory_path):
        slices = file_name.split('.')
        if slices[len(slices) - 1] == 'csv':
            i = 0
            for row in csv_reader(f'{directory_path}{file_name}', encoding='latin-1'):
                if i > 0:
                    if file_name in my_dict:
                        my_dict[file_name].add(row[0])
                    else:
                        my_set = set()
                        my_set.add(row[0])
                        my_dict[file_name] = my_set
                i = i + 1
    for key in my_dict:
        list = my_dict[key]
        if len(list) > 1:
            print(f'{key} {my_dict[key]}')


def get_date_statistics(file_path, start_date=None, end_date=None):
    date_list = []
    date_dict = dict()
    if start_date is not None:
        start_date = int(start_date)
    if end_date is not None:
        end_date = int(end_date)
    for row in csv_reader(file_path):
        try:
            date = int(datetime.strptime(row[3], '%Y-%m-%d %H:%M:%S%z').strftime('%Y%m%d'))
            if start_date is not None and end_date is not None:
                if date < start_date or date > end_date:
                    continue
            if date in date_dict:
                date_dict[date] = date_dict[date] + 1
            else:
                date_list.append(date)
                date_dict[date] = 1
        except ValueError:
            pass
    return date_list, date_dict


def download(repo, lower_case, directory_path, replace):
    slices = repo.split('/')
    repos = [repo, f'{slices[0]}/.github']
    file_path = directory_path.replace('{}', '_'.join(slices))
    file_exists = os.path.exists(file_path)
    if replace or not file_exists:
        print(repo)
        if lower_case:
            api_count = commit_history.download(repos, lower_case_paths, file_path)
        else:
            api_count = commit_history.download(repos, upper_case_paths, file_path)
    else:
        api_count = 0
    return api_count


if __name__ == '__main__':
    if len(sys.argv) == 1 or sys.argv[1] == 'l':
        lower_case = False
        api_count = 0
        repos = repository.get_list()
        for repo in repos:
            download(repo, lower_case, f'{directory_path}{{}}.csv', False)
            # api_count = api_count + download(repo, lower_case, f'{directory_path}{{}}.csv', False)
            # if api_count >= commit_history.rate_limit:
            #     break
    elif '/' in sys.argv[1]:
        lower_case = len(sys.argv) > 2 and sys.argv[2] == 'l'
        download(sys.argv[1], lower_case, f'{directory_path}{{}}.csv', True)
