import csv
import json
import random
from urllib.error import HTTPError
from urllib.request import Request, urlopen


def get_json(url_string, is_array=True):
    request = Request(url_string)
    try:
        print(f'url: {url_string}')
        response = urlopen(request)
        # response.info()["X-RateLimit-Remaining"]
        json_response = json.loads(response.read())
    except HTTPError as error:
        print(f'error: {error.reason}')
        json_response = {} if is_array else []
    return json_response


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


if __name__ == '__main__':
    # https://api.github.com/repositories?since=178709752
    # https://api.github.com/users/wanlok/repos
    # https://api.github.com/repos/wanlok/chatbot-web
    # https://api.github.com/repos/wanlok/chatbot-web/contents
    csv_file_path = 'C:\\Files\\Projects\\unimelb-research-project\\repositories.csv'
    read_file = open(csv_file_path)
    reader = csv.reader(read_file, delimiter=',')
    old_repository_names = set()
    for row in reader:
        old_repository_names.add(row[0])
    write_file = open(csv_file_path, 'a', newline='')
    writer = csv.writer(write_file)
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


