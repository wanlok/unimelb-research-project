import os.path
import sys

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
            api_count = api_count + download(repo, lower_case, f'{directory_path}{{}}.csv', False)
            if api_count >= commit_history.rate_limit:
                break
    elif '/' in sys.argv[1]:
        lower_case = len(sys.argv) > 2 and sys.argv[2] == 'l'
        download(sys.argv[1], lower_case, f'{directory_path}{{}}.csv', True)
