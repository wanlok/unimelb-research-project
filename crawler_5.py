import time

from utils import csv_reader, csv_writer, prepare_csv_file, get_json, get_csv_start_index

if __name__ == '__main__':
    repo_csv_file_path = 'C:\\Files\\Projects\\unimelb-research-project\\repo.csv'
    repo_csv_writer = csv_writer(repo_csv_file_path)
    repo_csv_reader = csv_reader(repo_csv_file_path)
    repo_csv_rows = prepare_csv_file(repo_csv_reader, repo_csv_writer, ['repo'])
    files_csv_file_path = 'C:\\Files\\Projects\\unimelb-research-project\\files.csv'
    files_csv_writer = csv_writer(files_csv_file_path)
    files_csv_reader = csv_reader(files_csv_file_path)
    files_csv_rows = prepare_csv_file(files_csv_reader, files_csv_writer, ['repo', 'path', 'url'])
    file_name = 'security.md'
    time_limit = 60 + 3
    start_index = get_csv_start_index(repo_csv_rows, files_csv_rows, 1)
    while start_index < len(repo_csv_rows):
        repo = repo_csv_rows[start_index][0]
        codes = get_json(f'https://api.github.com/search/code?q=repo:{repo}+filename:{file_name}')
        if codes is not None:
            for code in codes['items']:
                row = [repo, code['path'], code['html_url']]
                if row not in files_csv_rows:
                    files_csv_writer.writerow(row)
                    files_csv_rows.append(row)
            start_index = start_index + 1
        else:
            time.sleep(time_limit)
