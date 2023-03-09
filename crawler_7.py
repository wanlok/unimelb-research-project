import time

from utils import get_secret, csv_reader, csv_writer, prepare_csv_file, get_json

if __name__ == '__main__':
    secret = get_secret()
    files_csv_file_path = 'files.csv'
    files_csv_writer = csv_writer(files_csv_file_path)
    files_csv_reader = csv_reader(files_csv_file_path)
    files_csv_rows = prepare_csv_file(files_csv_reader, files_csv_writer, ['repo', 'path', 'url'])
    q = 'security+in:path+language:markdown'
    per_page = 100
    page = 1
    size_limit = 1000
    time_limit = 60 + 3
    first = True
    while True:
        while page * per_page <= size_limit:
            if not first:
                time.sleep(time_limit)
            first = False
            codes = get_json(f'https://api.github.com/search/code?q={q}&per_page={per_page}&page={page}', token=secret['personal_access_token'])
            if codes is not None:
                for code in codes['items']:
                    row = [code['repository']['full_name'], code['path'], code['html_url']]
                    if row not in files_csv_rows:
                        files_csv_writer.writerow(row)
                        files_csv_rows.append(row)
                page = page + 1