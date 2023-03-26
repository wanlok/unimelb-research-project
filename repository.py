import sys
from datetime import datetime

import requests

from utils import csv_writer, csv_reader, prepare_csv_file, get_secret

csv_header = ['repo', 'path', 'sha', 'date_time', 'previous_content', 'content', 'levenshtein_distance', 'bcompare']

# https://docs.gitlab.com/ee/api/dependencies.html
package_managers = [
    'bundler',
    'composer',
    'conan',
    'go',
    'gradle',
    'maven',
    'npm',
    'nuget',
    'pip',
    'pipenv',
    'yarn',
    'sbt',
    'setuptools'
]

content = '''
fragment content on Repository {
    dependencyGraphManifests {
        edges {
            node {
                blobPath
                dependencies {
                    nodes {
                        packageName
                        requirements
                        packageManager
                        repository {
                            url
                        }
                    }
                }
            }
        }
    }
}
'''


def get_list(i=None, j=None):
    repo_file_path = 'repo.csv'
    repo_writer = csv_writer(repo_file_path)
    repo_reader = csv_reader(repo_file_path)
    repo_rows = prepare_csv_file(repo_reader, repo_writer, ['repo'])
    if i is not None:
        if j is None:
            start = 1
            end = int(i)
        else:
            start = int(i)
            end = int(j)
        if start > 0:
            end = end + 1
            length = len(repo_rows)
            if end > length:
                end = length
            repo_rows = repo_rows[start:end]
        else:
            repo_rows = []
    else:
        repo_rows = repo_rows[1:]
    return list(map(lambda x: x[0], repo_rows))


personal_access_token = get_secret()['personal_access_token']

headers = {
    'Accept': 'application/vnd.github.hawkgirl-preview+json',
    'Authorization': f'token {personal_access_token}'
}


def get_dependencies(repo):
    slices = repo.split('/')
    owner = slices[0]
    repo = slices[1]
    json = {'query': f'{content}query {{repository(owner: \"{owner}\", name: \"{repo}\") {{...content}}}}'}
    json = requests.post('https://api.github.com/graphql', json=json, headers=headers).json()
    paths = set()
    dependency_dict = dict()
    if 'errors' not in json:
        files = map(lambda x: x['node'], json['data']['repository']['dependencyGraphManifests']['edges'])
        for file in files:
            path = file['blobPath']
            slices = path.split('/')
            lock_file = len(slices) > 0 and 'lock' in slices[len(slices) - 1].lower()
            if not lock_file:
                paths.add(path)
                dependencies = list(
                    filter(lambda x: x['packageManager'].lower() in package_managers, file['dependencies']['nodes']))
                if len(dependencies) > 0:
                    for dependency in dependencies:
                        name = dependency['packageName']
                        requirements = dependency['requirements']
                        package_manager = dependency['packageManager'].lower()
                        if dependency['repository'] is None:
                            repository = None
                        else:
                            repository = dependency['repository']['url']
                        if package_manager not in dependency_dict:
                            dependency_dict[package_manager] = set()
                        dependency_dict[package_manager].add((path, name, requirements, repository))
    return paths, dependency_dict


commit_message_query = '''
query {
    repository(owner: "{1}", name: "{2}") {
        defaultBranchRef {
            target {
                ... on Commit {
                    history(first: 100{3}{4}{5}) {
                        nodes {
                            committedDate
                            message
                        }
                        pageInfo {
                            endCursor
                            hasNextPage
                        }
                    }
                }
            }
        }
    }
}
'''

date_time_format = '%Y-%m-%dT%H:%M:%SZ'


def get_commit_messages(repo, start_date=None, end_date=None):
    slices = repo.split('/')
    owner = slices[0]
    name = slices[1]
    since = ''
    until = ''
    after = ''
    if start_date is not None:
        since = datetime.strptime(start_date, '%Y%m%d').strftime(date_time_format)
        since = f', since: \"{since}\"'
    if end_date is not None:
        until = datetime.strptime(end_date, '%Y%m%d')
        until = datetime(until.year, until.month, until.day, 23, 59, 59, 999999).strftime(date_time_format)
        until = f', until: \"{until}\"'
    query = commit_message_query
    query = query.replace('{1}', owner)
    query = query.replace('{2}', name)
    query = query.replace('{3}', since)
    query = query.replace('{4}', until)
    targets = []
    has_next_page = True
    while has_next_page:
        q = query.replace('{5}', after)
        json = requests.post('https://api.github.com/graphql', json={'query': q}, headers=headers).json()
        if 'errors' not in json:
            branch = json['data']['repository']['defaultBranchRef']['target']['history']
            for commit in branch['nodes']:
                target = dict()
                target['date_time'] = commit['committedDate']
                target['message'] = commit['message']
                targets.append(target)
            page_info = branch['pageInfo']
            has_next_page = bool(page_info['hasNextPage'])
            cursor = page_info['endCursor']
            after = f', after: \"{cursor}\"'
    return targets


def get_commit_count(repo, start_date=None, end_date=None):
    slices = repo.split('/')
    owner = slices[0]
    name = slices[1]
    since = ''
    until = ''
    if start_date is not None:
        since = datetime.strptime(start_date, '%Y%m%d').strftime(date_time_format)
        since = f', since: \"{since}\"'
    if end_date is not None:
        until = datetime.strptime(end_date, '%Y%m%d')
        until = datetime(until.year, until.month, until.day, 23, 59, 59, 999999).strftime(date_time_format)
        until = f', until: \"{until}\"'
    query = 'query {repository(owner: "{1}", name: "{2}") {defaultBranchRef {target {... on Commit {history(first: 1{3}{4}) {totalCount}}}}}}'
    query = query.replace('{1}', owner)
    query = query.replace('{2}', name)
    query = query.replace('{3}', since)
    query = query.replace('{4}', until)
    json = requests.post('https://api.github.com/graphql', json={'query': query}, headers=headers).json()
    commit_count = 0
    if 'errors' not in json:
        commit_count = int(json['data']['repository']['defaultBranchRef']['target']['history']['totalCount'])
    return commit_count


def get_repositories_by_owners(file_names):
    my_dict = {}
    for file_name in file_names:
        slices = file_name.split('_')
        key = slices[0]
        if key in my_dict:
            my_dict[key].append(file_name)
        else:
            my_dict[key] = [file_name]
    for key in my_dict:
        if len(my_dict[key]) > 1:
            print(f'{key} {my_dict[key]}')


if __name__ == '__main__':
    length = len(sys.argv)
    if length == 3:
        i = int(sys.argv[1])
        repos = get_list(i, sys.argv[2])
        for j in range(len(repos)):
            print(f'{i + j} {repos[j]}')
    else:
        if length == 2:
            repos = get_list(sys.argv[1])
        else:
            repos = get_list()
        for i in range(len(repos)):
            print(f'{i + 1} {repos[i]}')
