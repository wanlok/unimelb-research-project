import os
import sys
from datetime import datetime
from os.path import exists

import requests
from bs4 import BeautifulSoup
from dateutil import parser

import nvdcve
import security_md
from security_md import get_non_empty_file_names
from utils import csv_writer, csv_reader, prepare_csv_file, get_secret, get_start_and_end_date_string

graphql = 'https://api.github.com/graphql'

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



def get_separated_issue_count(repo, date):
    start = '1970-01-01'
    json = {'query': f'query {{s1: search(query:"repo:{repo} is:issue created:{start}..{date}",type:ISSUE) {{issueCount}}, s2: search(query:"repo:{repo} is:issue is:open created:{start}..{date}",type:ISSUE) {{issueCount}}, s3: search(query:"repo:{repo} is:issue is:closed created:{start}..{date}",type:ISSUE) {{issueCount}}}}'}
    # json = {'query': f'{content}query {{repository(owner: \"{owner}\", name: \"{repo}\") {{...content}}}}'}
    json = requests.post('https://api.github.com/graphql', json=json, headers=headers).json()
    return int(json['data']['s1']['issueCount']), int(json['data']['s2']['issueCount']), int(json['data']['s3']['issueCount'])




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
                            oid
                            committedDate
                            message
                            author {
                                email
                            }
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
                target['sha'] = commit['oid']
                target['date_time'] = commit['committedDate']
                target['message'] = commit['message']
                target['email'] = commit['author']['email']
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
    # print(query)
    json = requests.post('https://api.github.com/graphql', json={'query': query}, headers=headers).json()
    commit_count = 0
    if 'errors' not in json:
        commit_count = int(json['data']['repository']['defaultBranchRef']['target']['history']['totalCount'])
    return commit_count


def get_monthly_commit_statistics(repo, start_date=None, end_date=None):
    commit_dict = dict()
    directory_path = '.\\data\\commits\\'
    file_name = '_'.join(repo.split('/'))
    if start_date is not None and end_date is not None:
        start_date = datetime.strptime(start_date, '%Y%m%d')
        end_date = datetime.strptime(end_date, '%Y%m%d')
        end_date = datetime(end_date.year, end_date.month, end_date.day, 23, 59, 59, 999999)
        for year in range(start_date.year, end_date.year + 1):
            if year == end_date.year:
                end_month = end_date.month
            else:
                end_month = 12
            for month in range(1, end_month + 1):
                file_path = f'{directory_path}{year}\\{month}\\{file_name}.csv'
                if exists(file_path):
                    number_of_commits = -1
                    for _ in csv_reader(file_path):
                        number_of_commits = number_of_commits + 1
                    month = '{:02d}'.format(month)
                    commit_dict[f'{year}{month}'] = number_of_commits
    return commit_dict


def get_issue_count_rows(repo, start_date, end_date):
    rows = []
    start_date = int(f'{start_date}'[:6])
    end_date = int(f'{end_date}'[:6])
    directory_path = f'.\\data\\issues\\'
    for file_name in os.listdir(directory_path):
        for row in csv_reader(f'{directory_path}{file_name}'):
            if row[0] == repo and start_date <= int(row[1]) <= end_date:
                rows.append(row)
    return rows


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

ccc = '''
query{
    parent:repository(owner:"{1}",name:".github"){
        defaultBranchRef{
            target {
                ... on Commit {
                    history(path: "SECURITY.md") {
                        totalCount
                    },
                }
            }
        }
    }
    repo:repository(owner:"{2}",name:"{3}"){
        defaultBranchRef{
            security:target {
                ... on Commit {
                    root:history(path: "SECURITY.md") {
                        totalCount
                    },
                    github:history(path: ".github/SECURITY.md") {
                        totalCount
                    },
                    docs:history(path: "docs/SECURITY.md") {
                        totalCount
                    }
                }
            },
            commit:target{
                ...on Commit{
                    history(first:1){
                        totalCount
                    }
                }
            }  
        },
        languages(first: 100) {
            edges {
                node {
                    name
                }
            }
        }
    }
}
'''


