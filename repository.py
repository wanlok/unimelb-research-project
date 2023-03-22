import sys

from utils import csv_writer, csv_reader, prepare_csv_file


def get_list(i=None, j=None):
    repo_file_path = 'repo.csv'
    repo_writer = csv_writer(repo_file_path)
    repo_reader = csv_reader(repo_file_path)
    repo_rows = prepare_csv_file(repo_reader, repo_writer, ['repo'])
    if i is not None:
        if j is None:
            start = 1
            end = int(i)
        else:
            start = int(i)
            end = int(j)
        if start > 0:
            end = end + 1
            length = len(repo_rows)
            if end > length:
                end = length
            repo_rows = repo_rows[start:end]
        else:
            repo_rows = []
    return list(map(lambda x: x[0], repo_rows))


if __name__ == '__main__':
    length = len(sys.argv)
    if length == 3:
        i = int(sys.argv[1])
        repos = get_list(i, sys.argv[2])
        for j in range(len(repos)):
            print(f'{i + j} {repos[j]}')
    else:
        if length == 2:
            repos = get_list(sys.argv[1])
        else:
            repos = get_list()
        for i in range(len(repos)):
            print(f'{i + 1} {repos[i]}')
