import sys
from datetime import datetime

import requests
from Levenshtein import distance
from bs4 import BeautifulSoup
from dateutil import parser

from utils import csv_writer, csv_reader, prepare_csv_file, get_json, get_content, get_secret

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
            previous_content_dict = dict()
            for row in rows:
                repo, path, sha, date_time, content, _ = row
                key = (repo, path)
                if key in previous_content_dict:
                    previous_content = previous_content_dict[key]
                else:
                    previous_content = ''
                writer.writerow([repo, path, sha, date_time, previous_content, content, distance(previous_content, content), f'b {repos[0]} {sha}'])
                previous_content_dict[key] = content


# def download(repos, paths, file_path):
#     api_count = 0
#     rows = []
#     error = None
#     for i in range(len(repos)):
#         repo = repos[i]
#         for path in paths[i]:
#             data_1, error = get_json(f'https://api.github.com/repos/{repo}/commits?path={path}')
#             api_count = api_count + 1
#             if data_1 is not None:
#                 for j in range(len(data_1)):
#                     sha = data_1[j]['sha']
#                     data_2, error = get_json(f'https://api.github.com/repos/{repo}/commits/{sha}?path={path}')
#                     api_count = api_count + 1
#                     if data_2 is not None:
#                         date_time = parser.parse(data_2['commit']['committer']['date'])
#                         for file in data_2['files']:
#                             if file["filename"] == path:
#                                 content = get_content(file['raw_url'])
#                                 content = BeautifulSoup(eval(f'{content}').decode('utf-8'), features='lxml').get_text()
#                                 # api_count = api_count + 1
#                                 row = [repo, path, sha, date_time, content]
#                                 if row not in rows:
#                                     index = len(rows)
#                                     for k in range(len(rows)):
#                                         if date_time < rows[k][3]:
#                                             index = k
#                                             break
#                                     rows.insert(index, row)
#                     if error == rate_limit_exceeded:
#                         api_count = rate_limit
#                         break
#             if error == rate_limit_exceeded:
#                 api_count = rate_limit
#                 break
#             if len(rows) > 0:
#                 break
#         if error == rate_limit_exceeded or len(rows) > 0:
#             break
#     write(repos, rows, error, file_path)
#     return api_count


personal_access_token = get_secret()['personal_access_token']

headers = {
    'Accept': 'application/vnd.github.hawkgirl-preview+json',
    'Authorization': f'token {personal_access_token}'
}

def download(repos, paths, file_path):
    rows = []
    for i in range(len(repos)):
        repo = repos[i]
        slices = repo.split('/')
        query = 'query{repository(owner:"{1}",name:"{2}"){defaultBranchRef{target{... on Commit{history(path:"{3}"){edges{node{oid committedDate file(path:"{4}"){object{... on Blob{text}}}}}}}}}}}'
        query = query.replace('{1}', slices[0])
        query = query.replace('{2}', slices[1])
        j = 0
        for path in paths[i]:
            q = query
            q = q.replace('{3}', path)
            q = q.replace('{4}', path)
            print(q)
            json = requests.post('https://api.github.com/graphql', json={'query': q}, headers=headers).json()
            repository = json['data']['repository']
            if repository is not None:
                default_branch = repository['defaultBranchRef']
                if default_branch is not None:
                    commits = default_branch['target']['history']['edges']
                    for commit in commits:
                        commit = commit['node']
                        sha = commit['oid']
                        date_time = parser.parse(commit['committedDate'])
                        file = commit['file']
                        if file is None:
                            content = ''
                            deleted = True
                        else:
                            content = file['object']['text']
                            deleted = False
                        row = [repo, path, sha, date_time, content, deleted]
                        if row not in rows:
                            index = len(rows)
                            for k in range(len(rows)):
                                if date_time < rows[k][3]:
                                    index = k
                                    break
                            rows.insert(index, row)
            j = len(rows) - 1
            if j >= 0 and rows[j][5] is False:
                break
        if j >= 0 and rows[j][5] is False:
            break
    write([repo], rows, None, file_path)


if __name__ == '__main__':
    slices = sys.argv[2].split('/')
    directory_name = '_'.join(slices[len(slices) - 1].split('.'))
    file_name = '_'.join(sys.argv[1].split('/'))
    download([sys.argv[1]], [[sys.argv[2]]], f'data\\commits\\{directory_name}\\{file_name}.csv')
