import os

import requests

from repository import headers
from utils import csv_reader, csv_writer

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
                    bodyText
                    comments(first: 100) {
                        edges {
                            node {
                                createdAt
                                bodyText
                            }
                        }
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

path_committer_list = '/data/repository/defaultBranchRef/target/history/edges'
path_committer_count = '/data/repository/defaultBranchRef/target/history/totalCount'
path_committer_next_page = '/data/repository/defaultBranchRef/target/history/pageInfo/hasNextPage'
path_committer_cursor = '/data/repository/defaultBranchRef/target/history/pageInfo/endCursor'

path_issue_list = '/data/repository/issues/edges'
path_issue_count = '/data/repository/issues/totalCount'
path_issue_next_page = '/data/repository/issues/pageInfo/hasNextPage'
path_issue_cursor = '/data/repository/issues/pageInfo/endCursor'

def post_graphql(graphql):
    return requests.post('https://api.github.com/graphql', json={'query': graphql}, headers=headers).json()


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
            issues = eval(f.readlines()[0])
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
        if expected_number_of_issues <= 5000:
            cursor = ''
            while len(issue_list) < expected_number_of_issues:
                print(f'{repo} {expected_number_of_issues} {number_of_issues}')
                new_issue_list, cursor = get_list(graphql, path_issue_list, path_issue_next_page, path_issue_cursor, path_issue_count, cursor)
                for new_issue in new_issue_list:
                    exists = False
                    for issue in issue_list:
                        if new_issue['node']['createdAt'] == issue['node']['createdAt']\
                                and new_issue['node']['title'] == issue['node']['title']\
                                and new_issue['node']['bodyText'] == issue['node']['bodyText']:
                            exists = True
                            break
                    if not exists:
                        issue_list.append(new_issue)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(f'{issue_list}')
                number_of_issues = len(issue_list)


def repos(function):
    directory_path = 'C:\\Files\\a1\\'
    for file_name in os.listdir(directory_path):
        repo = file_name.replace('.csv', '').replace('_', '/', 1)
        function(repo)


def dummy(repo):
    file_name = repo.replace('/', '_')
    slices = repo.split('/')
    owner = slices[0]
    project = slices[1]
    graphql = issue_graphql.replace('{1}', owner).replace('{2}', project).replace('{AFTER}', '')
    result_dict = get_result_dict(graphql, post_graphql(graphql))
    if path_issue_count in result_dict:
        print(f'{repo},{result_dict[path_issue_count]}')
    else:
        print(f'{repo},failed')


if __name__ == '__main__':
    # repos(download_attributes)
    prepare_count_dict()
    repos(download_issues)
    # repos(dummy)