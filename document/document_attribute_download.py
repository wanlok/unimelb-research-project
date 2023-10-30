import os

import requests

from document.rq3 import get_user_dict, get_relevant_repos, get_parent_github_security_policy_commit_sha
from repository import headers
from utils import csv_reader, csv_writer, repos

all_graphql = '''
query {
    repository(owner:"{1}", name:"{2}") {
        defaultBranchRef {
            target {
                ... on Commit {
                    commitCount2018: history(since: "2018-01-01T00:00:00Z", until: "2018-12-31T23:59:59Z") {
                        totalCount
                    }
                    commitCount2019: history(since: "2019-01-01T00:00:00Z", until: "2019-12-31T23:59:59Z") {
                        totalCount
                    }
                    commitCount2020: history(since: "2020-01-01T00:00:00Z", until: "2020-12-31T23:59:59Z") {
                        totalCount
                    }
                    commitCount2021: history(since: "2021-01-01T00:00:00Z", until: "2021-12-31T23:59:59Z") {
                        totalCount
                    }
                    commitCount2022: history(since: "2022-01-01T00:00:00Z", until: "2022-12-31T23:59:59Z") {
                        totalCount
                    }
                }
            }
        }
        stargazers {
            totalCount
        }
        languages(first:100) {
            edges {
                node {
                    name
                }
            }
        }
        forkCount
    }
    issueCount2018: search(query:"repo:{3} is:issue created:2018-01-01T00:00:00Z..2018-12-31T23:59:59Z", type:ISSUE) {
        issueCount
    }
    issueCount2019: search(query:"repo:{3} is:issue created:2019-01-01T00:00:00Z..2019-12-31T23:59:59Z", type:ISSUE) {
        issueCount
    }
    issueCount2020: search(query:"repo:{3} is:issue created:2020-01-01T00:00:00Z..2020-12-31T23:59:59Z", type:ISSUE) {
        issueCount
    }
    issueCount2021: search(query:"repo:{3} is:issue created:2021-01-01T00:00:00Z..2021-12-31T23:59:59Z", type:ISSUE) {
        issueCount
    }
    issueCount2022: search(query:"repo:{3} is:issue created:2022-01-01T00:00:00Z..2022-12-31T23:59:59Z", type:ISSUE) {
        issueCount
    }
    issueClosedCount2018: search(query:"repo:{3} is:issue closed:2018-01-01T00:00:00Z..2018-12-31T23:59:59Z", type:ISSUE) {
        issueCount
    }
    issueClosedCount2019: search(query:"repo:{3} is:issue closed:2019-01-01T00:00:00Z..2019-12-31T23:59:59Z", type:ISSUE) {
        issueCount
    }
    issueClosedCount2020: search(query:"repo:{3} is:issue closed:2020-01-01T00:00:00Z..2020-12-31T23:59:59Z", type:ISSUE) {
        issueCount
    }
    issueClosedCount2021: search(query:"repo:{3} is:issue closed:2021-01-01T00:00:00Z..2021-12-31T23:59:59Z", type:ISSUE) {
        issueCount
    }
    issueClosedCount2022: search(query:"repo:{3} is:issue closed:2022-01-01T00:00:00Z..2022-12-31T23:59:59Z", type:ISSUE) {
        issueCount
    }
}
'''