def case_selection(after=None):
    repo_dict = dict()
    prefix = 'https://github.com/'
    for row in nvdcve.get_list():
        for url in eval(row[7]):
            if prefix in url:
                slices = url.replace(prefix, '').split('/')
                if slices[0] != 'advisories':
                    if len(slices) > 1:
                        key = f'{slices[0]}/{slices[1]}'
                        if key not in repo_dict:
                            repo_dict[key] = 1
    print(len(repo_dict))
    started = False
    for repo in repo_dict.keys():
        if started:
            slices = repo.split('/')
            owner = slices[0]
            name = slices[1]
            ddd = ccc
            ddd = ddd.replace('{1}', owner)
            ddd = ddd.replace('{2}', owner)
            ddd = ddd.replace('{3}', name)
            json = requests.post('https://api.github.com/graphql', json={'query': ddd}, headers=headers).json()
            data = json['data']
            parent_data = data['parent']
            if parent_data is None or parent_data['defaultBranchRef'] is None:
                parent_count = 0
            else:
                parent_count = int(data['parent']['defaultBranchRef']['target']['history']['totalCount'])
            repo_data = data['repo']
            if repo_data is None or repo_data['defaultBranchRef'] is None:
                print(f'{repo},{parent_count},0,[]')
            else:
                repo_default = repo_data['defaultBranchRef']
                root_count = int(repo_default['security']['root']['totalCount'])
                github_count = int(repo_default['security']['github']['totalCount'])
                docs_count = int(repo_default['security']['docs']['totalCount'])
                security_md_count = parent_count + root_count + github_count + docs_count
                commit_count = int(repo_default['commit']['history']['totalCount'])
                languages = list(map(lambda x: x['node']['name'], repo_data['languages']['edges']))
                print(f'{repo},{security_md_count},{commit_count},{languages}')
        if after is None or len(after) == 0 or repo == after:
            started = True



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
                        print(f'{year}{month} {file_path_2}')
                        rows = []
                        for commit_message in get_commit_messages(repo, start_date, end_date):
                            row = [commit_message['sha'], commit_message['date_time'], commit_message['message'], commit_message['email']]
                            if row not in rows:
                                index = len(rows)
                                for i in range(len(rows)):
                                    if parser.parse(row[1]) < parser.parse(rows[i][1]):
                                        index = i
                                        break
                                rows.insert(index, row)
                        writer = csv_writer(file_path_2, mode='w')
                        prepare_csv_file(csv_reader(file_path_2), writer, ['sha', 'date_time', 'message', 'email'])
                        for row in rows:
                            writer.writerow(row)


def download_yearly_issue_counts(repos, year):
    day = '{:02d}'.format(1)
    query = 'i{1}:search(query:"repo:{2} is:issue created:{3}..{4}",type:ISSUE){issueCount}'
    file_path = f'.\\data\\issues\\{year}.csv'
    writer = csv_writer(file_path, mode='w')
    prepare_csv_file(csv_reader(file_path), writer, ['repo', 'date', 'count'])
    for file_name in get_non_empty_file_names():
        for repo in repos:
            if file_name.split('.')[0] == '_'.join(repo.split('/')):
                print(repo)
                my_list = []
                for month in range(1, 13):
                    month = '{:02d}'.format(month)
                    start_date, end_date = get_start_and_end_date_string(f'{year}{month}{day}', '%Y-%m-%d')
                    q = query
                    q = q.replace('{1}', f'{year}{month}')
                    q = q.replace('{2}', repo)
                    q = q.replace('{3}', start_date)
                    q = q.replace('{4}', end_date)
                    my_list.append(q)
                q = ','.join(my_list)
                q = f'query{{{q}}}'
                print(q)
                json = requests.post('https://api.github.com/graphql', json={'query': q}, headers=headers).json()
                for key in json['data']:
                    row = [repo, key[1:], int(json['data'][key]['issueCount'])]
                    writer.writerow(row)


