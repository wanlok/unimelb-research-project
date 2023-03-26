import sys
from datetime import datetime

import requests

from utils import get_secret

content = '''
fragment Content on Repository {
    refs(first: 20, refPrefix: "refs/heads/") {
        edges {
            node {
                target {
                    ... on Commit {
                        history {
                            edges {
                                node {
                                    committedDate
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}
'''

personal_access_token = get_secret()['personal_access_token']

headers = {
    'Authorization': f'token {personal_access_token}'
}


def get_number_of_commits(repo, start_date, end_date):
    slices = repo.split('/')
    owner = slices[0]
    name = slices[1]
    start_date_time = datetime.strptime(start_date, '%Y%m%d')
    end_date_time = datetime.strptime(end_date, '%Y%m%d')
    end_date_time = datetime(end_date_time.year, end_date_time.month, end_date_time.day, 23, 59, 59, 999999)
    print(f'{start_date_time} {end_date_time}')
    json = {'query': f'{content}query{{repository(owner:\"{owner}\", name:\"{name}\"){{...Content}}}}'}
    json = requests.post('https://api.github.com/graphql', json=json, headers=headers).json()
    count = 0
    if 'errors' not in json:
        branches = json['data']['repository']['refs']['edges']
        for branch in branches:
            commits = branch['node']['target']['history']['edges']
            for commit in commits:
                date_time = datetime.strptime(commit['node']['committedDate'], '%Y-%m-%dT%H:%M:%S%z')
                if start_date_time <= date_time.replace(tzinfo=None) <= end_date_time:
                    count = count + 1
    return count


if __name__ == '__main__':
    repo = sys.argv[1]
    start_date = sys.argv[2]
    end_date = sys.argv[3]
    print(f'{get_number_of_commits(repo, start_date, end_date)}')
