import time

from utils import csv_writer, csv_reader, prepare_csv_file, get_json, get_csv_start_index

if __name__ == '__main__':
    files_csv_file_path = '../files.csv'
    files_csv_writer = csv_writer(files_csv_file_path)
    files_csv_reader = csv_reader(files_csv_file_path)
    files_csv_rows = prepare_csv_file(files_csv_reader, files_csv_writer, ['repo', 'path', 'url'])
    file_mapping_csv_file_path = '../file_mapping.csv'
    file_mapping_csv_writer = csv_writer(file_mapping_csv_file_path)
    file_mapping_csv_reader = csv_reader(file_mapping_csv_file_path)
    file_mapping_csv_rows = prepare_csv_file(file_mapping_csv_reader, file_mapping_csv_writer, ['repo', 'path', 'sha'])
    get_count = 0
    start_index = get_csv_start_index(files_csv_rows, file_mapping_csv_rows, 2)
    end_index = len(files_csv_rows)
    while start_index < end_index:
        if get_count == 0:
            print(f'{start_index} {end_index}')
        if get_count < 60:
            repo, path, _ = files_csv_rows[start_index]
            commits, error = get_json(f'https://api.github.com/repos/{repo}/commits?path={path}')
            get_count = get_count + 1
            if commits is not None:
                for commit in commits:
                    row = [repo, path, commit['sha']]
                    if row not in file_mapping_csv_rows:
                        file_mapping_csv_writer.writerow(row)
                        file_mapping_csv_rows.append(row)
                start_index = start_index + 1
        else:
            time.sleep(60 * 60)
            get_count = 0

    # commits, error = get_json(f'https://api.github.com/repos/{repo}/commits?path={path}')
    # i = 0
    # if commits is not None:
    #     for i in range(len(commits)):
    #         sha = commits[i]['sha']
    #         commit, error = get_json(f'https://api.github.com/repos/{repo}/commits/{sha}?path={path}')
    #         if commit is not None:
    #             for file in commit['files']:
    #                 file_name = file['filename']
    #                 contents_url = file['contents_url']
    #                 print(f'{file_name} {contents_url}')

