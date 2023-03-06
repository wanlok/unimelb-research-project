import csv
import json
from urllib.request import Request, urlopen


def get_json(url_string, token=None):
    try:
        print(f'url: {url_string}')
        request = Request(url_string)
        if token is not None:
            request.add_header('Authorization', f'token {token}')
        response = urlopen(request)
        # response.info()["X-RateLimit-Remaining"]
        json_object = json.loads(response.read())
    except Exception as e:
        print(f'error: {e.reason}')
        json_object = None
    return json_object


def get_secret():
    json.load(open('secret.json'))


def read_csv_file(reader):
    rows = []
    for row in reader:
        rows.append(row)
    return rows


def csv_reader(file_path):
    return csv.reader(open(file_path), delimiter=',')


def csv_writer(file_path):
    return csv.writer(open(file_path, 'a', newline='', encoding='utf-8'))


def prepare_csv_file(reader, writer, header):
    rows = read_csv_file(reader)
    if len(rows) == 0:
        writer.writerow(header)
    return rows


def extract(rows, index):
    for i in range(len(rows)):
        if len(rows[i]) > index:
            rows[i] = rows[i][index]
        else:
            rows[i] = None


def prepare_repo_mapping(repo_csv_reader, repo_csv_writer, mapping_csv_reader, mapping_csv_writer):
    prepare_csv_file(repo_csv_reader, repo_csv_writer, ['repo'])
    prepare_csv_file(mapping_csv_reader, mapping_csv_writer, ['repo', 'url'])
    repo_csv_rows = read_csv_file(repo_csv_reader)
    extract(repo_csv_rows, 0)
    return repo_csv_rows


def append_csv(row, rows, writer):
    if row not in rows:
        writer.writerow(row)
        rows.append(row)
