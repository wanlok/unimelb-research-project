import time

from utils import csv_reader, csv_writer, prepare_csv_file, get_json

if __name__ == '__main__':
    repo_csv_file_path = 'repo.csv'
    repo_csv_writer = csv_writer(repo_csv_file_path)
    repo_csv_reader = csv_reader(repo_csv_file_path)
    repo_csv_rows = prepare_csv_file(repo_csv_reader, repo_csv_writer, ['repo'])
    q = 'filename:SECURITY.md'
    per_page = 100
    page = 1
    size_limit = 1000
    time_limit = 60 + 3
    while page * per_page <= size_limit:
        commits = get_json(f'https://api.github.com/search/commits?q={q}&per_page={per_page}&page={page}')
        if commits is not None:
            for commit in commits['items']:
                row = [commit['repository']['full_name']]
                if row not in repo_csv_rows:
                    repo_csv_writer.writerow(row)
                    repo_csv_rows.append(row)
            page = page + 1
            time.sleep(1)
        else:
            time.sleep(time_limit)
