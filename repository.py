import os
import sys
from datetime import datetime

import requests
from bs4 import BeautifulSoup

from security_md import get_non_empty_file_names
from utils import csv_writer, csv_reader, prepare_csv_file, get_secret, get_start_and_end_date_string

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

date_format = '%Y-%m-%d'
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
    query = 'query{repository(owner:"{1}",name:"{2}"){defaultBranchRef{target{...on Commit{history(first:1{3}{4}){totalCount}}}}}}'
    query = query.replace('{1}', owner)
    query = query.replace('{2}', name)
    query = query.replace('{3}', since)
    query = query.replace('{4}', until)
    print(query)
    json = requests.post('https://api.github.com/graphql', json={'query': query}, headers=headers).json()
    commit_count = 0
    if 'errors' not in json:
        commit_count = int(json['data']['repository']['defaultBranchRef']['target']['history']['totalCount'])
    return commit_count


def get_issues(repo):
    slices = repo.split('/')
    owner = slices[0]
    name = slices[1]
    after = ''
    query = 'query{repository(owner:\"{1}\",name:\"{2}\"){issues(first:100,states:OPEN{3}){edges{node{createdAt title body url}}pageInfo{hasNextPage endCursor}}}}'
    query = query.replace('{1}', owner)
    query = query.replace('{2}', name)
    targets = []
    has_next_page = True
    while has_next_page:
        q = query.replace('{3}', after)
        print(q)
        json = requests.post('https://api.github.com/graphql', json={'query': q}, headers=headers).json()
        if 'errors' not in json:
            issues = json['data']['repository']['issues']
            for issue in issues['edges']:
                issue = issue['node']
                target = dict()
                target['date_time'] = issue['createdAt']
                target['title'] = issue['title']
                target['body'] = issue['body']
                target['url'] = issue['url']
                targets.append(target)
            page_info = issues['pageInfo']
            has_next_page = bool(page_info['hasNextPage'])
            cursor = page_info['endCursor']
            after = f',after:\"{cursor}\"'
    return targets


def get_issue_count(repo, start_date=None, end_date=None):
    created = ''
    if start_date is not None and end_date is not None:
        start = datetime.strptime(start_date, '%Y%m%d').strftime(date_format)
        end = datetime.strptime(end_date, '%Y%m%d').strftime(date_format)
        created = f' created:{start}..{end}'
    query = 'query {search(query:"repo:{1} is:issue{2}",type:ISSUE){issueCount}}'
    query = query.replace('{1}', repo)
    query = query.replace('{2}', created)
    print(query)
    json = requests.post('https://api.github.com/graphql', json={'query': query}, headers=headers).json()
    count = 0
    if 'errors' not in json:
        count = int(json['data']['search']['issueCount'])
    else:
        print(json)
    return count






def download_yearly_commits(year):
    day = '{:02d}'.format(1)
    file_names = get_non_empty_file_names()
    repos = get_list()
    for month in range(1, 13):
        file_path = f'.\\data\\commits\\{year}\\{month}\\'
        month = '{:02d}'.format(month)
        start_date, end_date = get_start_and_end_date_string(f'{year}{month}{day}')
        for file_name in file_names:
            for repo in repos:
                file_path_2 = f'{file_path}{file_name}'
                if file_name.split('.')[0] == '_'.join(repo.split('/')):
                    if not os.path.exists(file_path_2):
                        print(file_path_2)
                        writer = csv_writer(file_path_2, mode='w')
                        prepare_csv_file(csv_reader(file_path_2), writer, ['date_time', 'message'])
                        for commit_message in get_commit_messages(repo, start_date, end_date):
                            writer.writerow([commit_message['date_time'], commit_message['message']])


qqq = '''
query {
    securityAdvisories(first:100{1}) {
        nodes {
            ... on SecurityAdvisory {
                publishedAt
                references{
                    url
                }
            }
        }
        pageInfo {
            endCursor
            hasNextPage
        }
    }
}
'''


