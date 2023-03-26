import time

from utils import csv_writer, csv_reader, prepare_csv_file, get_csv_start_index, get_json, get_content

if __name__ == '__main__':
    file_mapping_csv_file_path = '../file_mapping.csv'
    file_mapping_csv_writer = csv_writer(file_mapping_csv_file_path)
    file_mapping_csv_reader = csv_reader(file_mapping_csv_file_path)
    file_mapping_csv_rows = prepare_csv_file(file_mapping_csv_reader, file_mapping_csv_writer, ['repo', 'path', 'sha'])
    file_content_mapping_csv_file_path = 'file_content_mapping.csv'
    file_content_mapping_csv_writer = csv_writer(file_content_mapping_csv_file_path)
    file_content_mapping_csv_reader = csv_reader(file_content_mapping_csv_file_path)
    file_content_mapping_csv_rows = prepare_csv_file(file_content_mapping_csv_reader, file_content_mapping_csv_writer, ['repo', 'path', 'date_time', 'content'])
    get_count = 0
    start_index = get_csv_start_index(file_mapping_csv_rows, file_content_mapping_csv_rows, 2)
    end_index = len(file_mapping_csv_rows)
    while start_index < end_index:
        if get_count == 0:
            print(f'{start_index} {end_index}')
        if get_count < 60:
            repo, path, sha = file_mapping_csv_rows[start_index]
            commit, error = get_json(f'https://api.github.com/repos/{repo}/commits/{sha}?path={path}')
            get_count = get_count + 1
            if commit is not None:
                date_time = commit['commit']['committer']['date']
                for file in commit['files']:
                    if file["filename"] == path:
                        row = [repo, path, date_time, get_content(file['raw_url'])]
                        if row not in file_content_mapping_csv_rows:
                            file_content_mapping_csv_writer.writerow(row)
                            file_content_mapping_csv_rows.append(row)
                        start_index = start_index + 1
        else:
            time.sleep(60 * 60)
            get_count = 0