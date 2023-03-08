import sys
import time

from utils import csv_reader, csv_writer, prepare_csv_file, get_json, get_csv_start_index

if __name__ == '__main__':
    repo_csv_file_path = 'repo.csv'
    repo_csv_writer = csv_writer(repo_csv_file_path)
    repo_csv_reader = csv_reader(repo_csv_file_path)
    repo_csv_rows = prepare_csv_file(repo_csv_reader, repo_csv_writer, ['repo'])
    files_csv_file_path = 'files.csv'
    files_csv_writer = csv_writer(files_csv_file_path)
    files_csv_reader = csv_reader(files_csv_file_path)
    files_csv_rows = prepare_csv_file(files_csv_reader, files_csv_writer, ['repo', 'path', 'url'])
    file_names = ['security.md', 'SECURITY.md']
    per_page = 100
    time_limit = 60 + 3
    if len(sys.argv) > 1:
        start_index = 1
        end_index = len(sys.argv)
    else:
        start_index = get_csv_start_index(repo_csv_rows, files_csv_rows, 1)
        end_index = len(repo_csv_rows)
    while start_index < end_index:
        if len(sys.argv) > 1:
            repo = sys.argv[start_index]
        else:
            repo = repo_csv_rows[start_index][0]
        completed = True
        for file_name in file_names:
            codes = get_json(f'https://api.github.com/search/code?q=repo:{repo}+filename:{file_name}&per_page={per_page}')
            if codes is not None:
                for code in codes['items']:
                    row = [repo, code['path'], code['html_url']]
                    if row not in files_csv_rows:
                        files_csv_writer.writerow(row)
                        files_csv_rows.append(row)
            else:
                completed = False
                time.sleep(time_limit)
        if completed:
            start_index = start_index + 1
