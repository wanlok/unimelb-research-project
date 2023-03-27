import sys
from datetime import datetime

from Levenshtein import distance
from bs4 import BeautifulSoup
from dateutil import parser

from utils import csv_writer, csv_reader, prepare_csv_file, get_json, get_content

header = ['repo', 'path', 'sha', 'date_time', 'previous_content', 'content', 'levenshtein_distance', 'bcompare']

rate_limit = 60
rate_limit_exceeded = 'rate limit exceeded'


def get_content_by_month(directory_path, repo):
    file_name = '_'.join(repo.split('/'))
    file_path = f'{directory_path}{file_name}.csv'
    my_dict = dict()
    for row in csv_reader(file_path):
        try:
            key = int(datetime.strptime(row[3], '%Y-%m-%d %H:%M:%S%z').strftime('%Y%m'))
            if key in my_dict:
                my_dict[key].append(row)
            else:
                my_dict[key] = [row]
        except ValueError as e:
            pass
    return my_dict


def get_content_by_day(directory_path, repo):
    file_name = '_'.join(repo.split('/'))
    file_path = f'{directory_path}{file_name}.csv'
    my_dict = dict()
    for row in csv_reader(file_path):
        try:
            key = int(datetime.strptime(row[3], '%Y-%m-%d %H:%M:%S%z').strftime('%Y%m%d'))
            if key in my_dict:
                my_dict[key].append(row)
            else:
                my_dict[key] = [row]
        except ValueError as e:
            pass
    return my_dict


def write(repos, rows, error, file_path):
    if error != rate_limit_exceeded:
        writer = csv_writer(file_path, mode='w')
        prepare_csv_file(csv_reader(file_path), writer, header)
        if len(rows) > 0:
            previous_content = ''
            for row in rows:
                repo, path, sha, date_time, content = row
                writer.writerow([repo, path, sha, date_time, previous_content, content, distance(previous_content, content), f'b {repos[0]} {sha}'])
                previous_content = content


def download(repos, paths, file_path):
    api_count = 0
    rows = []
    error = None
    for i in range(len(repos)):
        repo = repos[i]
        for path in paths[i]:
            data_1, error = get_json(f'https://api.github.com/repos/{repo}/commits?path={path}')
            api_count = api_count + 1
            if data_1 is not None:
                for j in range(len(data_1)):
                    sha = data_1[j]['sha']
                    data_2, error = get_json(f'https://api.github.com/repos/{repo}/commits/{sha}?path={path}')
                    api_count = api_count + 1
                    if data_2 is not None:
                        date_time = parser.parse(data_2['commit']['committer']['date'])
                        for file in data_2['files']:
                            if file["filename"] == path:
                                content = get_content(file['raw_url'])
                                content = BeautifulSoup(eval(f'{content}').decode('utf-8'), features='lxml').get_text()
                                # api_count = api_count + 1
                                row = [repo, path, sha, date_time, content]
                                if row not in rows:
                                    index = len(rows)
                                    for k in range(len(rows)):
                                        if date_time < rows[k][3]:
                                            index = k
                                            break
                                    rows.insert(index, row)
                    if error == rate_limit_exceeded:
                        api_count = rate_limit
                        break
            if error == rate_limit_exceeded:
                api_count = rate_limit
                break
            if len(rows) > 0:
                break
        if error == rate_limit_exceeded or len(rows) > 0:
            break
    write(repos, rows, error, file_path)
    return api_count


if __name__ == '__main__':
    slices = sys.argv[2].split('/')
    directory_name = '_'.join(slices[len(slices) - 1].split('.'))
    file_name = '_'.join(sys.argv[1].split('/'))
    download([sys.argv[1]], [[sys.argv[2]]], f'data\\commits\\{directory_name}\\{file_name}.csv')
