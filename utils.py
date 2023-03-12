import csv
import json
import operator
import sys
from urllib.request import Request, urlopen


def get_json(url_string, token=None):
    try:
        print(f'url: {url_string}')
        request = Request(url_string)
        if token is not None:
            request.add_header('Authorization', f'token {token}')
        response = urlopen(request)
        # response.info()["X-RateLimit-Remaining"]
        json_response = json.loads(response.read())
        error = None
    except Exception as e:
        print(f'error: {e.reason}')
        json_response = None
        error = e.reason
    return json_response, error


def get_content(url_string):
    request = Request(url_string)
    response = urlopen(request)
    return response.read()


def get_secret():
    return json.load(open('secret.json'))


def read_csv_file(reader):
    rows = []
    for row in reader:
        rows.append(row)
    return rows


def csv_reader(file_path, encoding='utf-8'):
    max_int = sys.maxsize
    while True:
        try:
            csv.field_size_limit(max_int)
            break
        except OverflowError:
            max_int = int(max_int / 10)
    return csv.reader(open(file_path, encoding=encoding), delimiter=',')


def csv_writer(file_path, mode='a'):
    return csv.writer(open(file_path, mode, newline='', encoding='utf-8'))


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


def get_csv_start_index(full_list, sub_list, number_of_matches):
    start_index = 0
    number_of_header_rows = 1
    for i in range(number_of_header_rows, len(full_list)):
        for j in range(number_of_header_rows, len(sub_list)):
            valid = True
            for k in range(number_of_matches):
                if full_list[i][k] != sub_list[j][k]:
                    valid = False
            if valid:
                start_index = i
    return start_index + 1


def sort_by_descending_values(input_dict):
    return dict(sorted(input_dict.items(), key=operator.itemgetter(1), reverse=True))
