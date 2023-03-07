from utils import csv_writer, csv_reader, prepare_csv_file, get_json, get_content, get_csv_start_index


if __name__ == '__main__':
    files_csv_file_path = 'C:\\Files\\Projects\\unimelb-research-project\\files.csv'
    files_csv_writer = csv_writer(files_csv_file_path)
    files_csv_reader = csv_reader(files_csv_file_path)
    files_csv_rows = prepare_csv_file(files_csv_reader, files_csv_writer, ['repo', 'path', 'url'])
    content_csv_file_path = 'C:\\Files\\Projects\\unimelb-research-project\\content.csv'
    content_csv_writer = csv_writer(content_csv_file_path)
    content_csv_reader = csv_reader(content_csv_file_path)
    content_csv_rows = prepare_csv_file(content_csv_reader, content_csv_writer, ['repo', 'path', 'content'])
    for i in range(get_csv_start_index(files_csv_rows, content_csv_rows, 2), len(files_csv_rows)):
        repo = files_csv_rows[i][0]
        path = files_csv_rows[i][1]
        content = get_json(f'https://api.github.com/repos/{repo}/contents/{path}')
        print(content)
        download_url = ['download_url']
        row = [repo, path, get_content(download_url)]
        if row not in content_csv_rows:
            content_csv_writer.writerow(row)
            content_csv_rows.append(row)
