import time

from utils import csv_reader, csv_writer, get_json, prepare_csv_file, read_csv_file, append_csv

if __name__ == '__main__':
    repo_csv_file_path = 'C:\\Files\\Projects\\unimelb-research-project\\repo.csv'
    repo_csv_writer = csv_writer(repo_csv_file_path)
    repo_csv_reader = csv_reader(repo_csv_file_path)
    mapping_csv_file_path = 'C:\\Files\\Projects\\unimelb-research-project\\mapping.csv'
    mapping_csv_writer = csv_writer(mapping_csv_file_path)
    mapping_csv_reader = csv_reader(mapping_csv_file_path)
    prepare_csv_file(repo_csv_reader, repo_csv_writer, ['repo'])
    prepare_csv_file(mapping_csv_reader, mapping_csv_writer, ['repo', 'url'])
    q = 'filename:SECURITY.md+language:Markdown'
    per_page = 100
    page = 3
    token = ''
    file_name = 'security.md'
    time_limit = 60 + 3
    repo_csv_rows = read_csv_file(repo_csv_reader)
    mapping_csv_rows = read_csv_file(mapping_csv_reader)
    while True:
        codes = get_json(f'https://api.github.com/search/code?q={q}&per_page={per_page}&page={page}', token=token)
        if codes is not None:
            for code in codes['items']:
                repo = code['repository']['full_name']
                append_csv([repo], repo_csv_rows, repo_csv_writer)
                if file_name in code['name'].lower():
                    append_csv([repo, code['html_url']], mapping_csv_rows, mapping_csv_writer)
            page = page + 1
        print('done')
        time.sleep(time_limit)
