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
    # file_names = ['security.md', 'SECURITY.md']
    file_names = ['security.md']
    per_page = 100
    time_limit = 60 + 3
    get_count = 0
    if len(sys.argv) > 1:
        repo_start_index = 1
        repo_end_index = len(sys.argv)
    else:
        repo_start_index = get_csv_start_index(repo_csv_rows, files_csv_rows, 1)
        repo_end_index = len(repo_csv_rows)
    while repo_start_index < repo_end_index:
        print(f'{repo_start_index} {repo_end_index}')
        if len(sys.argv) > 1:
            repo = sys.argv[repo_start_index]
        else:
            repo = repo_csv_rows[repo_start_index][0]
        file_index = 0
        while file_index < len(file_names):
            if get_count < 10:
                codes, error = get_json(f'https://api.github.com/search/code?q=repo:{repo}+filename:{file_names[file_index]}&per_page={per_page}')
                get_count = get_count + 1
                if codes is not None:
                    for code in codes['items']:
                        path = code['path'].lower()
                        if path == 'security.md' or path == '.github/security.md' or path == 'docs/security.md':
                            row = [repo, code['path'], code['html_url']]
                            if row not in files_csv_rows:
                                files_csv_writer.writerow(row)
                                files_csv_rows.append(row)
                    file_index = file_index + 1
                elif error == 'Unprocessable Entity':
                    file_index = file_index + 1
                else:
                    time.sleep(time_limit)
                    get_count = 0
            else:
                time.sleep(time_limit)
                get_count = 0
        repo_start_index = repo_start_index + 1
