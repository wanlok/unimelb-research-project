import json
import random
from urllib.error import HTTPError
from urllib.request import Request, urlopen


def get_json(url_string, is_array=True):
    request = Request(url_string)
    try:
        response = urlopen(request)
        print(f'count: {response.info()["X-RateLimit-Remaining"]}')
        json_response = json.loads(response.read())
    except HTTPError as err:
        print(f'error: {err.reason}')
        json_response = {} if is_array else []
    return json_response


if __name__ == '__main__':
    # https://api.github.com/repositories?since=178709752
    # https://api.github.com/users/wanlok/repos
    # https://api.github.com/repos/wanlok/chatbot-web
    # https://api.github.com/repos/wanlok/chatbot-web/contents
    since = random.randint(0, 100000000)
    print(f'since: {since}')
    repositories = get_json(f'https://api.github.com/repositories?since={since}')
    for repository in repositories:
        repository_name = repository['full_name']
        print(f'name: {repository_name}')
        contents = get_json(f'https://api.github.com/repos/{repository_name}/contents')
        file_names = list(map(lambda j: j['name'], contents))
        print(f'files: {file_names}')