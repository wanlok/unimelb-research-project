import os

import requests

from repository import headers
from utils import csv_reader


def post_graphql(graphql):
    return requests.post('https://api.github.com/graphql', json={'query': graphql}, headers=headers).json()


graphql = '''
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


def get_name(graphql, start_index, end_index):
    name = graphql[start_index:end_index].strip()
    for index in range(len(name)):
        if name[index] == '(' or name[index] == ':':
            name = name[:index]
            break
    return name


def get_result_dict(graphql, data):
    result_dict = dict()
    name_set = set()
    graphql_length = len(graphql)
    if graphql_length > 0:
        depth = 0
        start_index = 1
        for index in range(graphql_length):
            if graphql[index] == '{':
                name_set.add((depth, get_name(graphql, start_index, index)))
                depth = depth + 1
                start_index = index + 1
            elif graphql[index] == '}':
                name = get_name(graphql, start_index, index)
                if len(name) > 0:
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


if __name__ == '__main__':
    language_csv_file_path = 'M:\\我的雲端硬碟\\UniMelb\\Research Project\\Attributes\\Languages.csv'
    language_csv_file_rows = get_csv_rows(language_csv_file_path)
    directory_path = 'C:\\Files\\a1\\'
    i = 0
    for file_name in os.listdir(directory_path):
        i = i + 1
        repo = file_name.replace('.csv', '').replace('_', '/', 1)
        repo = 'tensorflow/tensorflow'
        slices = repo.split('/')
        owner = slices[0]
        project = slices[1]
        if not is_exists(repo, language_csv_file_rows):
            graphql = graphql.replace('{1}', owner).replace('{2}', project).replace('{3}', repo)
            result_dict = get_result_dict(graphql, post_graphql(graphql))
            # for key in result_dict:
            #     print(f'{key} {result_dict[key]}')
            programming_languages = list(map(lambda x: x['node']['name'], result_dict[path_programming_language]))
            row = [
                result_dict[path_number_of_stars],
                result_dict[path_commit_count_2018],
                result_dict[path_commit_count_2019],
                result_dict[path_commit_count_2020],
                result_dict[path_commit_count_2021],
                result_dict[path_commit_count_2022],
                result_dict[path_issue_count_2018],
                result_dict[path_issue_count_2019],
                result_dict[path_issue_count_2020],
                result_dict[path_issue_count_2021],
                result_dict[path_issue_count_2022],
                result_dict[path_issue_closed_count_2018],
                result_dict[path_issue_closed_count_2019],
                result_dict[path_issue_closed_count_2020],
                result_dict[path_issue_closed_count_2021],
                result_dict[path_issue_closed_count_2022],
                f'{programming_languages}'
            ]
            print(row)
            break