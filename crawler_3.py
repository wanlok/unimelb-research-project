import time

from utils import read_csv_file, extract, csv_reader, csv_writer, get_json


def prepare(repo_csv_reader, repo_csv_writer, mapping_csv_reader, mapping_csv_writer):
    repo_csv_rows = read_csv_file(repo_csv_reader)
    if len(repo_csv_rows) == 0:
        repo_csv_writer.writerow(['repo'])
    mapping_csv_rows = read_csv_file(mapping_csv_reader)
    if len(mapping_csv_rows) == 0:
        mapping_csv_writer.writerow(['repo', 'url'])
    extract(repo_csv_rows, 0)
    return repo_csv_rows


if __name__ == '__main__':
    repo_csv_file_path = 'C:\\Files\\Projects\\unimelb-research-project\\repo.csv'
    repo_csv_reader = csv_reader(repo_csv_file_path)
    repo_csv_writer = csv_writer(repo_csv_file_path)
    mapping_csv_file_path = 'C:\\Files\\Projects\\unimelb-research-project\\mapping.csv'
    mapping_csv_reader = csv_reader(mapping_csv_file_path)
    mapping_csv_writer = csv_writer(mapping_csv_file_path)
    q = 'security.md'
    per_page = 100
    page = 2
    file_name = 'security.md'
    time_limit = 60 + 3
    repos = prepare(repo_csv_reader, repo_csv_writer, mapping_csv_reader, mapping_csv_writer)
    while True:
        repositories = get_json(f'https://api.github.com/search/repositories?q={q}&per_page={per_page}&page={page}')
        count = 0
        if repositories is not None:
            for r_item in repositories['items']:
                repo = r_item['full_name']
                if repo not in repos:
                    code = get_json(f'https://api.github.com/search/code?q=repo:{repo}+filename:{file_name}')
                    if code is not None:
                        for c_item in code['items']:
                            mapping_csv_writer.writerow([repo, c_item['html_url']])
                        repo_csv_writer.writerow([repo])
                        repos.append(repo)
                        count = count + 1
                    else:
                        break
        print('done')
        if count > 0:
            time.sleep(time_limit)
        else:
            break
