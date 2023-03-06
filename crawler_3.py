from utils import get_json, read_csv_file, csv_writer, extract

if __name__ == '__main__':
    repo_csv_file_path = 'C:\\Files\\Projects\\unimelb-research-project\\repo.csv'
    mapping_csv_file_path = 'C:\\Files\\Projects\\unimelb-research-project\\mapping.csv'
    repo_csv_writer = csv_writer(repo_csv_file_path)
    mapping_csv_writer = csv_writer(mapping_csv_file_path)
    repo_csv_rows = read_csv_file(repo_csv_file_path)
    if len(repo_csv_rows) == 0:
        repo_csv_writer.writerow(['repo'])
    mapping_csv_rows = read_csv_file(mapping_csv_file_path)
    if len(mapping_csv_rows) == 0:
        mapping_csv_writer.writerow(['repo', 'url'])
    extract(repo_csv_rows, 0)
    filename = 'security.md'
    repositories = get_json('https://api.github.com/search/repositories?q=security.md')
    if repositories is not None:
        for r_item in repositories['items']:
            repo = r_item['full_name']
            if repo not in repo_csv_rows:
                code = get_json(f'https://api.github.com/search/code?q=repo:{repo}+filename:{filename}')
                if code is not None:
                    for c_item in code['items']:
                        mapping_csv_writer.writerow([repo, c_item['html_url']])
                else:
                    break
                repo_csv_writer.writerow([repo])