def download_security_advisories():
    file_path = 'security_advisory.csv'
    writer = csv_writer(file_path, mode='w')
    reader = csv_reader(file_path)
    rows = prepare_csv_file(reader, writer, ['ghsa_id', 'repo', 'date_time'])
    after = ''
    query = qqq
    has_next_page = True
    while has_next_page:
        q = query.replace('{1}', after)
        json = requests.post('https://api.github.com/graphql', json={'query': q}, headers=headers).json()
        if 'errors' not in json:
            security_advisories = json['data']['securityAdvisories']
            for security_advisory in security_advisories['nodes']:
                ghsa_id = None
                repo = None
                published_at = security_advisory['publishedAt']
                for url in security_advisory['references']:
                    url = url['url']
                    if 'https://github.com/advisories/' in url:
                        ghsa_id = url.replace('https://github.com/advisories/', '')
                    elif 'https://github.com/' in url:
                        slices = url.replace('https://github.com/', '').split('/')
                        if len(slices) > 2:
                            repo = f'{slices[0]}/{slices[1]}'
                if ghsa_id is not None:
                    if repo is None:
                        repo = ''
                    row = [ghsa_id, repo, published_at]
                    if row not in rows:
                        print(row)
                        writer.writerow(row)
            page_info = security_advisories['pageInfo']
            has_next_page = bool(page_info['hasNextPage'])
            cursor = page_info['endCursor']
            after = f',after:\"{cursor}\"'


def get_security_advisories(repo, start_date=None, end_date=None):
    rows = []
    file_path = 'security_advisory.csv'
    if start_date is not None and end_date is not None:
        start = datetime.strptime(start_date, '%Y%m%d')
        end = datetime.strptime(end_date, '%Y%m%d')
        end = datetime(end.year, end.month, end.day, 23, 59, 59, 999999)
        for row in csv_reader(file_path):
            if row[1] == repo:
                date_time = datetime.strptime(row[2], '%Y-%m-%dT%H:%M:%SZ')
                # print(f'{start} < {date_time} < {end}')
                if start < date_time < end:
                    rows.append(row)
    else:
        for row in csv_reader(file_path):
            if row[1] == repo:
                rows.append(row)
    return rows


def get_email_statistics(repo, start_date, end_date):
    slices = repo.split('/')
    owner = slices[0]
    name = slices[1]
    # file_path = 'security_advisory.csv'
    # writer = csv_writer(file_path, mode='w')
    # reader = csv_reader(file_path)
    # rows = prepare_csv_file(reader, writer, ['ghsa_id', 'repo', 'date_time'])
    after = ''
    query = 'query{repository(owner:\"{1}\",name:\"{2}\"){defaultBranchRef{target{... on Commit{history(first:100,since:\"{3}\",until:\"{4}\"{5}){edges{node{author{email}}}pageInfo{endCursor hasNextPage}}}}}}}'
    query = query.replace('{1}', owner)
    query = query.replace('{2}', name)
    query = query.replace('{3}', f'{start_date}')
    query = query.replace('{4}', f'{end_date}')
    email_dict = dict()
    domain_dict = dict()
    has_next_page = True
    while has_next_page:
        q = query.replace('{5}', after)
        print(q)
        json = requests.post('https://api.github.com/graphql', json={'query': q}, headers=headers).json()
        if 'errors' not in json:
            history = json['data']['repository']['defaultBranchRef']['target']['history']
            commits = history['edges']
            for commit in commits:
                commit = commit['node']
                email = commit['author']['email']
                if email in email_dict:
                    email_dict[email] = email_dict[email] + 1
                else:
                    email_dict[email] = 1
                domain = email[email.index('@') + 1:]
                if domain in domain_dict:
                    domain_dict[domain] = domain_dict[domain] + 1
                else:
                    domain_dict[domain] = 1
            page_info = history['pageInfo']
            has_next_page = bool(page_info['hasNextPage'])
            cursor = page_info['endCursor']
            after = f',after:\"{cursor}\"'
    return email_dict, domain_dict


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


def create_deduplicated_repo_list():
    repo_file_path = 'deduplicated_repo.csv'
    repo_writer = csv_writer(repo_file_path, mode='w')
    repo_reader = csv_reader(repo_file_path)
    prepare_csv_file(repo_reader, repo_writer, ['repo'])
    repo_list = []
    i = 0
    for repo in get_list():
        key = repo.lower()
        if key not in repo_list:
            repo_writer.writerow([repo])
            repo_list.append(key)
        else:
            i = i + 1
            print(f'{i} {repo}')


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
