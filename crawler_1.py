import csv
import json
import random
from urllib.error import HTTPError
from urllib.request import Request, urlopen


def read_csv_file(file_path, column):
    reader = csv.reader(open(csv_file_path), delimiter=',')
    s = set()
    for row in reader:
        s.add(row[column])
    return s


def directory(name, repository_name, files, writer):
    if name in files:
        contents = get_json(f'https://api.github.com/repos/{repository_name}/contents/{name}')
        write(repository_name, list(map(lambda j: j['name'], contents)), writer, name)


def write(repository_name, files, writer, path=None):
    if len(files) > 0:
        try:
            if path is None:
                writer.writerow([repository_name, '', files])
            else:
                writer.writerow([repository_name, path, files])
        except UnicodeEncodeError as error:
            print(f'error: {error.reason}')


# https://api.github.com/repositories?since=178709752
# https://api.github.com/users/wanlok/repos
# https://api.github.com/repos/wanlok/chatbot-web
# https://api.github.com/repos/wanlok/chatbot-web/contents


if __name__ == '__main__':
    csv_file_path = 'C:\\Files\\Projects\\unimelb-research-project\\repositories.csv'
    old_repository_names = read_csv_file(csv_file_path, 0)
    writer = csv.writer(open(csv_file_path, 'a', newline=''))
    if len(old_repository_names) == 0:
        writer.writerow(['Name', 'Files'])
    since = random.randint(320000000, 330000000)
    print(f'since: {since}')
    repositories = get_json(f'https://api.github.com/repositories?since={since}')
    new_repository_names = set(map(lambda j: j['full_name'], repositories))
    repository_names = new_repository_names - old_repository_names
    print(f'new: {len(new_repository_names)}')
    print(f'old: {len(old_repository_names)}')
    print(f'new - old: {len(repository_names)}')
    for repository_name in repository_names:
        contents = get_json(f'https://api.github.com/repos/{repository_name}/contents')
        files = list(map(lambda j: j['name'], contents))
        write(repository_name, files, writer)
        directory('doc', repository_name, files, writer)
        directory('docs', repository_name, files, writer)
        directory('.github', repository_name, files, writer)