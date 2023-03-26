import time

from utils import csv_reader, csv_writer, get_json, prepare_repo_mapping

if __name__ == '__main__':
    repo_csv_file_path = '../repo.csv'
    repo_csv_writer = csv_writer(repo_csv_file_path)
    repo_csv_reader = csv_reader(repo_csv_file_path)
    mapping_csv_file_path = 'mapping.csv'
    mapping_csv_writer = csv_writer(mapping_csv_file_path)
    mapping_csv_reader = csv_reader(mapping_csv_file_path)
    q = 'security.md'
    per_page = 100
    page = 2
    file_name = 'security.md'
    time_limit = 60 + 3
    repos = prepare_repo_mapping(repo_csv_reader, repo_csv_writer, mapping_csv_reader, mapping_csv_writer)
    while True:
        count = 0
        repositories = get_json(f'https://api.github.com/search/repositories?q={q}&per_page={per_page}&page={page}')
        if repositories is not None:
            for repository in repositories['items']:
                repo = repository['full_name']
                if repo not in repos:
                    codes = get_json(f'https://api.github.com/search/code?q=repo:{repo}+filename:{file_name}')
                    if codes is not None:
                        for code in codes['items']:
                            mapping_csv_writer.writerow([repo, code['html_url']])
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
