import csv
import json
from urllib.request import Request, urlopen


def get_json(url_string):
    try:
        print(f'url: {url_string}')
        response = urlopen(Request(url_string))
        # response.info()["X-RateLimit-Remaining"]
        json_object = json.loads(response.read())
    except Exception as e:
        print(f'error: {e.reason}')
        json_object = None
    return json_object


def read_csv_file(file_path):
    rows = []
    for row in csv_reader(file_path):
        rows.append(row)
    return rows


def csv_reader(file_path):
    return csv.reader(open(file_path), delimiter=',')


def csv_writer(file_path):
    return csv.writer(open(file_path, 'a', newline=''))


def extract(rows, index):
    for i in range(len(rows)):
        if len(rows[i]) > index:
            rows[i] = rows[i][index]
        else:
            rows[i] = None
