from utils import csv_writer, csv_reader, prepare_csv_file


def get_list(i=None, j=None):
    repo_file_path = 'repo.csv'
    repo_writer = csv_writer(repo_file_path)
    repo_reader = csv_reader(repo_file_path)
    repo_rows = prepare_csv_file(repo_reader, repo_writer, ['repo'])
    if i is not None:
        length = len(repo_rows)
        if j is None:
            start = 1
            end = i
        else:
            start = i
            end = j
        if start > 0:
            end = end + 1
            if end > length:
                end = length
            repo_rows = repo_rows[start:end]
        else:
            repo_rows = []
    return list(map(lambda x: x[0], repo_rows))