qqq = '''
query {
    securityAdvisories(first:100{1}) {
        nodes {
            ... on SecurityAdvisory {
                ghsaId
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
                ghsa_id = security_advisory['ghsaId']
                repo = None
                published_at = security_advisory['publishedAt']
                for url in security_advisory['references']:
                    url = url['url']
                    if 'https://github.com/advisories/' in url:
                        pass
                    elif 'https://github.com/' in url:
                        slices = url.replace('https://github.com/', '').split('/')
                        if len(slices) > 2:
                            repo = f'{slices[0]}/{slices[1]}'
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


def download_topics():
    file_path = 'topics.csv'
    writer = csv_writer(file_path, mode='w')
    reader = csv_reader(file_path)
    rows = prepare_csv_file(reader, writer, ['repo', 'topics'])
    for repo in get_list(10):
        topics = []
        slices = repo.split('/')
        owner = slices[0]
        name = slices[1]
        query = 'query{repository(owner:"{1}",name:"{2}"){repositoryTopics(first:100){edges{node{topic{name}}}}}}'
        query = query.replace('{1}', owner)
        query = query.replace('{2}', name)
        # print(query)
        json = requests.post(graphql, json={'query': query}, headers=headers).json()
        for topic in json['data']['repository']['repositoryTopics']['edges']:
            topics.append(topic['node']['topic']['name'])
        row = [repo, topics]
        if row not in rows:
            print(row)
            writer.writerow(row)


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


def is_security_md_empty(repo):
    file_name = repo.replace('/', '_')
    file_path = f'.\\data\\securities\\{file_name}.csv'
    i = 0
    for _ in csv_reader(file_path, encoding='latin-1'):
        i = i + 1
    return i <= 1


def get_list_by_keywords(keywords=None, not_keywords=None, exact_match=False):
    repos = []
    i = 0
    for row in csv_reader('topics.csv'):
        if i > 0:
            if keywords is None:
                a = True
            else:
                a = False
                for keyword in keywords:
                    keyword = keyword.lower()
                    for topic in eval(row[1]):
                        topic = topic.lower()
                        if (exact_match and keyword == topic) or (not exact_match and keyword in topic):
                            a = True
                            break
                    if a:
                        break
            if not_keywords is None:
                b = True
            else:
                b = False
                for not_keyword in not_keywords:
                    not_keyword = not_keyword.lower()
                    for topic in eval(row[1]):
                        topic = topic.lower()
                        if (exact_match and not_keyword == topic) or (not exact_match and not_keyword in topic):
                            b = True
                            break
                    if b:
                        break
                b = not b
            if a and b:
                print(row)
                repos.append(row[0])
        i = i + 1
    return repos


def search_by_categories(keywords=None, not_keywords=None, exact_match=False):
    total = 0
    with_security_md_repo_set = set()
    without_security_md_repo_set = set()
    for row in get_categories():
        if keywords is None:
            a = True
        else:
            a = False
            for keyword in keywords:
                if (exact_match and keyword.lower() == row[0].lower()) or (not exact_match and keyword.lower() in row[0].lower()):
                    a = True
                    break
        if not_keywords is None:
            b = True
        else:
            b = False
            for not_keyword in not_keywords:
                if (exact_match and not_keyword.lower() == row[0].lower()) or (not exact_match and not_keyword.lower() in row[0].lower()):
                    b = True
                    break
            b = not b
        if a and b:
            # print(f'    {row[0]}')
            total += row[1]
            with_security_md_repo_set.update(row[2])
            without_security_md_repo_set.update(row[3])
    return list(with_security_md_repo_set), list(without_security_md_repo_set)


def get_categories():
    categories = []
    for row in csv_reader('C:\\Users\\WAN Tung Lok\\Desktop\\dummy.csv'):
        category = row[0]
        my_list = eval(row[1])
        length = len(my_list)
        with_security_md_repos = []
        without_security_md_repos = []
        for a in my_list:
            repo, empty = a
            if empty:
                without_security_md_repos.append(repo)
            else:
                with_security_md_repos.append(repo)
        row = [category, length, with_security_md_repos, without_security_md_repos]
        index = len(categories)
        for i in range(index):
            if length > categories[i][1]:
                index = i
                break
        categories.insert(index, row)
    return categories


def my_dummy():
    categories = get_categories()
    # filter(categories, ['react'], ['azureactivedirectory', 'reactive', 'reactive-programming'])
    # filter(categories, ['vue'])
    # filter(categories, ['angular'])
    # filter(categories, ['spring'])
    # filter(categories, ['django'])
    with_security_md_repos, without_security_md_repos = search(categories, ['php'])
    # print(f'php {len(with_security_md_repos)} {len(without_security_md_repos)}')
    for repo in with_security_md_repos:
        print('_'.join(repo.split('/')))


    # print(security_md.get_date_statistics())


    # filter(categories, ['python'])
    # filter(categories, ['javascript'])
    # filter(categories, ['go'], ['argo', 'gorm', 'gogs', 'sogo', 'beego', 'piwigo', 'gophish', 'flashgot', 'godotengine', 'argo-workflows', 'argo-cd', 'gollum', 'django', 'spigotmc-plugins', 'mongo', 'arangodb', 'argo-tunnel', 'good-first-issue', 'algolia', 'dragonfly', 'trigonometry', 'google', 'goog', 'goa', 'goobi', 'hugo', 'duckduckgo', 'algorithm', 'nodegoat', 'agora'])
    # filter(categories, ['java'], ['javascript', 'javascipt', 'js'])
    # filter(categories, ['typescript'])
    # filter(categories, ['c'], exact_match=True)
    # filter(categories, ['ruby'])
    # filter(categories, ['shell'])
    # filter(categories, ['swift'])
    # filter(categories, ['objective-c'])
    # filter(categories, ['c#'])
    # filter(categories, ['c++'])
    # filter(categories, ['kotlin'])


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
