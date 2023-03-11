import time

from utils import get_json, csv_writer, csv_reader, prepare_csv_file

if __name__ == '__main__':
    # json_array = get_json('https://api.github.com/repos/wanlok/unimelb-research-project/commits?path=SECURITY.md')
    # for json_object in json_array:
    #     commit = json_object['commit']
    #     date = commit['committer']['date']
    #     message = commit['message']
    #     print(f'{date} {message}')

    files_csv_file_path = 'files.csv'
    files_csv_writer = csv_writer(files_csv_file_path)
    files_csv_reader = csv_reader(files_csv_file_path)
    files_csv_rows = prepare_csv_file(files_csv_reader, files_csv_writer, ['repo', 'path', 'url'])

    security_md_files_csv_file_path = 'security_md_files.csv'
    security_md_files_csv_writer = csv_writer(security_md_files_csv_file_path, mode='w')
    security_md_files_csv_reader = csv_reader(security_md_files_csv_file_path)
    security_md_files_csv_rows = prepare_csv_file(security_md_files_csv_reader, security_md_files_csv_writer, ['repo', 'path', 'url'])

    for row in files_csv_rows:
        if row[1].lower() == 'security.md':
            security_md_files_csv_writer.writerow(row)

