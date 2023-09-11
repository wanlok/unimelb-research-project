import csv
import json
import operator
import os
import sys
import types
from datetime import datetime, timedelta
from urllib.request import Request, urlopen

from dateutil.relativedelta import relativedelta

attribute_file_path = 'C:\\Users\\WAN Tung Lok\\Desktop\\Attributes.csv'
dependency_file_path = 'C:\\Files\\Dependencies.csv'


def get_file_json(file_path):
    try:
        file = open(file_path, encoding='utf-8')
        data = json.load(file)
    except Exception:
        data = None
    return data


def get_json(url_string, token=None):
    try:
        print(f'url: {url_string}')
        request = Request(url_string)
        if token is not None:
            request.add_header('Authorization', f'token {token}')
        response = urlopen(request)
        # response.info()["X-RateLimit-Remaining"]
        data = json.loads(response.read())
        error = None
    except Exception as e:
        print(f'error: {e.reason}')
        data = None
        error = e.reason
    return data, error


def get_content(url_string):
    print(f'url: {url_string}')
    request = Request(url_string)
    response = urlopen(request)
    return response.read()


def get_secret():
    path = 'C:\\Files\\Projects\\unimelb-research-project\\'
    return json.load(open(f'{path}secret.json'))


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


def sort_by_ascending_keys(input_dict):
    return dict(sorted(input_dict.items()))


def sort_by_descending_keys(input_dict):
    return dict(sorted(input_dict.items(), reverse=True))


def sort_by_descending_values(input_dict):
    return dict(sorted(input_dict.items(), key=operator.itemgetter(1), reverse=True))


def get_writer(file_path):
    try:
        file = open(file_path, mode='w', encoding='utf-8')
    except Exception:
        file = None
    return file


def get_start_and_end_date_string(date_string, output_format='%Y%m%d'):
    date = datetime.strptime(date_string, '%Y%m%d')
    year = date.year
    month = date.month
    month_string = '{:02d}'.format(month)
    start_date = datetime.strptime(f'{year}{month_string}01', '%Y%m%d').strftime(output_format)
    if month == 12:
        year = year + 1
        month = 1
    else:
        month = month + 1
    month_string = '{:02d}'.format(month)
    end_date = (datetime.strptime(f'{year}{month_string}01', '%Y%m%d') - timedelta(days=1)).strftime(output_format)
    return start_date, end_date


def get_start_and_end_date_string_before_date_minus_days(date, days, format):
    date = datetime(date.year, date.month, date.day, 0, 0, 0, 0)
    end_date = date - relativedelta(days=1)
    start_date = date - relativedelta(days=days)
    start_date = start_date.strftime(format)
    end_date = end_date.strftime(format)
    return start_date, end_date


def contain_string(string, string_list, ignore_case=False):
    contain = False
    for s in string_list:
        if ignore_case and s.lower() in string.lower():
            print(f'{s.lower()} {string.lower()}')
            contain = True
            break
        elif s in string:
            contain = True
            break
    return contain


def expand(aaa):
    bbb = []
    previous = None
    for i in range(len(aaa)):
        if len(aaa[i]) == 0:
            bbb.append(previous)
        else:
            bbb.append(aaa[i])
            previous = aaa[i]
    return bbb


def repos(*params):
    my_list = []
    if len(params) > 0 and type(params[0]) is types.FunctionType:
        function = params[0]
        params = list(params[1:])
        for file_name in os.listdir('C:\\Files\\security policies\\'):
            repo = file_name.replace('.csv', '').replace('_', '/', 1)
            my_list.append(function(*tuple([repo] + params)))
    return my_list


def repo_2(*params):
    my_list = []
    if len(params) > 0 and type(params[0]) is types.FunctionType:
        function = params[0]
        params = list(params[1:])
        _, repo_list = get_column_title_and_values(0)
        for repo in repo_list:
            my_list.append(function(*tuple([repo] + params)))
    return my_list


def random_repo(*params):
    data = None
    if len(params) > 0 and type(params[0]) is types.FunctionType:
        function = params[0]
        params = list(params[1:])

        for file_name in os.listdir('C:\\Files\\security policies\\'):
            repo = file_name.replace('.csv', '').replace('_', '/', 1)
            # dafunction(*tuple([repo] + params)))
    # return my_list



def get_file_path(repo):
    file_name = repo.replace('/', '_')
    return f'C:\\Files\\security policies\\{file_name}.csv'


def get_repo_and_path(file_path):
    repo = None
    path = None
    target_row = None
    i = 0
    for row in csv_reader(f'{file_path}'):
        if i > 0:
            target_row = row
        i = i + 1
    if target_row is not None:
        repo = target_row[0]
        path = target_row[1]
    return repo, path


def get_latest_content(file_path):
    content = None
    target_row = None
    i = 0
    for row in csv_reader(f'{file_path}'):
        if i > 0:
            target_row = row
        i = i + 1
    if target_row is not None:
        content = target_row[5]
    return content


def get_security_policy_repo(repo):
    directory_path = 'C:\\Files\\security policies\\'
    file_name = repo.replace('/', '_')
    file_name = f'{file_name}.csv'
    security_policy_repo, _ = get_repo_and_path(f'{directory_path}{file_name}')
    security_policy_repo = security_policy_repo.lower()
    return security_policy_repo


def is_contain_alphanumeric(word):
    contain_alphanumeric = False
    for character in word:
        if f'{character}'.isalnum():
            contain_alphanumeric = True
            break
    return contain_alphanumeric


def get_column_title_and_values(column_index, as_list=False, as_list_count=False):
    title = ''
    sub_title = ''
    values = []
    i = 0
    for row in csv_reader(attribute_file_path):
        if i == 0:
            title = expand(row)[column_index]
        elif i == 1:
            sub_title = row[column_index]
        else:
            if as_list:
                try:
                    value = eval(row[column_index])
                    if as_list_count:
                        value = f'{len(value)}'
                except:
                    value = None
            else:
                value = row[column_index]
                # v = row[column_index]
                # if type(v) == str:
                #     value = v
                # else:
                #     value = int(v) if len(v) > 0 else v
            values.append(value)
        i = i + 1
    return f'{title} {sub_title}'.strip(), values


def is_float(num):
    try:
        float(num)
        return True
    except ValueError:
        return False


def is_int(num):
    try:
        int(num)
        return True
    except ValueError:
        return False


def combine_values(my_list, as_list, as_list_count):
    value = None
    if as_list:
        for x in my_list:
            if x is not None:
                if value is None:
                    value = set()
                value.update(x)
        if value is not None:
            if as_list_count:
                value = f'{len(value)}'
            else:
                value = list(value)
    else:
        for x in my_list:
            if is_float(x):
                if value is None:
                    value = 0.0
                value = value + float(x)
            elif is_int(x):
                if value is None:
                    value = 0
                value = value + int(x)
        if value is not None:
            value = f'{value}'
    return value


def get_grouped_column_title_and_values(column_index, as_list=False, as_list_count=False):
    x_values = []
    y_values = []
    keys = repos(get_security_policy_repo)
    y_title, values = get_column_title_and_values(column_index, as_list)
    my_dict = dict()
    for key, value in zip(keys, values):
        if key in my_dict:
            my_dict[key].append(value)
        else:
            my_dict[key] = [value]
    for key in sort_by_ascending_keys(my_dict):
        x_values.append(key)
        # y_values.append(my_dict[key])
        y_values.append(combine_values(my_dict[key], as_list, as_list_count))
    return y_title, x_values, y_values