committer_graphql = '''
query {
    repository(owner:"{1}", name:"{2}") {
        defaultBranchRef {
            target {
                ... on Commit {
                    history(first:100, since:"{3}-01-01T00:00:00Z", until:"{3}-12-31T23:59:59Z"{AFTER}) {
                        totalCount
                        edges {
                            node {
                                author {
                                    email
                                }
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

# comments(first: 100) {
#                         edges {
#                             node {
#                                 createdAt
#                                 bodyHTML
#                             }
#                         }
#                     }

issue_graphql = '''
query {
    repository(owner: "{1}", name: "{2}") {
        issues(first: 100{AFTER}) {
            totalCount
            edges {
                node {
                    createdAt
                    state
                    title
                    bodyHTML
                }
            }
            pageInfo {
                endCursor
                hasNextPage
            }            
        }
    }
}
'''

issue_count_graphql = '''
query {
    repository(owner: "{1}", name: "{2}") {
        issues(first: 1) {
            totalCount         
        }
    }
}
'''

primary_language_graphql = '''
query {
    repository(owner: "{1}", name: "{2}") {
        primaryLanguage {
            name
        }
    }
}
'''


path_programming_language = '/data/repository/languages/edges'
path_number_of_stars = '/data/repository/stargazers/totalCount'
path_commit_count_2018 = '/data/repository/defaultBranchRef/target/commitCount2018/totalCount'
path_commit_count_2019 = '/data/repository/defaultBranchRef/target/commitCount2019/totalCount'
path_commit_count_2020 = '/data/repository/defaultBranchRef/target/commitCount2020/totalCount'
path_commit_count_2021 = '/data/repository/defaultBranchRef/target/commitCount2021/totalCount'
path_commit_count_2022 = '/data/repository/defaultBranchRef/target/commitCount2022/totalCount'
path_issue_count_2018 = '/data/issueCount2018/issueCount'
path_issue_count_2019 = '/data/issueCount2019/issueCount'
path_issue_count_2020 = '/data/issueCount2020/issueCount'
path_issue_count_2021 = '/data/issueCount2021/issueCount'
path_issue_count_2022 = '/data/issueCount2022/issueCount'
path_issue_closed_count_2018 = '/data/issueClosedCount2018/issueCount'
path_issue_closed_count_2019 = '/data/issueClosedCount2019/issueCount'
path_issue_closed_count_2020 = '/data/issueClosedCount2020/issueCount'
path_issue_closed_count_2021 = '/data/issueClosedCount2021/issueCount'
path_issue_closed_count_2022 = '/data/issueClosedCount2022/issueCount'
path_fork_count = '/data/repository/forkCount'

path_committer_list = '/data/repository/defaultBranchRef/target/history/edges'
path_committer_count = '/data/repository/defaultBranchRef/target/history/totalCount'
path_committer_next_page = '/data/repository/defaultBranchRef/target/history/pageInfo/hasNextPage'
path_committer_cursor = '/data/repository/defaultBranchRef/target/history/pageInfo/endCursor'

path_issue_list = '/data/repository/issues/edges'
path_issue_count = '/data/repository/issues/totalCount'
path_issue_next_page = '/data/repository/issues/pageInfo/hasNextPage'
path_issue_cursor = '/data/repository/issues/pageInfo/endCursor'

path_pull_request_list = '/data/repository/pullRequests/edges'
path_pull_request_count = '/data/repository/pullRequests/totalCount'
path_pull_request_next_page = '/data/repository/pullRequests/pageInfo/hasNextPage'
path_pull_request_cursor = '/data/repository/pullRequests/pageInfo/endCursor'

path_commit_list = '/data/repository/defaultBranchRef/target/history/edges'
path_commit_count = '/data/repository/defaultBranchRef/target/history/totalCount'
path_commit_next_page = '/data/repository/defaultBranchRef/target/history/pageInfo/hasNextPage'
path_commit_cursor = '/data/repository/defaultBranchRef/target/history/pageInfo/endCursor'

path_user_repo_list = '/data/organization/repositories/edges'
path_user_repo_count = '/data/organization/repositories/totalCount'
path_user_repo_next_page = '/data/organization/repositories/pageInfo/hasNextPage'
path_user_repo_cursor = '/data/organization/repositories/pageInfo/endCursor'


def post_graphql(graphql):
    try:
        return requests.post('https://api.github.com/graphql', json={'query': graphql}, headers=headers).json()
    except requests.exceptions.RequestException as e:
        print('retry')
        return post_graphql(graphql)


def parse_result_dict(all_set, current_depth, path, data, result_dict):
    current_set = set(filter(lambda x: x[0] == current_depth, all_set))
    if len(all_set) > 0:
        for _, name in current_set:
            if current_depth == 0:
                name = 'data'
            if data.__class__ is dict and name in data:
                parse_result_dict(all_set - current_set, current_depth + 1, path + '/' + name, data[name], result_dict)
            elif '...' in name:
                parse_result_dict(all_set - current_set, current_depth + 1, path, data, result_dict)
            elif data.__class__ is not dict:
                result_dict[path] = data
    else:
        result_dict[path] = data


def get_names(graphql, start_index, end_index):
    names = []
    for name in graphql[start_index:end_index].split('\n'):
        name = name.strip()
        name_length = len(name)
        if name_length > 0:
            for index in range(name_length):
                if name[index] == '(' or name[index] == ':':
                    name = name[:index]
                    break
            names.append(name)
    return names


def get_result_dict(graphql, data):
    result_dict = dict()
    name_set = set()
    graphql_length = len(graphql)
    if graphql_length > 0:
        depth = 0
        start_index = 1
        for index in range(graphql_length):
            if graphql[index] == '{':
                for name in get_names(graphql, start_index, index):
                    name_set.add((depth, name))
                depth = depth + 1
                start_index = index + 1
            elif graphql[index] == '}':
                for name in get_names(graphql, start_index, index):
                    name_set.add((depth, name))
                depth = depth - 1
                start_index = index + 1
        parse_result_dict(name_set, 0, '', data, result_dict)
    return result_dict


def get_csv_rows(csv_file_path):
    rows = []
    for row in csv_reader(csv_file_path):
        rows.append(row)
    return rows


def is_exists(repo, rows):
    exists = False
    for row in rows:
        if row[0] == repo:
            exists = True
            break
    return exists


def get_list(graphql, path_list, path_next_page, path_cursor, path_count=None, cursor=''):
    list = []
    next_page = True
    count = None
    while next_page:
        next_graphql = graphql.replace('{AFTER}', cursor)
        # print(next_graphql)
        result_dict = get_result_dict(next_graphql, post_graphql(next_graphql))
        if path_list in result_dict:
            sub_list = result_dict[path_list]
            if path_count is not None:
                if count is None:
                    count = result_dict[path_count]
                count = count - len(sub_list)
                print(f'{count}')
            list.extend(sub_list)
            next_page = result_dict[path_next_page]
            cursor = f', after:"{result_dict[path_cursor]}"'
        else:
            next_page = False
    return list, cursor


def extract(key, dict):
    if key in dict:
        value = dict[key]
    else:
        value = None
    return value


def download_attributes(repo):
    slices = repo.split('/')
    owner = slices[0]
    project = slices[1]
    # if not is_exists(repo, language_csv_file_rows) or True:
    graphql = all_graphql.replace('{1}', owner).replace('{2}', project).replace('{3}', repo)
    result_dict = get_result_dict(graphql, post_graphql(graphql))
    programming_languages = extract(path_programming_language, result_dict)
    if programming_languages is not None:
        programming_languages = list(map(lambda x: x['node']['name'], programming_languages))
    row = [
        repo,
        extract(path_number_of_stars, result_dict),
        extract(path_commit_count_2018, result_dict),
        extract(path_commit_count_2019, result_dict),
        extract(path_commit_count_2020, result_dict),
        extract(path_commit_count_2021, result_dict),
        extract(path_commit_count_2022, result_dict),
        extract(path_issue_count_2018, result_dict),
        extract(path_issue_count_2019, result_dict),
        extract(path_issue_count_2020, result_dict),
        extract(path_issue_count_2021, result_dict),
        extract(path_issue_count_2022, result_dict),
        extract(path_issue_closed_count_2018, result_dict),
        extract(path_issue_closed_count_2019, result_dict),
        extract(path_issue_closed_count_2020, result_dict),
        extract(path_issue_closed_count_2021, result_dict),
        extract(path_issue_closed_count_2022, result_dict),
        f'{programming_languages}'
    ]
    return row


count_dict = dict()

def prepare_count_dict():
    # count_dict = dict()
    for row in csv_reader('C:\\Users\\WAN Tung Lok\\Desktop\\repo_issue_counts.txt'):
        if row[1] != 'failed':
            count = int(row[1])
        else:
            count = None
        if count is not None:
            count_dict[row[0]] = count


def get_saved_issue_list(file_path):
    issues = []
    if os.path.exists(file_path):
        with open(file_path, encoding='utf-8') as f:
            lines = f.readlines()
            if len(lines) > 0:
                issues = eval(lines[0])
        f.close()
    return issues


def download_issues(repo):
    slices = repo.split('/')
    owner = slices[0]
    project = slices[1]
    graphql = issue_graphql.replace('{1}', owner).replace('{2}', project)
    directory_path = 'C:\\Files\\issues\\'
    file_name = repo.replace('/', '_')
    file_path = f'{directory_path}{file_name}.txt'
    if repo in count_dict:
        expected_number_of_issues = count_dict[repo]
        issue_list = get_saved_issue_list(file_path)
        number_of_issues = len(issue_list)
        print(f'{repo} {expected_number_of_issues} {number_of_issues}')
        if expected_number_of_issues <= 999999999 and repo not in ['kubernetes/kubernetes']:
            cursor = ''
            while len(issue_list) < expected_number_of_issues:
                print(f'{repo} {expected_number_of_issues} {number_of_issues}')
                new_issue_list, cursor = get_list(graphql, path_issue_list, path_issue_next_page, path_issue_cursor, path_issue_count, cursor)
                for new_issue in new_issue_list:
                    exists = False
                    for issue in issue_list:
                        if new_issue['node']['createdAt'] == issue['node']['createdAt']\
                                and new_issue['node']['title'] == issue['node']['title']\
                                and new_issue['node']['bodyHTML'] == issue['node']['bodyHTML']:
                            exists = True
                            break
                    if not exists:
                        issue_list.append(new_issue)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(f'{issue_list}')
                number_of_issues = len(issue_list)


def get_graphql_values(repo, graphql, paths):
    values = [None] * len(paths)
    slices = repo.split('/')
    owner = slices[0]
    project = slices[1]
    graphql = graphql.replace('{1}', owner).replace('{2}', project)
    # print(graphql)
    result_dict = get_result_dict(graphql, post_graphql(graphql))
    # print(result_dict)
    for i in range(len(paths)):
        path = paths[i]
        if path in result_dict:
            # print(f'"{repo}","{result_dict[path]}"')
            values[i] = result_dict[path]
        # else:
        #     print(f'"{repo}",""')
    return values


def get_stuff(repo, a, target):
    # if target in a:
    headers = {
        'Authorization': 'token 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'
    }
    url = f'https://api.github.com/repos/{repo}/languages'
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        print(f'"{repo}","{data}"')
    else:
        print(f'"{repo}","{{}}"')
    # a.append(repo)


readme_contributing_graphql = '''
query {
    github: repository(owner:"{1}", name:".github") {
        defaultBranchRef {
            target {
                ... on Commit {
                    readme: history(path: "README.md", first: 1) {
                        edges {
                            node {
                                committedDate
                            }
                        }
                    },
                    contributing: history(path: "CONTRIBUTING.md", first: 1) {
                        edges {
                            node {
                                committedDate
                            }
                        }
                    }
                }
            }
        }
    },
    repository: repository(owner:"{1}", name:"{2}") {
        defaultBranchRef {
            target {
                ... on Commit {
                    readme: history(path: "README.md", first: 1) {
                        edges {
                            node {
                                committedDate
                            }
                        }
                    },
                    readme_docs: history(path: "docs/README.md", first: 1) {
                        edges {
                            node {
                                committedDate
                            }
                        }
                    }
                    contributing: history(path: "CONTRIBUTING.md", first: 1) {
                        edges {
                            node {
                                committedDate
                            }
                        }
                    },
                    contributing_docs: history(path: "docs/CONTRIBUTING.md", first: 1) {
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
'''

path_github_readme = '/data/github/defaultBranchRef/target/readme/edges'
path_github_contributing = '/data/github/defaultBranchRef/target/contributing/edges'
path_repository_readme = '/data/repository/defaultBranchRef/target/readme/edges'
path_repository_readme_docs = '/data/repository/defaultBranchRef/target/readme_docs/edges'
path_repository_contributing = '/data/repository/defaultBranchRef/target/contributing/edges'
path_repository_contributing_docs = '/data/repository/defaultBranchRef/target/contributing_docs/edges'

repository_created_at_graphql = '''
query {
    repository(owner: "{1}", name: "{2}") {
        createdAt
    }
}
'''

path_repository_created_at = '/data/repository/createdAt'


dependency_graphql = '''
query { 
    repository(owner: "{1}", name: "{2}") {
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
}
'''

path_dependency = '/data/repository/dependencyGraphManifests/edges'


def dumm(repo, text_file):
    values = get_graphql_values(repo, dependency_graphql, [path_dependency])[0]
    package_manager_dict = dict()
    if values is not None:
        for value in values:
            dependencies = value['node']['dependencies']['nodes']
            for dependency in dependencies:
                # package_name = dependency['packageName']
                if 'repository' in dependency and dependency['repository'] is not None and 'url' in dependency['repository']:
                    github_url = dependency['repository']['url']
                    package_manager = dependency['packageManager']
                    if package_manager in package_manager_dict:
                        package_manager_dict[package_manager].add(github_url)
                    else:
                        package_manager_dict[package_manager] = {github_url}
        # for package_manager in package_manager_dict:
        #     package_manager_dict[package_manager] = len(package_manager_dict[package_manager])
    print(f'"{repo}","{package_manager_dict}"')
    text_file.write(f'"{repo}","{package_manager_dict}"\n')


def get_failed_or_zero_issue_counts():
    repos = []
    file = open('C:\\Files\\repo_issue_counts - 20230827.txt', 'r', encoding='utf-8')
    for line in file.readlines():
        line = line.replace('\n', '')
        slices = line.split(',')
        if slices[1] == '0' or slices[1] == 'failed':
            repos.append(slices[0])
    file.close()
    for repo in repos:
        issue_count = get_graphql_values(repo, issue_count_graphql, [path_issue_count])[0]
        print(f'{repo},{issue_count}')


def combine_aaa():
    repo_dict = dict()
    file = open('C:\\Files\\repo_issue_counts - failed.txt', 'r', encoding='utf-8')
    for line in file.readlines():
        line = line.replace('\n', '')
        slices = line.split(',')
        repo_dict[slices[0]] = slices[1]
    file.close()
    file = open('C:\\Files\\repo_issue_counts - 20230827.txt', 'r', encoding='utf-8')
    for line in file.readlines():
        line = line.replace('\n', '')
        slices = line.split(',')
        if slices[0] in repo_dict:
            print(f'{slices[0]},{repo_dict[slices[0]]}')
        else:
            print(line)
    file.close()


pull_request_graphql = '''
query {
    repository(owner: "{1}", name: "{2}") {
        pullRequests(first: 100{AFTER}) {
            totalCount
            edges {
                node {
                    createdAt
                }
            }
            pageInfo {
                endCursor
                hasNextPage
            }
        }
    }
}
'''


commit_graphql = '''
query {
    repository(owner: "{1}", name: "{2}") {
        defaultBranchRef {
            target {
                ... on Commit {
                    history(first: 100{AFTER}) {
                        totalCount
                        edges {
                            node {
                                committedDate
                                author {
                                    email
                                }
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

user_repo_graphql = '''
query {
    organization(login: "{1}") {
        repositories(first: 100{AFTER}) {
            totalCount
            edges {
                node {
                    name
                    createdAt
                }
            }
            pageInfo {
                endCursor
                hasNextPage
            }
        }
    }
}
'''

security_md_graphql = '''
query {
    parent: repository(owner:"{1}", name:".github") {
        defaultBranchRef {
            target {
                ... on Commit {
                    root: history(path: "SECURITY.md") {
                        edges {
                            node {
                                oid
                                committedDate
                                committedViaWeb
                                author {
                                    email
                                    user {
                                        login
                                    }
                                }
                                file(path: "SECURITY.md") {
                                   object {
                                       ... on Blob {
                                           text
                                       }
                                   }
                                }
                            }
                        }
                    }
                }
            }
        }
    },
    self: repository(owner:"{1}", name:"{2}") {
        defaultBranchRef {
            target {
                ... on Commit {
                    root: history(path: "SECURITY.md") {
                        edges {
                            node {
                                oid
                                committedDate
                                committedViaWeb
                                author {
                                    email
                                    user {
                                        login
                                    }
                                }
                                file(path: "SECURITY.md") {
                                   object {
                                       ... on Blob {
                                           text
                                       }
                                   }
                                }
                            }
                        }
                    },
                    github: history(path: ".github/SECURITY.md") {
                        edges {
                            node {
                                oid
                                committedDate
                                committedViaWeb
                                author {
                                    email
                                    user {
                                        login
                                    }
                                }
                                file(path: ".github/SECURITY.md") {
                                   object {
                                       ... on Blob {
                                           text
                                       }
                                   }
                                }
                            }
                        }
                    },
                    docs: history(path: "docs/SECURITY.md") {
                        edges {
                            node {
                                oid
                                committedDate
                                author {
                                    email
                                    user {
                                        login
                                    }
                                }
                                file(path: "docs/SECURITY.md") {
                                   object {
                                       ... on Blob {
                                           text
                                       }
                                   }
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

security_md_commit_graphql = '''
query {
    repository(owner:"{1}", name:"{2}") {
        object(oid:"{3}") {
            ... on Commit {
                message
                author {
                    name
                    email
                    date
                }
            }
        }
    }
}
'''


def download(repo, directory_path, graphql, path_list, path_next_page, path_cursor, path_count):
    file_name = repo.replace('/', '_')
    file_name = f'{file_name}.txt'
    if file_name in os.listdir(directory_path):
        with open(f'{directory_path}{file_name}', encoding='utf-8') as f:
            lines = f.readlines()
            download_needed = len(lines) > 0 and lines[0] == '[]'
    else:
        download_needed = True
    if download_needed:
        slices = repo.split('/')
        owner = slices[0]
        project = slices[1]
        print(repo)
        data, cursor = get_list(
            graphql.replace('{1}', owner).replace('{2}', project),
            path_list,
            path_next_page,
            path_cursor,
            path_count
        )
        with open(f'{directory_path}{file_name}', 'w', encoding='utf-8') as f:
            f.write(f'{data}')


def user_download(user, directory_path, graphql, path_list, path_next_page, path_cursor, path_count):
    print(user)
    file_name = f'{user}.txt'
    if file_name in os.listdir(directory_path):
        with open(f'{directory_path}{file_name}', encoding='utf-8') as f:
            lines = f.readlines()
            download_needed = len(lines) > 0 and lines[0] == '[]'
    else:
        download_needed = True
    if download_needed:
        data, cursor = get_list(
            graphql.replace('{1}', user),
            path_list,
            path_next_page,
            path_cursor,
            path_count
        )
        with open(f'{directory_path}{file_name}', 'w', encoding='utf-8') as f:
            f.write(f'{data}')


def download_3(repo, directory_path):
    file_name = repo.replace('/', '_')
    file_name = f'{file_name}.txt'
    if file_name in os.listdir(directory_path):
        with open(f'{directory_path}{file_name}', encoding='utf-8') as f:
            lines = f.readlines()
            download_needed = len(lines) > 0 and lines[0] == '[]'
    else:
        download_needed = True
    if download_needed:
        slices = repo.split('/')
        owner = slices[0]
        project = slices[1]
        graphql = security_md_graphql.replace('{1}', owner).replace('{2}', project)
        data = get_result_dict(graphql, post_graphql(graphql))
        print(f'{repo} {data}')
        with open(f'{directory_path}{file_name}', 'w', encoding='utf-8') as f:
            f.write(f'{data}')


def print_paths(graphql, show_details=False):
    graphql = graphql.replace('{AFTER}', '')
    result_dict = get_result_dict(graphql, post_graphql(graphql))
    for path in result_dict:
        if show_details:
            print(f'{path} {result_dict[path]}')
        else:
            print(f'{path}')


def my_dummy(repo):
    return repo.split('/')[0].lower()


def download_pull_requests(repo):
    slices = repo.split('/')
    owner = slices[0]
    project = slices[1]
    graphql = pull_request_graphql.replace('{1}', owner).replace('{2}', project).replace('{3}', repo)
    graphql = graphql.replace('{AFTER}', '')
    result_dict = get_result_dict(graphql, post_graphql(graphql))
    print(f'"{repo}",{result_dict[path_pull_request_count]}')


if __name__ == '__main__':
    # repos(download_attributes)
    # prepare_count_dict()
    # repos(download_issues)
    # repos(dummy)
    # a = []
    # repos(get_stuff, a, "behave/behave")
    # dummy('tensorflow/tensorflow')

    # repos(get_graphql_values, repository_created_at_graphql, [path_repository_created_at])

    # text_file = open('C:\\Files\\depend_2.txt', 'w', encoding='utf-8')
    # # repos(dumm, text_file)
    #
    # for row in csv_reader('C:\\Users\\WAN Tung Lok\\Desktop\\remains.csv'):
    #     dumm(row[0], text_file)
    #
    # text_file.close()
    # dumm('iofinnet/tss-lib')
    # combine_aaa()
    # repos(download_pull_requests, 'C:\\Files\\Commits\\')

    # repos(
    #     download,
    #     'C:\\Files\\Projects\\Commits\\',
    #     commit_graphql,
    #     path_commit_list,
    #     path_commit_next_page,
    #     path_commit_cursor,
    #     path_commit_count
    # )

    # user_dict = get_user_dict()

    # username_set_1 = set()
    # directory_path = 'C:\\Files\\Projects\\User Repositories\\'
    # for file_name in os.listdir(directory_path):
    #     username = file_name.replace('.txt', '').lower()
    #     username_set_1.add(username)
    #
    # username_set_2 = set(repos(my_dummy))
    # for user in username_set_2 - username_set_1:
    # # i = 0
    # # for user in user_dict:
    #     print(user)
    #     user_download(
    #         user,
    #         'C:\\Files\\Projects\\User repositories 2\\',
    #         user_repo_graphql,
    #         path_user_repo_list,
    #         path_user_repo_next_page,
    #         path_user_repo_cursor,
    #         path_user_repo_count
    #     )

    repos(download_pull_requests)


    # print_paths(security_md_graphql.replace('{1}','tensorflow').replace('{2}','tensorflow'))

    # for repo in get_relevant_repos():
    #     download_3(repo, 'C:\\Files\\Projects\\Other Security Policies\\')

    # repo_set = set()
    # for repo, sha in get_parent_github_security_policy_commit_sha():
    #     slices = repo.split('/')
    #     owner = slices[0]
    #     project = slices[1]
    #     graphql = security_md_commit_graphql.replace('{1}', owner).replace('{2}', project).replace('{3}', sha)
    #     result_dict = get_result_dict(graphql, post_graphql(graphql))
    #     message = result_dict['/data/repository/object/message']
    #     email = result_dict['/data/repository/object/author/email']
    #     name = result_dict['/data/repository/object/author/name']
    #     date_time_string = result_dict['/data/repository/object/author/date']
    #     print((repo, email, name, date_time_string, message))
    #     # print(f'"{repo}","{email}","{name}","{date_time_string}","{message}"')

